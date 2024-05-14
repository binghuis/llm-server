from os import path

from langchain_community.document_loaders import AzureAIDocumentIntelligenceLoader

from server.core.env_vars import (
    azure_document_intelligence_api_key,
    azure_document_intelligence_endpoint,
)

cur_path = path.abspath(__file__)


cur_dir = path.dirname(cur_path)

abs_cur_path = path.join(cur_dir, "../docs/test.pdf")

# https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/concept-layout?view=doc-intel-4.0.0

loader = AzureAIDocumentIntelligenceLoader(
    api_endpoint=azure_document_intelligence_endpoint,
    api_key=azure_document_intelligence_api_key.display(),
    file_path=abs_cur_path,
    api_model="prebuilt-layout",
)

documents = loader.load()

print(documents)
