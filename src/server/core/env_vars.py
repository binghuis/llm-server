from os import getenv

from dotenv import load_dotenv
from pydantic.v1.types import SecretStr

load_dotenv()

azure_openai_endpoint = str(getenv("AZURE_OPENAI_ENDPOINT"))
azure_openai_api_key = SecretStr(str(getenv("AZURE_OPENAI_API_KEY")))
azure_openai_api_version = str(getenv("AZURE_OPENAI_API_VERSION"))
azure_openai_chat_deployment_name = str(getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"))

azure_openai_embedding_deployment_name = str(
    getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")
)

langchain_api_key = str(getenv("LANGCHAIN_API_KEY"))
