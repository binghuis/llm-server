import json

from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI

from server.core.env_vars import (
    azure_openai_api_key,
    azure_openai_api_version,
    azure_openai_chat_deployment_name,
    azure_openai_endpoint,
)
from server.utils.format import format_event_data

model = AzureChatOpenAI(
    azure_endpoint=azure_openai_endpoint,
    api_key=azure_openai_api_key,
    api_version=azure_openai_api_version,
    azure_deployment=azure_openai_chat_deployment_name,
    streaming=True,
)


def completion(messages: list[BaseMessage]):
    count = 0

    chunks = model.stream(messages)

    for chunk in chunks:
        if chunk.content == "":
            continue
        yield format_event_data("add", count, json.dumps(chunk.content))
        count += 1

    yield format_event_data("end", count)


# application/x-ndjson application/stream+json text/event-stream
# https://stackoverflow.com/questions/52098863/whats-the-difference-between-text-event-stream-and-application-streamjson
# https://github.com/spring-projects/spring-framework/issues/21283

if __name__ == "__main__":
    system_template = "把以下文本翻译成 {language}："
    prompt_template = ChatPromptTemplate.from_messages(
        [("system", system_template), ("user", "{text}")]
    )
    parser = StrOutputParser()
    chain = prompt_template | model | parser
    print(chain.invoke({"language": "chinese", "text": "hi"}))
    # messages = [
    #     HumanMessage(content="你好"),
    #     SystemMessage(content="我是一个聊天机器人，我可以回答你的问题"),
    # ]
    # for chunk in completion(messages):
    #     print(chunk)
