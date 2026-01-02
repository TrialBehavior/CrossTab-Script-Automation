import pdfplumber
import re
import fitz  # PyMuPDF for handling highlights
import io
from abc import ABC, abstractmethod
from .PDF_abstract import PDFProcessor
import tempfile
import os
import docx2pdf
import pythoncom
class PDFHandler1(PDFProcessor):
    """Handles PDF processing operations"""
    
    def find_pages_with_text(self, pdf_path, search_text: str) -> list[int]:
        """
        Find pages containing specific text.
        
        Args:
            pdf_path: Path to PDF or file-like object
            search_text: Text to search for
            
        Returns:
            List of page numbers (0-indexed) containing the text
        """
        matching_pages = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                
                if text and search_text.lower() in text.lower():
                    matching_pages.append(i)
        
        return matching_pages
    
    def extract_highlighted_statements(self, pdf_path) -> list[str]:
        """
        Extract highlighted text from PDF.
        
        Args:
            pdf_path: Path to PDF, BytesIO, or file-like object
            
        Returns:
            List of highlighted statements
        """
        # Handle different input types
        if isinstance(pdf_path, io.BytesIO):
            doc = fitz.open(stream=pdf_path.read(), filetype="pdf")
        elif hasattr(pdf_path, 'read'):  # File-like object (like Streamlit upload)
            doc = fitz.open(stream=pdf_path.read(), filetype="pdf")
        else:  # String path
            doc = fitz.open(pdf_path)
        
        all_highlights = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text_dict = page.get_text("dict")
            drawings = page.get_drawings()
            
            # Find yellow rectangles
            yellow_rects = self._find_yellow_rectangles(drawings)
            
            # Get highlighted text spans
            highlighted_spans = self._extract_highlighted_spans(
                text_dict, yellow_rects, page_num
            )
            
            # Merge spans on same line
            merged_highlights = self._merge_spans_on_line(highlighted_spans)
            
            all_highlights.extend(merged_highlights)
        
        doc.close()
        
        # Remove duplicates and clean text
        unique_highlights = self._remove_duplicates(all_highlights)
        statements = self._clean_and_split_statements(unique_highlights)
        
        return statements
    
    def split_pdf_by_pages(
        self, 
        pdf_file, 
        page_numbers: list[int], 
        output_path=None
    ) -> str | bytes:
        """
        Extract specific pages from PDF.
        
        Args:
            pdf_file: Path to PDF or file-like object
            page_numbers: List of page numbers (0-indexed) to extract
            output_path: Optional path to save the output PDF
            
        Returns:
            Path to saved file if output_path provided, otherwise PDF bytes
        """
        # Open source PDF
        if hasattr(pdf_file, 'read'):
            source_doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        else:
            source_doc = fitz.open(pdf_file)
        
        # Create new PDF with only selected pages
        new_doc = fitz.open()
        
        for page_num in sorted(page_numbers):
            if 0 <= page_num < len(source_doc):
                new_doc.insert_pdf(source_doc, from_page=page_num, to_page=page_num)
        
        # Save or return bytes
        if output_path:
            new_doc.save(output_path)
            new_doc.close()
            source_doc.close()
            return output_path
        else:
            pdf_bytes = new_doc.write()
            new_doc.close()
            source_doc.close()
            return pdf_bytes
    
    # Private helper methods
    
    def _find_yellow_rectangles(self, drawings) -> list:
        """Find yellow highlight rectangles in drawings"""
        yellow_rects = []
        for drawing in drawings:
            if drawing["fill"]:
                r, g, b = drawing["fill"]
                if r > 0.8 and g > 0.8 and b < 0.5:
                    yellow_rects.append(drawing["rect"])
        return yellow_rects
    
    def _extract_highlighted_spans(self, text_dict, yellow_rects, page_num) -> list:
        """Extract text spans that intersect with yellow rectangles"""
        highlighted_spans = []
        
        for block in text_dict["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if text:
                            span_rect = fitz.Rect(span["bbox"])
                            for yellow_rect in yellow_rects:
                                if span_rect.intersects(yellow_rect):
                                    if not self._is_numeric_span(text):
                                        print(f"Found span: '{text}' at y_pos: {span['bbox'][1]}")  
                                        highlighted_spans.append({
                                            'page': page_num + 1,
                                            'text': text,
                                            'bbox': span["bbox"],
                                            'y_pos': span["bbox"][1]
                                        })
                                    break
        
        return highlighted_spans
    
    def _merge_spans_on_line(self, highlighted_spans, y_threshold=2) -> list:
        """Merge spans that are on the same line"""
        # Sort by y position and x position
        highlighted_spans.sort(key=lambda x: (x['y_pos'], x['bbox'][0]))
        
        merged_highlights = []
        current_line = None
        
        for span in highlighted_spans:
            if current_line is None:
                current_line = {
                    'page': span['page'],
                    'text': span['text'],
                    'y_pos': span['y_pos']
                }
            elif abs(span['y_pos'] - current_line['y_pos']) < y_threshold:
                current_line['text'] += ' ' + span['text']
            else:
                merged_highlights.append(current_line)
                current_line = {
                    'page': span['page'],
                    'text': span['text'],
                    'y_pos': span['y_pos']
                }
        
        if current_line:
            merged_highlights.append(current_line)
        
        return merged_highlights
    
    def _remove_duplicates(self, highlights) -> list:
        """Remove duplicate highlights"""
        seen = set()
        unique_highlights = []
        
        for h in highlights:
            key = (h['page'], h['text'])
            if key not in seen:
                seen.add(key)
                unique_highlights.append(h)
        
        return unique_highlights
    def docx_to_pdf(self, docx_file) -> bytes:
        """
        Convert DOCX file to PDF.
        
        Args:
            docx_file: File-like object or path to DOCX file
            
        Returns:
            PDF as bytes
        """
        import pythoncom
        
        # Initialize COM for this thread
        pythoncom.CoInitialize()
        
        try:
            # Save uploaded DOCX to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_docx:
                if hasattr(docx_file, 'read'):
                    tmp_docx.write(docx_file.read())
                else:
                    with open(docx_file, 'rb') as f:
                        tmp_docx.write(f.read())
                tmp_docx_path = tmp_docx.name
            
            # Convert to PDF
            tmp_pdf_path = tmp_docx_path.replace('.docx', '.pdf')
            docx2pdf.convert(tmp_docx_path, tmp_pdf_path)
            
            # Read the PDF bytes
            with open(tmp_pdf_path, 'rb') as pdf_file:
                pdf_bytes = pdf_file.read()
            
            # Clean up temp files
            os.unlink(tmp_docx_path)
            os.unlink(tmp_pdf_path)
            return pdf_bytes
        finally:
            # Always uninitialize COM
            pythoncom.CoUninitialize()
    def _clean_and_split_statements(self, highlights) -> list[str]:
        """Clean text and split into individual statements"""
        # Combine all text into one string
        combined_text = ' '.join([h['text'] for h in highlights])
        
        # Remove statistics patterns
        combined_text = re.sub(r'\d+\.\d+\s+(?:\d+\s*%\s*)+', '', combined_text)
        combined_text = re.sub(r'^\d+\s*%\s*', '', combined_text)
        
        # Split by period to get individual statements
        statements = [s.strip() + '.' for s in combined_text.split('.') if s.strip()]
        
        return statements
    def _is_numeric_span(self, text: str) -> bool:
        """Check if a span contains only numbers and whitespace"""
        text = re.sub(r'\s+\d+\s*%', '', text)
        return text.strip().replace(' ', '').isdigit()