"""
Script to run the export functionality from command line.
"""
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from export_tenders import main

if __name__ == "__main__":
    main()