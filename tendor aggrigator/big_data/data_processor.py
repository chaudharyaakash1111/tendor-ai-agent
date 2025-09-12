"""
Module for processing large amounts of tender data efficiently.
"""
import pandas as pd
from typing import List, Dict, Generator, Optional, Any
import json
from datetime import datetime
import os
from db.connection import get_db, MockMongoDB

class BigDataProcessor:
    """Processor for handling large volumes of tender data."""
    
    def __init__(self, batch_size: int = 1000):
        """
        Initialize the big data processor.
        
        Args:
            batch_size: Number of records to process in each batch
        """
        self.batch_size = batch_size
        self.db = get_db()
        if self.db is None:
            raise Exception("Failed to connect to database")
    
    def get_tenders_batch(self, batch_size: Optional[int] = None) -> Generator[List[Dict], None, None]:
        """
        Retrieve tenders in batches to handle large datasets efficiently.
        
        Args:
            batch_size: Size of each batch (defaults to instance batch_size)
            
        Yields:
            Lists of tender dictionaries
        """
        if batch_size is None:
            batch_size = self.batch_size
            
        # Handle different database types
        try:
            # Check if database connection is valid
            if self.db is None:
                raise Exception("Database connection is not valid")
                
            if isinstance(self.db, MockMongoDB):
                # MockMongoDB
                # Get total count for MockMongoDB
                total_count = len(self.db.tenders.data)
                
                # Process in batches
                skip = 0
                while skip < total_count:
                    # For MockMongoDB, implement pagination manually
                    tenders = self.db.tenders.data[skip:skip + batch_size]
                    
                    # Convert ObjectId to string for JSON serialization
                    for tender in tenders:
                        if "_id" in tender:
                            tender["_id"] = str(tender["_id"])
                    
                    yield tenders
                    skip += batch_size
            elif hasattr(self.db, 'tenders') and self.db.tenders is not None:
                # Real MongoDB
                # Get total count
                total_count = self.db.tenders.count_documents({})
                
                # Process in batches
                skip = 0
                while skip < total_count:
                    tenders = list(self.db.tenders.find().skip(skip).limit(batch_size))
                    
                    # Convert ObjectId to string for JSON serialization
                    for tender in tenders:
                        if "_id" in tender:
                            tender["_id"] = str(tender["_id"])
                    
                    yield tenders
                    skip += batch_size
            elif hasattr(self.db, 'cursor') and callable(getattr(self.db, 'cursor')):
                # PostgreSQL - implement batch processing
                offset = 0
                while True:
                    with self.db.cursor() as cursor:
                        cursor.execute("SELECT * FROM tenders LIMIT %s OFFSET %s", (batch_size, offset))
                        columns = [desc[0] for desc in cursor.description] if cursor.description else []
                        tenders = [dict(zip(columns, row)) for row in cursor.fetchall()]
                        
                        if not tenders:
                            break
                            
                        yield tenders
                        offset += batch_size
            else:
                raise Exception("Unsupported database type")
        except Exception as e:
            print(f"Error retrieving tenders in batches: {e}")
            yield []
    
    def export_large_dataset_to_json(self, filename: Optional[str] = None, batch_size: Optional[int] = None) -> str:
        """
        Export large dataset to JSON format using streaming to handle memory efficiently.
        
        Args:
            filename: Output filename (without extension)
            batch_size: Batch size for processing
            
        Returns:
            Path to the exported file
        """
        if batch_size is None:
            batch_size = self.batch_size
            
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"large_tenders_export_{timestamp}.json"
            
        # Ensure filename has .json extension
        if not filename.endswith('.json'):
            filename += '.json'
        
        # Create exports directory if it doesn't exist
        exports_dir = "exports"
        if not os.path.exists(exports_dir):
            os.makedirs(exports_dir)
            
        filepath = os.path.join(exports_dir, filename)
        
        # Write JSON array start
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('[\n')
            
        # Process batches and write to file
        first_record = True
        batch_count = 0
        
        for batch in self.get_tenders_batch(batch_size):
            if not batch:
                continue
                
            # Write batch to file
            with open(filepath, 'a', encoding='utf-8') as f:
                for tender in batch:
                    if not first_record:
                        f.write(',\n')
                    json.dump(tender, f, default=str)
                    first_record = False
                    
            batch_count += 1
            print(f"Processed batch {batch_count} ({len(batch)} records)")
        
        # Close JSON array
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write('\n]')
            
        print(f"Export completed. Total batches: {batch_count}")
        return filepath
    
    def export_large_dataset_to_excel(self, filename: Optional[str] = None, batch_size: Optional[int] = None) -> str:
        """
        Export large dataset to Excel format with multiple sheets for better organization.
        
        Args:
            filename: Output filename (without extension)
            batch_size: Batch size for processing
            
        Returns:
            Path to the exported file
        """
        if batch_size is None:
            batch_size = self.batch_size
            
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"large_tenders_export_{timestamp}.xlsx"
            
        # Ensure filename has .xlsx extension
        if not filename.endswith('.xlsx'):
            filename += '.xlsx'
        
        # Create exports directory if it doesn't exist
        exports_dir = "exports"
        if not os.path.exists(exports_dir):
            os.makedirs(exports_dir)
            
        filepath = os.path.join(exports_dir, filename)
        
        # Create Excel writer
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            batch_count = 0
            total_records = 0
            
            # Process batches
            for batch in self.get_tenders_batch(batch_size):
                if not batch:
                    continue
                    
                # Convert to DataFrame
                df = pd.DataFrame(batch)
                
                # Handle datetime columns
                datetime_columns = ['deadline']
                for col in datetime_columns:
                    if col in df.columns:
                        try:
                            df[col] = pd.to_datetime(df[col])
                        except Exception:
                            pass
                
                # Write to Excel sheet
                sheet_name = f"Batch_{batch_count+1}"
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                batch_count += 1
                total_records += len(batch)
                print(f"Processed batch {batch_count} ({len(batch)} records)")
            
            # Create summary sheet
            summary_data = {
                "Metric": ["Total Batches", "Total Records", "Export Date"],
                "Value": [batch_count, total_records, datetime.now().isoformat()]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name="Summary", index=False)
            
        print(f"Excel export completed. Total batches: {batch_count}, Total records: {total_records}")
        return filepath
    
    def get_data_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the tender dataset.
        
        Returns:
            Dictionary with dataset statistics
        """
        # Check if database connection is valid
        if self.db is None:
            raise Exception("Database connection is not valid")
            
        try:
            # Handle different database types
            if isinstance(self.db, MockMongoDB):
                # For MockMongoDB, implement statistics manually
                tenders_data = self.db.tenders.data
                total_count = len(tenders_data)
                
                # Get sample for field analysis
                sample_tender = tenders_data[0] if tenders_data else None
                
                # Get unique values for key fields (manual implementation for MockMongoDB)
                organizations = len(set(tender.get("organization", "") for tender in tenders_data))
                categories = len(set(tender.get("category", "") for tender in tenders_data))
                locations = len(set(tender.get("location", "") for tender in tenders_data))
                
                # Value statistics
                values = [tender.get("value", 0) for tender in tenders_data if tender.get("value") is not None]
                if values:
                    max_value = max(values)
                    min_value = min(values)
                    avg_value = sum(values) / len(values)
                else:
                    max_value = min_value = avg_value = 0
                
                return {
                    "total_records": total_count,
                    "unique_organizations": organizations,
                    "unique_categories": categories,
                    "unique_locations": locations,
                    "max_tender_value": max_value,
                    "min_tender_value": min_value,
                    "avg_tender_value": avg_value,
                    "fields": list(sample_tender.keys()) if sample_tender else []
                }
            elif hasattr(self.db, 'tenders') and self.db.tenders is not None:
                # Real MongoDB
                # Get total count
                total_count = self.db.tenders.count_documents({})
                
                # Get sample for field analysis
                sample_tender = self.db.tenders.find_one()
                
                # Get unique values for key fields
                organizations = len(list(self.db.tenders.distinct("organization")))
                categories = len(list(self.db.tenders.distinct("category")))
                locations = len(list(self.db.tenders.distinct("location")))
                
                # Value statistics
                value_stats = self.db.tenders.aggregate([
                    {"$group": {
                        "_id": None,
                        "max_value": {"$max": "$value"},
                        "min_value": {"$min": "$value"},
                        "avg_value": {"$avg": "$value"}
                    }}
                ])
                
                value_stats = list(value_stats)
                if value_stats:
                    stats = value_stats[0]
                    max_value = stats.get("max_value", 0)
                    min_value = stats.get("min_value", 0)
                    avg_value = stats.get("avg_value", 0)
                else:
                    max_value = min_value = avg_value = 0
                
                return {
                    "total_records": total_count,
                    "unique_organizations": organizations,
                    "unique_categories": categories,
                    "unique_locations": locations,
                    "max_tender_value": max_value,
                    "min_tender_value": min_value,
                    "avg_tender_value": avg_value,
                    "fields": list(sample_tender.keys()) if sample_tender else []
                }
            elif hasattr(self.db, 'cursor') and callable(getattr(self.db, 'cursor')):
                # PostgreSQL
                with self.db.cursor() as cursor:
                    # Get total count
                    cursor.execute("SELECT COUNT(*) FROM tenders")
                    count_result = cursor.fetchone()
                    total_count = count_result[0] if count_result else 0
                    
                    # Get sample for field analysis
                    cursor.execute("SELECT * FROM tenders LIMIT 1")
                    columns = [desc[0] for desc in cursor.description] if cursor.description else []
                    sample_row = cursor.fetchone()
                    sample_tender = dict(zip(columns, sample_row)) if sample_row else None
                    
                    # Get unique values for key fields
                    cursor.execute("SELECT COUNT(DISTINCT organization) FROM tenders")
                    org_result = cursor.fetchone()
                    organizations = org_result[0] if org_result else 0
                    
                    cursor.execute("SELECT COUNT(DISTINCT category) FROM tenders")
                    cat_result = cursor.fetchone()
                    categories = cat_result[0] if cat_result else 0
                    
                    cursor.execute("SELECT COUNT(DISTINCT location) FROM tenders")
                    loc_result = cursor.fetchone()
                    locations = loc_result[0] if loc_result else 0
                    
                    # Value statistics
                    cursor.execute("""
                        SELECT 
                            MAX(value) as max_value,
                            MIN(value) as min_value,
                            AVG(value) as avg_value
                        FROM tenders
                    """)
                    stats = cursor.fetchone()
                    max_value = stats[0] if stats and stats[0] is not None else 0
                    min_value = stats[1] if stats and stats[1] is not None else 0
                    avg_value = stats[2] if stats and stats[2] is not None else 0
                    
                    return {
                        "total_records": total_count,
                        "unique_organizations": organizations,
                        "unique_categories": categories,
                        "unique_locations": locations,
                        "max_tender_value": max_value,
                        "min_tender_value": min_value,
                        "avg_tender_value": avg_value,
                        "fields": list(sample_tender.keys()) if sample_tender else []
                    }
            else:
                raise Exception("Unsupported database type")
        except Exception as e:
            print(f"Error getting data statistics: {e}")
            return {}

def process_large_dataset():
    """
    Process large dataset with optimized memory usage.
    """
    print("Processing large tender dataset...")
    
    try:
        # Initialize processor
        processor = BigDataProcessor(batch_size=500)
        
        # Get statistics
        stats = processor.get_data_statistics()
        print("Dataset Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Export large dataset to JSON
        print("\nExporting large dataset to JSON...")
        json_path = processor.export_large_dataset_to_json()
        print(f"JSON export completed: {json_path}")
        
        # Export large dataset to Excel
        print("\nExporting large dataset to Excel...")
        excel_path = processor.export_large_dataset_to_excel()
        print(f"Excel export completed: {excel_path}")
        
        return json_path, excel_path
    except Exception as e:
        print(f"Error processing large dataset: {e}")
        return None, None

if __name__ == "__main__":
    process_large_dataset()