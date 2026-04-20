from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.docstore.document import Document
from typing import List

class DataLoader:
    
    def __init__(self,directory_path):
        self.directory_path = directory_path

    
    def get_documents(self)->List[Document]:
        """
        This Function Returns the Documents which is extracted from pdfs
        """

        loader = PyPDFDirectoryLoader(path=self.directory_path)

        self.docs = loader.load()

        return self.docs



        