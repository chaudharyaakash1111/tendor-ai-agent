"""
Module for exporting tender data to JSON and Excel formats.
"""
import json
import pandas as pd
from typing import List, Dict, Optional, Any
from datetime import datetime
import os

def export_to_json(tenders: List[Dict], filename: Optional[str] = None) -> str:
    """
    Export tenders to JSON format.
    
    Args:
        tenders: List of tender dictionaries
        filename: Optional filename for export (without extension)
        
    Returns:
        Path to the exported file
    """
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tenders_{timestamp}.json"
    
    # Ensure filename has .json extension
    if not filename.endswith('.json'):
        filename += '.json'
    
    # Create exports directory if it doesn't exist
    exports_dir = "exports"
    if not os.path.exists(exports_dir):
        os.makedirs(exports_dir)
    
    filepath = os.path.join(exports_dir, filename)
    
    # Write to JSON file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(tenders, f, indent=2, default=str)
    
    return filepath

def export_to_excel(tenders: List[Dict], filename: Optional[str] = None) -> str:
    """
    Export tenders to Excel format.
    
    Args:
        tenders: List of tender dictionaries
        filename: Optional filename for export (without extension)
        
    Returns:
        Path to the exported file
    """
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tenders_{timestamp}.xlsx"
    
    # Ensure filename has .xlsx extension
    if not filename.endswith('.xlsx'):
        filename += '.xlsx'
    
    # Create exports directory if it doesn't exist
    exports_dir = "exports"
    if not os.path.exists(exports_dir):
        os.makedirs(exports_dir)
    
    filepath = os.path.join(exports_dir, filename)
    
    # Convert to DataFrame
    df = pd.DataFrame(tenders)
    
    # Handle None values by replacing with empty strings
    df = df.fillna('')
    
    # Handle datetime columns
    datetime_columns = ['deadline']
    for col in datetime_columns:
        if col in df.columns:
            # Filter out None/empty values before conversion
            non_empty_mask = df[col] != ''
            if non_empty_mask.any():
                try:
                    df.loc[non_empty_mask, col] = pd.to_datetime(df.loc[non_empty_mask, col])
                except Exception:
                    # If conversion fails, leave as is
                    pass
    
    # Export to Excel
    df.to_excel(filepath, index=False)
    
    return filepath

def export_tenders(tenders: List[Dict], formats: Optional[List[str]] = None) -> Dict[str, str]:
    """
    Export tenders to multiple formats.
    
    Args:
        tenders: List of tender dictionaries
        formats: List of formats to export to ('json', 'excel')
        
    Returns:
        Dictionary mapping format to file path
    """
    if formats is None:
        formats = ['json', 'excel']
    
    exported_files = {}
    
    if 'json' in formats:
        json_path = export_to_json(tenders)
        exported_files['json'] = json_path
    
    if 'excel' in formats:
        excel_path = export_to_excel(tenders)
        exported_files['excel'] = excel_path
    
    return exported_files

def get_all_tenders_from_db() -> List[Dict]:
    """
    Retrieve all tenders from the database.
    This function connects directly to the database to fetch all tenders.
    
    Returns:
        List of tender dictionaries
    """
    # Import database connection
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
    
    from db.connection import get_db, MockMongoDB
    
    try:
        db = get_db()
        if db is None:
            print("Failed to connect to database")
            return []
        
        # Handle different database types with explicit type checking
        tenders = []
        
        # Check if it's a MockMongoDB instance
        if isinstance(db, MockMongoDB):
            # It's a mock MongoDB connection
            tenders = list(db.tenders.find())
        # Check if it has a tenders attribute (real MongoDB)
        elif hasattr(db, 'tenders'):
            # It's likely a MongoDB connection
            tenders = list(db.tenders.find())
        # Check if it has a cursor method (PostgreSQL)
        elif hasattr(db, 'cursor') and callable(getattr(db, 'cursor')):
            # It's likely a PostgreSQL connection
            try:
                with db.cursor() as cursor:
                    cursor.execute("SELECT * FROM tenders")
                    columns = [desc[0] for desc in cursor.description] if cursor.description else []
                    tenders = [dict(zip(columns, row)) for row in cursor.fetchall()]
            except Exception as e:
                print(f"Error querying PostgreSQL database: {e}")
                return []
        else:
            print("Unknown database type or connection issue")
            return []
        
        # Convert ObjectId to string for JSON serialization
        for tender in tenders:
            if "_id" in tender:
                tender["_id"] = str(tender["_id"])
        
        return tenders
    except Exception as e:
        print(f"Error retrieving tenders from database: {e}")
        return []

if __name__ == "__main__":
    # Example usage
    sample_tenders = [
        {
            "tender_id": "T1",
            "organization": "Ministry of Electronics",
            "category": "IT Services",
            "location": "Delhi",
            "value": 100000.0,
            "deadline": "2025-10-15T00:00:00",
            "description": "Software development services",
            "link": "http://test1.com"
        },
        {
            "tender_id": "T2",
            "organization": "Department of Roads",
            "category": "Construction",
            "location": "Mumbai",
            "value": 500000.0,
            "deadline": "2025-11-20T00:00:00",
            "description": "Road construction project",
            "link": "http://test2.com"
        }
    ]
    
    # Export sample data
    files = export_tenders(sample_tenders)
    print("Exported files:")
    for format_name, filepath in files.items():
        print(f"  {format_name.upper()}: {filepath}")