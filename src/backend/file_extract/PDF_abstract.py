from abc import ABC, abstractmethod

class PDFProcessor(ABC):
    """Abstract base class for PDF processing"""
    
    @abstractmethod
    def find_pages_with_text(self, pdf_path, search_text: str) -> list[int]:
        """Find pages containing specific text"""
        pass
    
    @abstractmethod
    def extract_highlighted_statements(self, pdf_path) -> list[str]:
        """Extract highlighted text from PDF"""
        pass
    
    @abstractmethod
    def split_pdf_by_pages(self, pdf_file, page_numbers: list[int], output_path=None) -> str | bytes:
        """Split PDF into specific pages"""
        pass
    # @abstractmethod
    # def docx_to_pdf(self, doc_file) -> bytes:
    #     """Convert DOCX file to PDF bytes"""
    #     pass


