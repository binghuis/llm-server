from langchain_openai import AzureOpenAIEmbeddings

from server.core.env_vars import (
    azure_openai_api_key,
    azure_openai_api_version,
    azure_openai_embedding_deployment_name,
    azure_openai_endpoint,
)

llm = AzureOpenAIEmbeddings(
    azure_endpoint=azure_openai_endpoint,
    api_key=azure_openai_api_key,
    api_version=azure_openai_api_version,
    azure_deployment=azure_openai_embedding_deployment_name,
)
