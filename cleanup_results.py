import pandas as pd
from datetime import datetime
import os

def cleanup_results(filename):
    print(f"Processing {filename}...")
    
    # Read the Excel file
    df = pd.read_excel(filename)
    total_rows = len(df)
    
    # Convert timestamp strings to datetime for proper sorting
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Sort by URL and timestamp, keep the latest entry for each URL
    df = df.sort_values(['url', 'timestamp']).drop_duplicates('url', keep='last')
    
    # Sort by timestamp for the final output
    df = df.sort_values('timestamp')
    
    # Generate new filename with _deduped suffix
    base, ext = os.path.splitext(filename)
    new_filename = f"{base}_deduped{ext}"
    
    # Save to new Excel file
    df.to_excel(new_filename, index=False)
    
    # Print statistics
    removed = total_rows - len(df)
    print(f"\nResults:")
    print(f"Original rows: {total_rows}")
    print(f"Unique URLs: {len(df)}")
    print(f"Duplicates removed: {removed}")
    print(f"\nSaved deduplicated results to: {new_filename}")

if __name__ == "__main__":
    cleanup_results("results/army_results_1743473929.xlsx")
