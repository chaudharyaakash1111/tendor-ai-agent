"""
Main orchestrator for the Tender Aggregator application.
"""
from agents.scrapers import (
    scrape_etenders, scrape_gem, scrape_ireps, scrape_defproc,
    scrape_mahatenders, scrape_rajasthan, scrape_up, scrape_tntenders,
    scrape_kerala, scrape_wb, scrape_jharkhand, scrape_assam,
    scrape_tendertiger, scrape_bidassist, scrape_tendersinfo
)
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
    
    print("Scraping IREPS portal...")
    ireps_tenders = scrape_ireps()
    print(f"Found {len(ireps_tenders)} tenders from IREPS")
    
    print("Scraping Defence Procurement Portal...")
    defproc_tenders = scrape_defproc()
    print(f"Found {len(defproc_tenders)} tenders from Defence Procurement Portal")
    
    print("Scraping Maharashtra Tenders Portal...")
    mahatenders_tenders = scrape_mahatenders()
    print(f"Found {len(mahatenders_tenders)} tenders from Maharashtra Tenders Portal")
    
    print("Scraping Rajasthan eProcurement Portal...")
    rajasthan_tenders = scrape_rajasthan()
    print(f"Found {len(rajasthan_tenders)} tenders from Rajasthan eProcurement Portal")
    
    print("Scraping Uttar Pradesh eTender Portal...")
    up_tenders = scrape_up()
    print(f"Found {len(up_tenders)} tenders from Uttar Pradesh eTender Portal")
    
    print("Scraping Tamil Nadu eTenders Portal...")
    tntenders_tenders = scrape_tntenders()
    print(f"Found {len(tntenders_tenders)} tenders from Tamil Nadu eTenders Portal")
    
    print("Scraping Kerala Tenders Portal...")
    kerala_tenders = scrape_kerala()
    print(f"Found {len(kerala_tenders)} tenders from Kerala Tenders Portal")
    
    print("Scraping West Bengal Tenders Portal...")
    wb_tenders = scrape_wb()
    print(f"Found {len(wb_tenders)} tenders from West Bengal Tenders Portal")
    
    print("Scraping Jharkhand Tenders Portal...")
    jharkhand_tenders = scrape_jharkhand()
    print(f"Found {len(jharkhand_tenders)} tenders from Jharkhand Tenders Portal")
    
    print("Scraping Assam Tenders Portal...")
    assam_tenders = scrape_assam()
    print(f"Found {len(assam_tenders)} tenders from Assam Tenders Portal")
    
    print("Scraping TenderTiger...")
    tendertiger_tenders = scrape_tendertiger()
    print(f"Found {len(tendertiger_tenders)} tenders from TenderTiger")
    
    print("Scraping BidAssist...")
    bidassist_tenders = scrape_bidassist()
    print(f"Found {len(bidassist_tenders)} tenders from BidAssist")
    
    print("Scraping TendersInfo...")
    tendersinfo_tenders = scrape_tendersinfo()
    print(f"Found {len(tendersinfo_tenders)} tenders from TendersInfo")
    
    # Combine all tenders
    all_tenders = (etenders_tenders + gem_tenders + ireps_tenders + defproc_tenders + 
                   mahatenders_tenders + rajasthan_tenders + up_tenders + tntenders_tenders + 
                   kerala_tenders + wb_tenders + jharkhand_tenders + assam_tenders + 
                   tendertiger_tenders + bidassist_tenders + tendersinfo_tenders)
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