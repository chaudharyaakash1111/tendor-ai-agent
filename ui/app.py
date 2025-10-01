"""
Streamlit frontend for Tender Aggregator application.
"""
import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date
import io

# API base URL - assuming the FastAPI server is running on localhost:8001
API_BASE_URL = "http://localhost:8001"

def main():
    st.set_page_config(page_title="Tender Aggregator", page_icon="📋", layout="wide")
    
    # App title and description
    st.title("📋 Tender Aggregator")
    st.markdown("""
    Welcome to the Tender Aggregator application. 
    This tool helps you find and filter government tenders from various portals.
    """)
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Search Tenders", "View Tender Details", "Export Data", "Big Data Processing"])
    
    if page == "Home":
        show_home_page()
    elif page == "Search Tenders":
        show_search_page()
    elif page == "View Tender Details":
        show_tender_details_page()
    elif page == "Export Data":
        show_export_page()
    elif page == "Big Data Processing":
        show_big_data_page()

def show_home_page():
    st.header("Overview")
    st.markdown("""
    The Tender Aggregator collects tender information from multiple government portals including:
    - eTenders (https://etenders.gov.in)
    - GeM (https://gem.gov.in)
    
    Use the navigation sidebar to search for tenders or view specific tender details.
    """)
    
    # Display some statistics
    try:
        response = requests.get(f"{API_BASE_URL}/tenders")
        if response.status_code == 200:
            tenders = response.json()
            st.subheader(f"Total Tenders in Database: {len(tenders)}")
            
            # Show recent tenders
            if tenders:
                st.subheader("Recent Tenders")
                df = pd.DataFrame(tenders)
                # Select key columns to display
                display_columns = ["tender_id", "organization", "category", "location", "value", "deadline"]
                df_display = df[display_columns].head(10)
                st.dataframe(df_display)
        else:
            st.warning("Could not fetch tender statistics. API might be unavailable.")
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the API. Please make sure the FastAPI server is running on port 8001.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

