# core/document_loader.py
# (Your reader.py code goes here, unchanged. It's already good.)
import fitz  # PyMuPDF
from pathlib import Path
import inspect
from langchain_core.documents import Document

def Error(msg="Error detected"):
    frame = inspect.currentframe().f_back
    func_name = frame.f_code.co_name
    cls_name = None
    if "self" in frame.f_locals:
        cls_name = frame.f_locals["self"].__class__.__name__
    full_name = f"{cls_name}.{func_name}" if cls_name else func_name
    raise ValueError(f"[{full_name}] {msg}")

class PDFReader:
    """Handles text extraction from regular (non-scanned) PDFs using PyMuPDF."""

    def __init__(self, filename: str):
        self.filepath = Path(filename)
        if not self.filepath.exists():
            raise FileNotFoundError(f"File not found: {filename}")
        if self.filepath.suffix.lower() != ".pdf":
            raise ValueError(f"Unsupported file type: {self.filepath.suffix}")
        
        self.doc = fitz.open(self.filepath)

    def get_page_count(self) -> int:
        """Return the total number of pages in the PDF."""
        return len(self.doc)

    def extract_text(self, page_no: int) -> str:
        """Extract text from a given page (1-indexed)."""
        if not (1 <= page_no <= len(self.doc)):
            raise ValueError(f"Invalid page number {page_no}. Must be between 1 and {len(self.doc)}.")
        
        page = self.doc.load_page(page_no - 1)  # PyMuPDF uses 0-indexed pages
        text = page.get_text("text")
        return text.strip()

class PDFLoader:
    """Wrapper around PDFReader to load LangChain Document objects."""
    def __init__(self, filename: str):
        self.filename = filename
        self.reader = PDFReader(filename)
    
    def load(self):
        """Return list of LangChain Document objects (one per page)."""
        docs = []
        num_pages = self.reader.get_page_count()
        for i in range(1, num_pages + 1):
            text = self.reader.extract_text(i)
            metadata = {"source": self.filename, "page_number": i}
            docs.append(Document(page_content=text, metadata=metadata))
        return docs

class TextLoader:
    """Generic text file loader."""
    def __init__(self, filename: str, encoding: str = "utf-8"):
        self.filename = filename
        self.encoding = encoding
    
    def load(self):
        """Return list with a single LangChain Document object."""
        with open(self.filename, "r", encoding=self.encoding) as f:
            text = f.read()
        metadata = {"source": self.filename}
        return [Document(page_content=text, metadata=metadata)]

class DocumentLoader:
    def __init__(self, filename: str):
        self.filename = filename
        self.filetype = Path(filename).suffix.lower()
        self.loaders = {
            ".pdf": PDFLoader,
            ".txt": TextLoader,
        }
    def load(self):
        if self.filetype in self.loaders:
            loader_class = self.loaders[self.filetype]
            loader = loader_class(self.filename)
            return loader.load()
        else:
            Error(f"No loader available for file type: {self.filetype}")
            # raise ValueError(f"No loader available for file type: {self.filetype}")
