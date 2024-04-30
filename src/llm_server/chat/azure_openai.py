import os

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import AzureChatOpenAI
from pydantic.v1.types import SecretStr

load_dotenv()
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = SecretStr(str(os.getenv("AZURE_OPENAI_KEY")))
api_version = str(os.getenv("AZURE_OPENAI_API_VERSION"))
azure_deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")


def completion(messages: list[BaseMessage]):
    chat = AzureChatOpenAI(
        azure_endpoint=azure_endpoint,
        api_key=api_key,
        api_version=api_version,
        azure_deployment=azure_deployment,
        streaming=True,
    )
    count = 0

    chunks = chat.stream(messages)

    for chunk in chunks:
        if chunk.content == "":
            continue
        yield f"event: message\ndata: {chunk.content}\nid: {count}\n\n"
        count += 1

    yield f"event: end\nid: {count}\n\n"


messages = [
    HumanMessage(content="你好"),
    SystemMessage(content="我是一个聊天机器人，我可以回答你的问题"),
]

for chunk in completion(messages):
    print(chunk)


# application/x-ndjson application/stream+json text/event-stream
# https://github.com/spring-projects/spring-framework/issues/21283
# https://stackoverflow.com/questions/52098863/whats-the-difference-between-text-event-stream-and-application-streamjson
