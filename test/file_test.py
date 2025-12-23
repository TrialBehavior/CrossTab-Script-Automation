"""Test file for PDF extraction debugging"""
import sys
sys.path.append('C:/Users/EthanTran/OneDrive - Trial Behavior Consulting/Desktop/automating_spss')

from src.backend.file_extract.PDF_implementation import PDFHandler1

def main():
    # Path to test PDF
    pdf_path = r"C:\Users\EthanTran\OneDrive - Trial Behavior Consulting\Desktop\automating_spss\pdf_testing\Q4\Wine\Q4_Wine Warehouse adv. GSC_MP.pdf"
    
    # Create PDF handler
    pdf_handler = PDFHandler1()
    
    # Extract highlighted statements
    print("Extracting highlighted statements...")
    print("=" * 80)
    
    statements = pdf_handler.extract_highlighted_statements(pdf_path)
    
    print(f"\nTotal statements extracted: {len(statements)}\n")
    
    # Print each statement
    for i, statement in enumerate(statements, 1):
        print(f"Statement {i}:")
        print(f"  {statement}")
        print()

if __name__ == "__main__":
    main()