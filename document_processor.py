import pandas as pd
from pathlib import Path
from typing import List, Union
import pypdf
from docx import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

    def process_pdf(self, file_path: Path) -> List[str]:
        pdf_reader = pypdf.PdfReader(file_path)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return self.text_splitter.split_text(text)

    def process_excel(self, file_path: Path) -> List[str]:
        df = pd.read_excel(file_path)
        text = df.to_string()
        return self.text_splitter.split_text(text)

    def process_docx(self, file_path: Path) -> List[str]:
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return self.text_splitter.split_text(text)

    def process_document(self, file_path: Union[str, Path]) -> List[str]:
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        file_extension = file_path.suffix.lower()
        
        if file_extension == '.pdf':
            return self.process_pdf(file_path)
        elif file_extension in ['.xlsx', '.xls']:
            return self.process_excel(file_path)
        elif file_extension in ['.docx', '.doc']:
            return self.process_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}") 