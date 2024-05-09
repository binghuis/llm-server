from os import getenv

from bs4 import SoupStrainer
from dotenv import load_dotenv
from langchain import hub
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter

from server.chat_models import azure_embedding, azure_openai

load_dotenv()
langchain_api_key = getenv("LANGCHAIN_API_KEY")

# 1. Indexing: Load
# 使用 bs4 从 HTML 中提取数据
bs4_strainer = SoupStrainer(class_=("devsite-page-title", "devsite-article-body"))
# 创建网络资源加载器，解析器为 lxml，parse_only 参数控制文档部分解析
loader = WebBaseLoader(
    web_paths=(
        "https://developer.chrome.com/docs/chromium/renderingng-data-structures?hl=zh-cn",
    ),
    bs_kwargs={"parse_only": bs4_strainer},
    default_parser="lxml",
)
docs = loader.load()

# 2. Indexing: Split
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=200, add_start_index=True
)
all_splits = text_splitter.split_documents(docs)

# 3. Indexing: Store
vectorstore = Chroma.from_documents(documents=all_splits, embedding=azure_embedding.llm)

# 4. Retrieval and Generation: Retrieve
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 6})

# 5. Retrieval and Generation: Generate
prompt = hub.pull("rlm/rag-prompt")
example_messages = prompt.invoke(
    {"context": "filler context", "question": "filler question"}
).to_messages()


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | azure_openai.llm
    | StrOutputParser()
)

for chunk in rag_chain.stream("帧树是什么？"):
    print(chunk, end="", flush=True)

if __name__ == "__main__":
    pass
