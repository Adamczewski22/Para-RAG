from langchain_core.messages import SystemMessage
from langgraph.runtime import Runtime
from pydantic import BaseModel, Field

from pararag.ai.llm import get_llm
from pararag.shared.models import Profile
from pararag.shared.console import get_console
from pararag.orchestration.deduplication.update.nodes import DeduplicationState
from pararag.orchestration.shared.types import ProfileUpdateContext
from pararag.orchestration.shared.prompts import UPDATE_PROFILE_PROMPT
from pararag.orchestration.shared.utils import assertions_to_string

class ProfilesUpdate(BaseModel):
    profile_updates: list[Profile] = Field(description="New versions of profiles that should be updated or created")

class ProfileState(DeduplicationState):
    users: list[str]
    profiles: list[Profile]

class InvalidUser(Exception):
    pass


async def update_profiles(state: ProfileState, runtime: Runtime[ProfileUpdateContext]) -> dict:
    # In case of no new assertions there is no need to update profiles
    if len(state["deduplicated_assertions"]) == 0:
        return {}

    profile_service = runtime.context["profile_service"]
    json_logger = runtime.context["json_logger"]

    # Get current profiles
    profiles = await profile_service.get_profiles()

    llm = get_llm().with_structured_output(ProfilesUpdate)

    # Serialize profiles for the prompt
    profile_dumps = [profile.model_dump_json() for profile in profiles]
    profiles_str = "\n".join(profile_dumps)

    # Prompt
    prompt = UPDATE_PROFILE_PROMPT.format(
        assertions=assertions_to_string(state["deduplicated_assertions"]),
        profiles=profiles_str,
    )

    # Report and ignore exceptions like structured output or invalid user failures
    try:
        # Update profiles
        response = await llm.ainvoke([SystemMessage(prompt)])
        profile_updates: list[Profile] = response.profile_updates
        profiles_by_name: dict[str, Profile] = {profile.name: profile for profile in profiles}

        for new_profile in profile_updates:
            # Check if user name is valid
            if new_profile.name not in state["users"]:
                raise InvalidUser(f"Invalid user: {new_profile.name}")
            
            # Use profile service to update the persistent state
            await profile_service.update_profile(
                new_profile=new_profile.profile,
                user=new_profile.name,
            )

            # Log
            if state["msg_id"]:
                json_logger.log_profile_update(
                    msg_id=state["msg_id"],
                    user=new_profile.name,
                    previous_profile=profiles_by_name[new_profile.name].profile,
                    new_profile=new_profile.profile,
                    assertions=state["deduplicated_assertions"],
                )
            get_console().print_profile_update(
                user=new_profile.name,
                previous_profile=profiles_by_name[new_profile.name].profile,
                new_profile=new_profile.profile,
            )

            profiles_by_name[new_profile.name] = new_profile
    
    except Exception as exc:
        get_console().print_exception(exc)
        return {}
    
    return {"profiles": list[profiles_by_name.values()]}
