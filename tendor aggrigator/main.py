"""
Main orchestrator for the Tender Aggregator application.
"""
from agents.etenders import scrape_etenders
from agents.gem import scrape_gem
from nlp.extract import process_tenders
from db.connection import get_db, MockMongoDB
from nlp.extract import Tender
from typing import Any, Union
import psycopg2

def main():
    print("Starting Tender Aggregator...")
    
    # Scrape tenders from portals
    print("Scraping eTenders portal...")
    etenders_tenders = scrape_etenders()
    print(f"Found {len(etenders_tenders)} tenders from eTenders")
    
    print("Scraping GeM portal...")
    gem_tenders = scrape_gem()
    print(f"Found {len(gem_tenders)} tenders from GeM")
    
    # Combine all tenders
    all_tenders = etenders_tenders + gem_tenders
    print(f"Total tenders found: {len(all_tenders)}")
    
    # Process tenders with NLP
    print("Processing tenders with NLP...")
    processed_tenders = process_tenders(all_tenders)
    
    # Store in database
    print("Storing tenders in database...")
    db = get_db()
    
    # Check if database connection is valid
    if db is None:
        print("Failed to connect to database. Data will not be stored.")
        return
    
    # Handle different database types
    try:
        # Check for MongoDB or MockMongoDB
        if isinstance(db, MockMongoDB):
            # MockMongoDB
            collection = db.tenders
            # Clear existing data and insert new tenders
            collection.delete_many({})
            
            if processed_tenders:
                collection.insert_many([tender.dict() for tender in processed_tenders])
                print(f"Stored {len(processed_tenders)} tenders in database")
            else:
                print("No tenders to store")
        elif hasattr(db, 'tenders') and db.tenders is not None:
            # Real MongoDB
            collection = db.tenders
            # Clear existing data and insert new tenders
            collection.delete_many({})
            
            if processed_tenders:
                collection.insert_many([tender.dict() for tender in processed_tenders])
                print(f"Stored {len(processed_tenders)} tenders in database")
            else:
                print("No tenders to store")
        elif hasattr(db, 'cursor') and callable(getattr(db, 'cursor')):
            # PostgreSQL
            with db.cursor() as cursor:
                # Clear existing data
                cursor.execute("DELETE FROM tenders")
                
                # Insert new tenders
                if processed_tenders:
                    for tender in processed_tenders:
                        cursor.execute("""
                            INSERT INTO tenders (tender_id, organization, category, location, value, deadline, description, link)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            tender.tender_id,
                            tender.organization,
                            tender.category,
                            tender.location,
                            tender.value,
                            tender.deadline,
                            tender.description,
                            tender.link
                        ))
                    db.commit()
                    print(f"Stored {len(processed_tenders)} tenders in database")
                else:
                    print("No tenders to store")
        else:
            print("Unsupported database type. Data will not be stored.")
    except Exception as e:
        print(f"Error storing tenders in database: {e}")
        # Only call rollback on PostgreSQL connections
        rollback_func = getattr(db, 'rollback', None)
        if callable(rollback_func):
            try:
                rollback_func()
            except:
                pass  # Ignore rollback errors
    
    print("Tender Aggregator completed successfully!")

if __name__ == "__main__":
    main()