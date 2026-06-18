from pararag import ParaRAGMemory, MemoryVersion, Collection, get_console
import asyncio


MEMORY_VERSION = MemoryVersion.PROFILES

async def main():
    first_speaker = input("First speaker: ")
    second_speaker = input("Second speaker: ")
    conversation = []

    # Read conersation
    try:
        while True:
            msg = input("")
            conversation.append(msg)

    except EOFError:
        pass

    # Init and clear memory
    memory = ParaRAGMemory(memory_version=MEMORY_VERSION, users=[first_speaker, second_speaker])
    await memory.clear_collection(Collection.LOCOMO)
    await memory.delete_profiles()
    await memory.init_profile_store()

    # Ingest conversation
    current_speaker = first_speaker
    for msg in conversation:
        await memory.add_user_msg(
            user_msg=msg,
            speaker=current_speaker
        )
        # Alternate the speaker
        current_speaker = second_speaker if current_speaker == first_speaker else first_speaker
    await memory.force_profile_update()
    
    # Clear memory afterwards
    await memory.clear_collection(Collection.LOCOMO)


if __name__ == "__main__":
    asyncio.run(main())
