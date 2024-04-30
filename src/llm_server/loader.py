from os import path

from langchain_community.document_loaders import TextLoader

script_path = path.abspath(__file__)

file_directory = path.dirname(script_path)

absolute_path = path.join(file_directory, "./docs/index.md")

loader = TextLoader(absolute_path)
content = loader.load()

print(content)

if __name__ == "__main__":
    pass
