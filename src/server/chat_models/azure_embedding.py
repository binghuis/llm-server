from os import getenv

from dotenv import load_dotenv
from langchain_openai import AzureOpenAIEmbeddings
from pydantic.v1.types import SecretStr

load_dotenv()
azure_endpoint = getenv("AZURE_OPENAI_ENDPOINT")
api_key = SecretStr(str(getenv("AZURE_OPENAI_KEY")))
api_version = str(getenv("AZURE_OPENAI_API_VERSION"))
azure_deployment = getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")

llm = AzureOpenAIEmbeddings(
    azure_endpoint=azure_endpoint,
    api_key=api_key,
    api_version=api_version,
    azure_deployment=azure_deployment,
)
