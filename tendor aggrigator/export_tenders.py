"""
Script to export all tenders from the database to JSON and Excel formats.
"""
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from export.data_exporter import get_all_tenders_from_db, export_tenders

def main():
    print("Exporting all tenders from database...")
    
    # Get all tenders from database
    tenders = get_all_tenders_from_db()
    
    if not tenders:
        print("No tenders found in database.")
        return
    
    print(f"Found {len(tenders)} tenders in database.")
    
    # Export to both JSON and Excel
    exported_files = export_tenders(tenders, formats=['json', 'excel'])
    
    print("Export completed successfully!")
    for format_name, filepath in exported_files.items():
        print(f"  {format_name.upper()}: {os.path.abspath(filepath)}")

if __name__ == "__main__":
    main()