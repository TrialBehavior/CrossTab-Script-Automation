"""
End-to-end test for default Plaintiff vs Defense workflow

Tests the complete workflow:
1. Extract PDF with party names
2. Verify correct page detection
3. Verify correct number of statements extracted
4. Generate SPSS syntax and verify output
"""
import pytest
import sys
import io
from pathlib import Path

# Add project root to path
sys.path.append('C:/Users/EthanTran/OneDrive - Trial Behavior Consulting/Desktop/automating_spss')

from src.backend.file_extract.PDF_implementation import PDFHandler1
from src.backend.sav.sav_handler import SavHandler
import pyreadstat


class TestDefaultWorkflow:
    """Test the default Plaintiff vs Defense workflow"""
    
    @pytest.fixture
    def pdf_path(self):
        """Path to test PDF"""
        return Path(r"C:\Users\EthanTran\OneDrive - Trial Behavior Consulting\Desktop\automating_spss\pdf_testing\Q4\PDF_Normal\Posted Q4_OPERS v. Freddie Mac (Correls) (004).pdf")
    
    @pytest.fixture
    def sav_path(self):
        """Path to test SAV file"""
        return Path(r"C:\Users\EthanTran\OneDrive - Trial Behavior Consulting\Desktop\automating_spss\pdf_testing\Q4\PDF_Normal\Untitled2.sav")
    
    @pytest.fixture
    def pdf_handler(self):
        """Create PDF handler instance"""
        return PDFHandler1()
    
    @pytest.fixture
    def party_names(self):
        """Default party names"""
        return {
            'name1': 'Plaintiff',
            'name2': 'Defense'
        }
    
    def test_find_party_pages(self, pdf_handler, pdf_path, party_names):
        """Test that Defense and Plaintiff pages are found correctly"""
        assert pdf_path.exists(), f"Test PDF not found: {pdf_path}"
        
        # Find Defense Arguments pages
        defense_pages = pdf_handler.find_pages_with_text(
            str(pdf_path), 
            f"{party_names['name2']} Arguments"
        )
        
        # Find Plaintiff Arguments pages
        plaintiff_pages = pdf_handler.find_pages_with_text(
            str(pdf_path), 
            f"{party_names['name1']} Arguments"
        )
        
        # Convert to 1-indexed for display
        defense_pages_1indexed = [p + 1 for p in defense_pages]
        plaintiff_pages_1indexed = [p + 1 for p in plaintiff_pages]
        
        print(f"\nDefense Arguments found on pages: {defense_pages_1indexed}")
        print(f"Plaintiff Arguments found on pages: {plaintiff_pages_1indexed}")
        
        # Assertions based on your screenshot
        assert defense_pages_1indexed == [8, 9, 10, 11], \
            f"Expected Defense pages [8, 9, 10, 11], got {defense_pages_1indexed}"
        
        assert plaintiff_pages_1indexed == [4, 5, 6, 7], \
            f"Expected Plaintiff pages [4, 5, 6, 7], got {plaintiff_pages_1indexed}"
    
    def test_extract_statements(self, pdf_handler, pdf_path, party_names):
        """Test that exactly 20 statements are extracted total"""
        assert pdf_path.exists(), f"Test PDF not found: {pdf_path}"
        
        # Find pages
        defense_pages = pdf_handler.find_pages_with_text(
            str(pdf_path), 
            f"{party_names['name2']} Arguments"
        )
        plaintiff_pages = pdf_handler.find_pages_with_text(
            str(pdf_path), 
            f"{party_names['name1']} Arguments"
        )
        
        # Extract Defense statements
        defense_pdf_bytes = pdf_handler.split_pdf_by_pages(str(pdf_path), defense_pages)
        defense_highlights = pdf_handler.extract_highlighted_statements(
            io.BytesIO(defense_pdf_bytes)
        )
        
        # Extract Plaintiff statements
        plaintiff_pdf_bytes = pdf_handler.split_pdf_by_pages(str(pdf_path), plaintiff_pages)
        plaintiff_highlights = pdf_handler.extract_highlighted_statements(
            io.BytesIO(plaintiff_pdf_bytes)
        )
        
        print(f"\nDefense statements extracted: {len(defense_highlights)}")
        print(f"Plaintiff statements extracted: {len(plaintiff_highlights)}")
        print(f"Total statements: {len(defense_highlights) + len(plaintiff_highlights)}")
        
        # Print statements for verification
        print("\n=== DEFENSE STATEMENTS ===")
        for i, stmt in enumerate(defense_highlights, 1):
            print(f"{i}. {stmt}")
        
        print("\n=== PLAINTIFF STATEMENTS ===")
        for i, stmt in enumerate(plaintiff_highlights, 1):
            print(f"{i}. {stmt}")
        
        # Assert total is 20
        total_statements = len(defense_highlights) + len(plaintiff_highlights)
        assert total_statements == 20, \
            f"Expected 20 total statements, got {total_statements}"
        
        return plaintiff_highlights, defense_highlights
    
    def test_generate_spss_syntax(self, pdf_handler, pdf_path, sav_path, party_names):
        """Test that SPSS syntax generation produces the expected output"""
        assert pdf_path.exists(), f"Test PDF not found: {pdf_path}"
        assert sav_path.exists(), f"Test SAV file not found: {sav_path}"
        
        # Extract statements (same as previous test)
        defense_pages = pdf_handler.find_pages_with_text(
            str(pdf_path), 
            f"{party_names['name2']} Arguments"
        )
        plaintiff_pages = pdf_handler.find_pages_with_text(
            str(pdf_path), 
            f"{party_names['name1']} Arguments"
        )
        
        defense_pdf_bytes = pdf_handler.split_pdf_by_pages(str(pdf_path), defense_pages)
        defense_highlights = pdf_handler.extract_highlighted_statements(
            io.BytesIO(defense_pdf_bytes)
        )
        
        plaintiff_pdf_bytes = pdf_handler.split_pdf_by_pages(str(pdf_path), plaintiff_pages)
        plaintiff_highlights = pdf_handler.extract_highlighted_statements(
            io.BytesIO(plaintiff_pdf_bytes)
        )
        
        # Read SAV file
        df, meta = pyreadstat.read_sav(str(sav_path))
        
        # Create recode settings (default values as in pdf_extractor.py)
        recode_settings = {}
        
        # Plaintiff settings
        for statement in plaintiff_highlights:
            recode_settings[statement] = {
                'range1_start': 1,
                'range1_end': 2,
                'range1_becomes': 1,
                'range2_start': 3,
                'range2_end': 4,
                'range2_becomes': 2
            }
        
        # Defense settings
        for statement in defense_highlights:
            recode_settings[statement] = {
                'range1_start': 1,
                'range1_end': 2,
                'range1_becomes': 2,
                'range2_start': 3,
                'range2_end': 4,
                'range2_becomes': 1
            }
        
        # Generate SPSS syntax
        sav_handler = SavHandler(
            list(meta.column_names_to_labels.items()),
            party_names['name1'],
            party_names['name2']
        )
        
        result = sav_handler.generate_recode_script(
            name1_questions=plaintiff_highlights,
            name2_questions=defense_highlights,
            recode_settings=recode_settings
        )
        
        print("\n=== GENERATED SPSS SYNTAX ===")
        print(result.script)
        
        print(f"\n=== MATCHING STATISTICS ===")
        print(f"Matched: {len(result.matched)} statements")
        print(f"Unmatched: {len(result.unmatched)} statements")
        
        if result.unmatched:
            print("\n=== UNMATCHED STATEMENTS ===")
            for side, stmt in result.unmatched:
                print(f"[{side}] {stmt}")
        
        # Verify the syntax matches expected output
        # Check for key patterns in the generated syntax
        assert "recode Plaaffs_" in result.script, "Should contain Plaintiff recode statements"
        assert "recode Defaffs_" in result.script, "Should contain Defense recode statements"
        assert "(1 thru 2=1) (3 thru 4=2)" in result.script, "Should contain Plaintiff recode pattern"
        assert "(1 thru 2=2) (3 thru 4=1)" in result.script, "Should contain Defense recode pattern"
        assert "variable labels" in result.script, "Should contain variable labels"
        assert "value labels" in result.script, "Should contain value labels"
        assert "'Plaintiff'" in result.script, "Should contain Plaintiff label"
        assert "'Defense'" in result.script, "Should contain Defense label"
        assert "execute." in result.script, "Should contain execute statements"
        
        # Verify all 20 statements were matched (no unmatched)
        assert len(result.unmatched) == 0, \
            f"Expected 0 unmatched statements, got {len(result.unmatched)}"
        
        assert len(result.matched) == 20, \
            f"Expected 20 matched statements, got {len(result.matched)}"
        
        return result