def show_search_page():
    st.header("Search Tenders")
    
    # Search filters
    st.subheader("Filter Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        organization = st.text_input("Organization")
        location = st.text_input("Location")
        
    with col2:
        category = st.text_input("Category")
        min_value = st.number_input("Minimum Value", min_value=0, value=0)
        
    with col3:
        max_value = st.number_input("Maximum Value", min_value=0, value=1000000)
        query = st.text_input("Keyword Search")
    
    # Date filters
    st.subheader("Deadline Filters")
    col4, col5 = st.columns(2)
    
    with col4:
        deadline_from = st.date_input("Deadline From", value=date.today())
        
    with col5:
        deadline_to = st.date_input("Deadline To", value=date.today())
    
    # Search button
    if st.button("Search Tenders", type="primary"):
        # Build query parameters
        params = {}
        if organization:
            params["organization"] = organization
        if category:
            params["category"] = category
        if location:
            params["location"] = location
        if min_value > 0:
            params["min_value"] = min_value
        if max_value > 0:
            params["max_value"] = max_value
        if query:
            params["query"] = query
        # Handle date inputs correctly - they might be date objects or tuples of date objects
        if deadline_from:
            # Check if it's a tuple (multiple dates selected) and get the first date
            if isinstance(deadline_from, tuple) and len(deadline_from) > 0:
                params["deadline_from"] = deadline_from[0].isoformat()
            # Check if it's a date object
            elif isinstance(deadline_from, (date, datetime)):
                params["deadline_from"] = deadline_from.isoformat()
        if deadline_to:
            # Check if it's a tuple (multiple dates selected) and get the first date
            if isinstance(deadline_to, tuple) and len(deadline_to) > 0:
                params["deadline_to"] = deadline_to[0].isoformat()
            # Check if it's a date object
            elif isinstance(deadline_to, (date, datetime)):
                params["deadline_to"] = deadline_to.isoformat()
        
        # Make API request
        try:
            response = requests.get(f"{API_BASE_URL}/tenders/search", params=params)
            if response.status_code == 200:
                tenders = response.json()
                
                if tenders:
                    st.subheader(f"Found {len(tenders)} tenders")
                    
                    # Display results in a table
                    df = pd.DataFrame(tenders)
                    
                    # Format the display
                    if "value" in df.columns:
                        df["value"] = df["value"].apply(lambda x: f"₹{x:,.2f}")
                    
                    if "deadline" in df.columns:
                        df["deadline"] = pd.to_datetime(df["deadline"]).dt.strftime("%Y-%m-%d")
                    
                    # Select columns to display
                    display_columns = ["tender_id", "organization", "category", "location", "value", "deadline"]
                    df_display = df[display_columns]
                    
                    # Show the dataframe
                    st.dataframe(df_display, use_container_width=True)
                    
                    # Option to download results
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download Results as CSV",
                        data=csv,
                        file_name="tenders.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("No tenders found matching your criteria.")
            else:
                st.error(f"Error fetching tenders: {response.status_code}")
        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the API. Please make sure the FastAPI server is running on port 8001.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

def show_tender_details_page():
    st.header("View Tender Details")
    
    # Input for tender ID
    tender_id = st.text_input("Enter Tender ID")
    
    if st.button("Get Tender Details", type="primary") and tender_id:
        try:
            response = requests.get(f"{API_BASE_URL}/tenders/{tender_id}")
            if response.status_code == 200:
                tender = response.json()
                
                # Display tender details
                st.subheader(f"Tender ID: {tender['tender_id']}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Organization", tender['organization'])
                    st.metric("Location", tender['location'])
                    st.metric("Category", tender['category'])
                
                with col2:
                    st.metric("Value", f"₹{tender['value']:,.2f}")
                    st.metric("Deadline", tender['deadline'])
                
                st.subheader("Description")
                st.write(tender['description'])
                
                st.subheader("Link")
                st.markdown(f"[View Tender Details]({tender['link']})")
                
            elif response.status_code == 404:
                st.warning("Tender not found. Please check the Tender ID.")
            else:
                st.error(f"Error fetching tender: {response.status_code}")
        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the API. Please make sure the FastAPI server is running on port 8001.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

def show_export_page():
    st.header("Export Tender Data")
    st.markdown("""
    Export all tenders from the database to JSON or Excel format.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Export to JSON")
        if st.button("Export All Tenders to JSON"):
            try:
                response = requests.get(f"{API_BASE_URL}/export?format=json")
                if response.status_code == 200:
                    # Create download button for JSON
                    st.download_button(
                        label="Download JSON File",
                        data=response.content,
                        file_name="tenders_export.json",
                        mime="application/json"
                    )
                    st.success("JSON export successful! Click the download button to save the file.")
                else:
                    st.error(f"Error exporting to JSON: {response.status_code}")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the API. Please make sure the FastAPI server is running on port 8001.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    
    with col2:
        st.subheader("Export to Excel")
        if st.button("Export All Tenders to Excel"):
            try:
                response = requests.get(f"{API_BASE_URL}/export?format=excel")
                if response.status_code == 200:
                    # Create download button for Excel
                    st.download_button(
                        label="Download Excel File",
                        data=response.content,
                        file_name="tenders_export.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    st.success("Excel export successful! Click the download button to save the file.")
                else:
                    st.error(f"Error exporting to Excel: {response.status_code}")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the API. Please make sure the FastAPI server is running on port 8001.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    
    st.info("Note: Export functionality requires the FastAPI server to be running.")

def show_big_data_page():
    st.header("Big Data Processing")
    st.markdown("""
    Process and export large amounts of tender data efficiently using batch processing.
    This is recommended for datasets with thousands of records.
    """)
    
    # Get dataset statistics
    st.subheader("Dataset Statistics")
    try:
        response = requests.get(f"{API_BASE_URL}/stats")
        if response.status_code == 200:
            stats = response.json()
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Records", stats.get("total_records", "N/A"))
                st.metric("Organizations", stats.get("unique_organizations", "N/A"))
                
            with col2:
                st.metric("Categories", stats.get("unique_categories", "N/A"))
                st.metric("Locations", stats.get("unique_locations", "N/A"))
                
            with col3:
                st.metric("Max Value", f"₹{stats.get('max_tender_value', 0):,.2f}")
                st.metric("Avg Value", f"₹{stats.get('avg_tender_value', 0):,.2f}")
        else:
            st.warning("Could not fetch dataset statistics.")
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the API. Please make sure the FastAPI server is running on port 8001.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
    
    # Big data export options
    st.subheader("Big Data Export")
    
    # Batch size selection
    batch_size = st.slider("Batch Size", min_value=100, max_value=5000, value=1000, step=100)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Export to JSON (Large Dataset)")
        if st.button("Export Large Dataset to JSON"):
            try:
                with st.spinner("Processing large dataset... This may take a while."):
                    response = requests.get(f"{API_BASE_URL}/export/big?format=json&batch_size={batch_size}")
                    if response.status_code == 200:
                        # Create download button for JSON
                        st.download_button(
                            label="Download Large JSON File",
                            data=response.content,
                            file_name=f"large_tenders_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )
                        st.success("Large JSON export successful! Click the download button to save the file.")
                    else:
                        st.error(f"Error exporting large dataset to JSON: {response.status_code}")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the API. Please make sure the FastAPI server is running on port 8001.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    
    with col2:
        st.subheader("Export to Excel (Large Dataset)")
        if st.button("Export Large Dataset to Excel"):
            try:
                with st.spinner("Processing large dataset... This may take a while."):
                    response = requests.get(f"{API_BASE_URL}/export/big?format=excel&batch_size={batch_size}")
                    if response.status_code == 200:
                        # Create download button for Excel
                        st.download_button(
                            label="Download Large Excel File",
                            data=response.content,
                            file_name=f"large_tenders_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                        st.success("Large Excel export successful! Click the download button to save the file.")
                    else:
                        st.error(f"Error exporting large dataset to Excel: {response.status_code}")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the API. Please make sure the FastAPI server is running on port 8001.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    
    st.info("Note: Big data processing requires the FastAPI server to be running and is recommended for datasets with thousands of records.")

if __name__ == "__main__":
    main()