from os import path

from langchain_community.document_loaders import AzureAIDocumentIntelligenceLoader

from server.core.env_vars import azure_openai_api_key, azure_openai_endpoint

cur_path = path.abspath(__file__)


cur_dir = path.dirname(cur_path)

abs_cur_path = path.join(cur_dir, "../docs/test.pdf")


loader = AzureAIDocumentIntelligenceLoader(
    api_endpoint=azure_openai_endpoint,
    api_key=azure_openai_api_key.display(),
    file_path=abs_cur_path,
    api_model="prebuilt-layout",
)

documents = loader.load()

print(documents)
