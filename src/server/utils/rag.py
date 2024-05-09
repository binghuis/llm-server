from os import getenv

import bs4
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
bs4_strainer = bs4.SoupStrainer(class_=("post-title", "post-header", "post-content"))
loader = WebBaseLoader(
    web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
    bs_kwargs={"parse_only": bs4_strainer},
)
docs = loader.load()

print(len(docs[0].page_content))

print(docs[0].page_content[:500])

# 2. Indexing: Split
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=200, add_start_index=True
)
all_splits = text_splitter.split_documents(docs)

print(len(all_splits), len(all_splits[0].page_content))
print(all_splits[10].metadata)


# 3. Indexing: Store
vectorstore = Chroma.from_documents(documents=all_splits, embedding=azure_embedding.llm)

# 4. Retrieval and Generation: Retrieve
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 6})
retrieved_docs = retriever.invoke("What are the approaches to Task Decomposition?")
print(len(retrieved_docs))
print(retrieved_docs[0].page_content)

# 5. Retrieval and Generation: Generate
prompt = hub.pull("rlm/rag-prompt")
example_messages = prompt.invoke(
    {"context": "filler context", "question": "filler question"}
).to_messages()
example_messages
print(example_messages[0].content)


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | azure_openai.llm
    | StrOutputParser()
)

for chunk in rag_chain.stream("What is Task Decomposition?"):
    print(chunk, end="", flush=True)

if __name__ == "__main__":
    pass
