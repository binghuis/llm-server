import json
from os import getenv

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import AzureChatOpenAI
from pydantic.v1.types import SecretStr
from server.utils.format import format_event_data

load_dotenv()

azure_endpoint = getenv("AZURE_OPENAI_ENDPOINT")
api_key = SecretStr(str(getenv("AZURE_OPENAI_KEY")))
api_version = str(getenv("AZURE_OPENAI_API_VERSION"))
azure_deployment = getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")

chat = AzureChatOpenAI(
    azure_endpoint=azure_endpoint,
    api_key=api_key,
    api_version=api_version,
    azure_deployment=azure_deployment,
    streaming=True,
)


def completion(messages: list[BaseMessage]):
    count = 0

    chunks = chat.stream(messages)

    for chunk in chunks:
        if chunk.content == "":
            continue
        yield format_event_data("add", count, json.dumps(chunk.content))
        count += 1

    yield format_event_data("end", count)


if __name__ == "__main__":
    messages = [
        HumanMessage(content="你好"),
        SystemMessage(content="我是一个聊天机器人，我可以回答你的问题"),
    ]

    for chunk in completion(messages):
        print(chunk)

# application/x-ndjson application/stream+json text/event-stream
# https://stackoverflow.com/questions/52098863/whats-the-difference-between-text-event-stream-and-application-streamjson
# https://github.com/spring-projects/spring-framework/issues/21283