class TestWineWarehouseWorkflow:
    """Test the Wine Warehouse vs Golden State Cider workflow"""
    
    @pytest.fixture
    def pdf_path(self):
        """Path to Wine Warehouse test PDF"""
        return Path(r"C:\Users\EthanTran\OneDrive - Trial Behavior Consulting\Desktop\automating_spss\pdf_testing\Q4\Wine\Q4_Wine Warehouse adv. GSC_MP.pdf")
    
    @pytest.fixture
    def sav_path(self):
        """Path to Wine SAV file"""
        return Path(r"C:\Users\EthanTran\OneDrive - Trial Behavior Consulting\Desktop\automating_spss\pdf_testing\Q4\Wine\wine.sav")
    
    @pytest.fixture
    def pdf_handler(self):
        """Create PDF handler instance"""
        return PDFHandler1()
    
    @pytest.fixture
    def party_names(self):
        """Custom party names for Wine case"""
        return {
            'name1': 'Wine Warehouse',
            'name2': 'Golden State Cider'
        }
    
    @pytest.fixture
    def expected_statements(self):
        """Expected statements for each party"""
        return {
            'Wine Warehouse': [
                "Temporary out-of-stocks are standard, common events that happen all the time in this industry; they are not breaches of the contract.",
                "Wine Warehouse delivered to 97% of California’s population, which means that it covers the state adequately and reasonably.",
                "The fact that Wine Warehouse outperformed Golden State Cider’s new distributor for a time proves that Wine Warehouse was performing well."
            ],
            'Golden State Cider': [
                "Golden State Cider lost sales from Wine Warehouse’s failure to service existing accounts."
            ]
        }
    
    def test_find_party_pages(self, pdf_handler, pdf_path, party_names):
        """Test that Wine Warehouse and Golden State Cider pages are found correctly"""
        assert pdf_path.exists(), f"Test PDF not found: {pdf_path}"
        
        # Find Wine Warehouse Arguments pages
        wine_pages = pdf_handler.find_pages_with_text(
            str(pdf_path), 
            f"{party_names['name1']} Arguments"
        )
        
        # Find Golden State Cider Arguments pages
        cider_pages = pdf_handler.find_pages_with_text(
            str(pdf_path), 
            f"{party_names['name2']} Arguments"
        )
        
        # Convert to 1-indexed for display
        wine_pages_1indexed = [p + 1 for p in wine_pages]
        cider_pages_1indexed = [p + 1 for p in cider_pages]
        
        print(f"\nWine Warehouse Arguments found on pages: {wine_pages_1indexed}")
        print(f"Golden State Cider Arguments found on pages: {cider_pages_1indexed}")
        
        # Assertions based on your specifications
        assert wine_pages_1indexed == [6, 7, 8], \
            f"Expected Wine Warehouse pages [6, 7, 8], got {wine_pages_1indexed}"
        
        assert cider_pages_1indexed == [9, 10, 11], \
            f"Expected Golden State Cider pages [9, 10, 11], got {cider_pages_1indexed}"
    
    def test_extract_statements(self, pdf_handler, pdf_path, party_names, expected_statements):
        """Test that correct statements are extracted for each party"""
        assert pdf_path.exists(), f"Test PDF not found: {pdf_path}"
        
        # Find pages
        wine_pages = pdf_handler.find_pages_with_text(
            str(pdf_path), 
            f"{party_names['name1']} Arguments"
        )
        cider_pages = pdf_handler.find_pages_with_text(
            str(pdf_path), 
            f"{party_names['name2']} Arguments"
        )
        
        # Extract Wine Warehouse statements
        wine_pdf_bytes = pdf_handler.split_pdf_by_pages(str(pdf_path), wine_pages)
        wine_highlights = pdf_handler.extract_highlighted_statements(
            io.BytesIO(wine_pdf_bytes)
        )
        
        # Extract Golden State Cider statements
        cider_pdf_bytes = pdf_handler.split_pdf_by_pages(str(pdf_path), cider_pages)
        cider_highlights = pdf_handler.extract_highlighted_statements(
            io.BytesIO(cider_pdf_bytes)
        )
        
        print(f"\nWine Warehouse statements extracted: {len(wine_highlights)}")
        print(f"Golden State Cider statements extracted: {len(cider_highlights)}")
        print(f"Total statements: {len(wine_highlights) + len(cider_highlights)}")
        
        # Print statements for verification
        print("\n=== WINE WAREHOUSE STATEMENTS ===")
        for i, stmt in enumerate(wine_highlights, 1):
            print(f"{i}. {stmt}")
        
        print("\n=== GOLDEN STATE CIDER STATEMENTS ===")
        for i, stmt in enumerate(cider_highlights, 1):
            print(f"{i}. {stmt}")
        
        # Assert counts
        assert len(wine_highlights) == 3, \
            f"Expected 3 Wine Warehouse statements, got {len(wine_highlights)}"
        
        assert len(cider_highlights) == 1, \
            f"Expected 1 Golden State Cider statement, got {len(cider_highlights)}"
        
        # Assert total is 4
        total_statements = len(wine_highlights) + len(cider_highlights)
        assert total_statements == 4, \
            f"Expected 4 total statements, got {total_statements}"
        
        # Verify exact statement matches
        print("\n=== VERIFYING EXACT STATEMENT MATCHES ===")
        for i, expected_stmt in enumerate(expected_statements['Wine Warehouse'], 1):
            print(f"\nChecking Wine Warehouse statement {i}:")
            print(f"  Expected: {expected_stmt}")
            assert expected_stmt in wine_highlights, \
                f"Expected Wine Warehouse statement not found: {expected_stmt}"
            print(f"  ✓ Found!")
        
        for i, expected_stmt in enumerate(expected_statements['Golden State Cider'], 1):
            print(f"\nChecking Golden State Cider statement {i}:")
            print(f"  Expected: {expected_stmt}")
            assert expected_stmt in cider_highlights, \
                f"Expected Golden State Cider statement not found: {expected_stmt}"
            print(f"  ✓ Found!")
        
        return wine_highlights, cider_highlights
    
    def test_statements_exist_in_sav(self, pdf_handler, pdf_path, sav_path, party_names):
        """Test that all 4 extracted statements exist in the SAV file"""
        assert pdf_path.exists(), f"Test PDF not found: {pdf_path}"
        assert sav_path.exists(), f"Test SAV file not found: {sav_path}"
        
        # Extract statements
        wine_pages = pdf_handler.find_pages_with_text(
            str(pdf_path), 
            f"{party_names['name1']} Arguments"
        )
        cider_pages = pdf_handler.find_pages_with_text(
            str(pdf_path), 
            f"{party_names['name2']} Arguments"
        )
        
        wine_pdf_bytes = pdf_handler.split_pdf_by_pages(str(pdf_path), wine_pages)
        wine_highlights = pdf_handler.extract_highlighted_statements(
            io.BytesIO(wine_pdf_bytes)
        )
        
        cider_pdf_bytes = pdf_handler.split_pdf_by_pages(str(pdf_path), cider_pages)
        cider_highlights = pdf_handler.extract_highlighted_statements(
            io.BytesIO(cider_pdf_bytes)
        )
        
        # Read SAV file
        df, meta = pyreadstat.read_sav(str(sav_path))
        
        print("\n=== SAV FILE VARIABLE LABELS ===")
        sav_labels = list(meta.column_names_to_labels.values())
        for col_name, label in meta.column_names_to_labels.items():
            print(f"{col_name}: {label}")
        
        # Check if each extracted statement exists in SAV labels
        print("\n=== CHECKING WINE WAREHOUSE STATEMENTS IN SAV ===")
        for i, statement in enumerate(wine_highlights, 1):
            found = statement in sav_labels
            status = "✓" if found else "✗"
            print(f"{status} Statement {i}: {statement[:80]}...")
            assert found, f"Wine Warehouse statement not found in SAV: {statement}"
        
        print("\n=== CHECKING GOLDEN STATE CIDER STATEMENTS IN SAV ===")
        for i, statement in enumerate(cider_highlights, 1):
            found = statement in sav_labels
            status = "✓" if found else "✗"
            print(f"{status} Statement {i}: {statement[:80]}...")
            assert found, f"Golden State Cider statement not found in SAV: {statement}"
        
        print("\n✓ All 4 extracted statements exist in the SAV file!")
        
if __name__ == "__main__":
    # Run with: pytest test_default_workflow.py -v -s
    pytest.main([__file__, "-v", "-s"])