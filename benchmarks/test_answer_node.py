from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from dotenv import find_dotenv, load_dotenv

from prompts import ANSWER_PROMPT_4


load_dotenv(find_dotenv())

MODEL = "gpt-5.4"


def main():
    question = input("Question: ")
    memories = input("Memories:\n")
    memories = memories.encode().decode("unicode_escape")
    
    prompt = ANSWER_PROMPT_4.format(
        question=question,
        context=memories,
    )

    llm = ChatOpenAI(model=MODEL)
    response = llm.invoke([SystemMessage(prompt)])
    print(response.content)


if __name__ == "__main__":
    main()