from langchain_core.messages import SystemMessage
from langgraph.runtime import Runtime
from pydantic import BaseModel, Field
import time

from pararag.ai.llm import get_llm
from pararag.shared.models import Profile
from pararag.shared.console import get_console
from pararag.shared.logger import JsonLogger, extract_token_usage
from pararag.memory.services.profile_service import ProfileService
from pararag.orchestration.deduplication.update.nodes import DeduplicationState
from pararag.orchestration.shared.types import ProfileUpdateContext
from pararag.orchestration.shared.prompts import UPDATE_PROFILE_PROMPT_2
from pararag.orchestration.shared.utils import assertions_to_string


class ProfilesUpdate(BaseModel):
    profile_updates: list[Profile] = Field(description="New versions of profiles that should be updated or created")


class ProfileState(DeduplicationState):
    users: list[str]
    profiles: list[Profile]


class InvalidUser(Exception):
    pass


async def update_profiles_from_assertions(
    assertions: list[str],
    users: list[str],
    profile_service: ProfileService,
    json_logger: JsonLogger | None = None,
    msg_id: str | None = None,
) -> list[Profile]:
    # In case of no new assertions there is no need to update profiles
    if len(assertions) == 0:
        return []

    # Get current profiles
    profiles = await profile_service.get_profiles()

    llm = get_llm().with_structured_output(ProfilesUpdate, include_raw=True)

    # Serialize profiles for the prompt
    profile_dumps = [profile.model_dump_json() for profile in profiles]
    profiles_str = "\n".join(profile_dumps)

    # Prompt
    prompt = UPDATE_PROFILE_PROMPT_2.format(
        assertions=assertions_to_string(assertions),
        profiles=profiles_str,
    )

    # Track latency and token usage
    profile_update_start = time.perf_counter()
    profile_update_tokens = {}

    # Report and ignore exceptions like structured output or invalid user failures
    try:
        # Update profiles
        response = await llm.ainvoke([SystemMessage(prompt)])

        # Obtain token usage
        profile_update_tokens = extract_token_usage(response.get("raw"))
        if response.get("parsing_error") is not None:
            raise response["parsing_error"]

        profile_updates: list[Profile] = response["parsed"].profile_updates
        profiles_by_name: dict[str, Profile] = {profile.name: profile for profile in profiles}

        for new_profile in profile_updates:
            # Check if user name is valid
            if new_profile.name not in users:
                raise InvalidUser(f"Invalid user: {new_profile.name}")

            # Use profile service to update the persistent state
            await profile_service.update_profile(
                new_profile=new_profile.profile,
                user=new_profile.name,
            )

            # Log
            if msg_id and json_logger is not None:
                json_logger.log_profile_update(
                    msg_id=msg_id,
                    user=new_profile.name,
                    previous_profile=profiles_by_name[new_profile.name].profile,
                    new_profile=new_profile.profile,
                    assertions=assertions,
                )
            get_console().print_profile_update(
                user=new_profile.name,
                previous_profile=profiles_by_name[new_profile.name].profile,
                new_profile=new_profile.profile,
            )

            profiles_by_name[new_profile.name] = new_profile

    except Exception as exc:
        get_console().print_exception(exc)
        return []

    finally:
        if msg_id and json_logger is not None:
            json_logger.log_profile_update_latency(
                msg_id=msg_id,
                latency=time.perf_counter() - profile_update_start,
            )
            if profile_update_tokens:
                json_logger.log_profile_update_tokens(
                    msg_id=msg_id,
                    token_usage=profile_update_tokens,
                )

    return list(profiles_by_name.values())


async def update_profiles(state: ProfileState, runtime: Runtime[ProfileUpdateContext]) -> dict:
    profiles = await update_profiles_from_assertions(
        assertions=state["deduplicated_assertions"] or [],
        users=state["users"],
        profile_service=runtime.context["profile_service"],
        json_logger=runtime.context["json_logger"],
        msg_id=state["msg_id"],
    )

    if len(profiles) == 0:
        return {}

    return {"profiles": profiles}
