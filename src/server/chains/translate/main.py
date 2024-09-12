from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from server.llms.azure_openai_chat import azure_openai_chat_model

translate_system_template = "把以下文本翻译成 {language}："

translate_prompt_template = ChatPromptTemplate.from_messages(
    [("system", translate_system_template), ("user", "{text}")]
)

parser = StrOutputParser()

translate_chain = translate_prompt_template | azure_openai_chat_model | parser

if __name__ == "__main__":
    print(translate_chain.invoke({"language": "中文", "text": "Hello, how are you?"}))
