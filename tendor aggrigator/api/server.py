"""
FastAPI server for Tender Aggregator.
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from typing import List, Optional, Any
import os
from db.connection import get_db, MockMongoDB
import uvicorn

app = FastAPI(title="Tender Aggregator API", version="1.0.0")

def get_tenders_from_db():
    """Helper function to get tenders from database with proper error handling."""
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        # Handle different database types
        if isinstance(db, MockMongoDB):
            # MockMongoDB
            return list(db.tenders.find())
        elif hasattr(db, 'tenders') and db.tenders is not None:
            # Real MongoDB
            return list(db.tenders.find())
        elif hasattr(db, 'cursor') and callable(getattr(db, 'cursor')):
            # PostgreSQL
            with db.cursor() as cursor:
                cursor.execute("SELECT * FROM tenders")
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        else:
            raise HTTPException(status_code=500, detail="Unsupported database type")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving tenders: {str(e)}")

def get_tender_by_id_from_db(tender_id: str):
    """Helper function to get a specific tender by ID with proper error handling."""
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        # Handle different database types
        if isinstance(db, MockMongoDB):
            # MockMongoDB
            return db.tenders.find_one({"tender_id": tender_id})
        elif hasattr(db, 'tenders') and db.tenders is not None:
            # Real MongoDB
            return db.tenders.find_one({"tender_id": tender_id})
        elif hasattr(db, 'cursor') and callable(getattr(db, 'cursor')):
            # PostgreSQL
            with db.cursor() as cursor:
                cursor.execute("SELECT * FROM tenders WHERE tender_id = %s", (tender_id,))
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                row = cursor.fetchone()
                return dict(zip(columns, row)) if row else None
        else:
            raise HTTPException(status_code=500, detail="Unsupported database type")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving tender: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "Welcome to Tender Aggregator API"}

@app.get("/tenders", response_model=List[dict])
def get_tenders():
    """Get all tenders."""
    tenders = get_tenders_from_db()
    # Convert ObjectId to string for JSON serialization (MongoDB only)
    for tender in tenders:
        if "_id" in tender:
            tender["_id"] = str(tender["_id"])
    return tenders

@app.get("/tenders/search", response_model=List[dict])
def search_tenders(
    organization: Optional[str] = None,
    category: Optional[str] = None,
    location: Optional[str] = None,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    deadline_from: Optional[str] = None,
    deadline_to: Optional[str] = None,
    query: Optional[str] = None
):
    """Search tenders with filters."""
    # Get all tenders
    tenders = get_tenders_from_db()
    # Convert ObjectId to string for JSON serialization (MongoDB only)
    for tender in tenders:
        if "_id" in tender:
            tender["_id"] = str(tender["_id"])
    
    # Apply filters
    filters = {}
    if organization:
        filters["organization"] = organization
    if category:
        filters["category"] = category
    if location:
        filters["location"] = location
    if min_value is not None:
        filters["min_value"] = min_value
    if max_value is not None:
        filters["max_value"] = max_value
    if deadline_from:
        filters["deadline_from"] = deadline_from
    if deadline_to:
        filters["deadline_to"] = deadline_to
    
    from api.filter import filter_tenders, rank_tenders
    filtered_tenders = filter_tenders(tenders, filters)
    
    # Apply ranking
    ranked_tenders = rank_tenders(filtered_tenders, query or "")
    
    return ranked_tenders

@app.get("/tenders/{tender_id}", response_model=dict)
def get_tender(tender_id: str):
    """Get a specific tender by ID."""
    tender = get_tender_by_id_from_db(tender_id)
    
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")
    
    # Convert ObjectId to string for JSON serialization (MongoDB only)
    if "_id" in tender:
        tender["_id"] = str(tender["_id"])
    
    return tender

@app.get("/export")
def export_tenders(format: str = "json"):
    """
    Export all tenders to JSON or Excel format.
    
    Args:
        format: Export format ('json' or 'excel')
        
    Returns:
        File response with exported data
    """
    from export.data_exporter import get_all_tenders_from_db, export_to_json, export_to_excel
    
    # Get all tenders from database
    tenders = get_all_tenders_from_db()
    
    if not tenders:
        raise HTTPException(status_code=404, detail="No tenders found to export")
    
    # Export based on format
    if format.lower() == "excel":
        filepath = export_to_excel(tenders, "tenders_export")
        return FileResponse(filepath, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename="tenders_export.xlsx")
    else:
        filepath = export_to_json(tenders, "tenders_export")
        return FileResponse(filepath, media_type='application/json', filename="tenders_export.json")

@app.get("/export/big")
def export_big_dataset(format: str = "json", batch_size: int = 1000):
    """
    Export large datasets efficiently using batch processing.
    
    Args:
        format: Export format ('json' or 'excel')
        batch_size: Number of records per batch
        
    Returns:
        File response with exported data
    """
    from big_data.data_processor import BigDataProcessor
    
    try:
        # Initialize processor
        processor = BigDataProcessor(batch_size=batch_size)
        
        # Export based on format
        if format.lower() == "excel":
            filepath = processor.export_large_dataset_to_excel(batch_size=batch_size)
            return FileResponse(filepath, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename=os.path.basename(filepath))
        else:
            filepath = processor.export_large_dataset_to_json(batch_size=batch_size)
            return FileResponse(filepath, media_type='application/json', filename=os.path.basename(filepath))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting dataset: {str(e)}")

@app.get("/stats")
def get_dataset_statistics():
    """
    Get statistics about the tender dataset.
    
    Returns:
        Dataset statistics
    """
    from big_data.data_processor import BigDataProcessor
    
    try:
        # Initialize processor
        processor = BigDataProcessor()
        
        # Get statistics
        stats = processor.get_data_statistics()
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting dataset statistics: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)