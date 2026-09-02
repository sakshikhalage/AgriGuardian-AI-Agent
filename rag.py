import os

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


KNOWLEDGE_FOLDER = "knowledge"


def load_documents():
    documents = []

    if not os.path.exists(KNOWLEDGE_FOLDER):
        print("Knowledge folder not found.")
        return documents

    for filename in os.listdir(KNOWLEDGE_FOLDER):

        if filename.lower().endswith(".pdf"):

            file_path = os.path.join(KNOWLEDGE_FOLDER, filename)

            print(f"Loading: {filename}")

            loader = PyMuPDFLoader(file_path)
            documents.extend(loader.load())

    return documents


def split_documents(documents):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_documents(documents)

    return chunks


if __name__ == "__main__":

    documents = load_documents()

    print(f"Documents loaded: {len(documents)}")

    chunks = split_documents(documents)

    print(f"Text chunks created: {len(chunks)}")