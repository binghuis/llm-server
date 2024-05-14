from os import path

script_path = path.abspath(__file__)

print(script_path)

file_directory = path.dirname(script_path)

absolute_path = path.join(file_directory, "./docs/index.md")


# loader = AzureAIDocumentIntelligenceLoader(
#     api_endpoint=azure_openai_endpoint,
#     api_key=azure_openai_api_key.display(),
#     file_path="",
#     api_model="prebuilt-layout",
# )

# documents = loader.load()
