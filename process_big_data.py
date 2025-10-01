"""
Script to process large amounts of tender data efficiently.
"""
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from big_data.data_processor import process_large_dataset

def main():
    print("Starting big data processing for Tender Aggregator...")
    
    try:
        json_path, excel_path = process_large_dataset()
        print("\nBig data processing completed successfully!")
        print(f"JSON export: {json_path}")
        print(f"Excel export: {excel_path}")
    except Exception as e:
        print(f"Error processing big data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()