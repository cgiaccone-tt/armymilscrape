import pandas as pd
import csv
import os
import glob

def find_latest_csv():
    # Look for CSV files with timestamp in name
    csv_files = glob.glob('army_results_*.csv')
    if not csv_files:
        # Try the default name
        if os.path.exists('army_results.csv'):
            return 'army_results.csv'
        # Try looking for any CSV that might be related
        csv_files = glob.glob('*.csv')
    if not csv_files:
        raise FileNotFoundError("No CSV files found")
    # Return the most recently modified file
    return max(csv_files, key=os.path.getmtime)

try:
    # Find the CSV file
    input_file = find_latest_csv()
    print(f"Found input file: {input_file}")

    # Read the CSV with proper encoding, trying different encodings if necessary
    encodings = ['utf-8-sig', 'utf-8', 'cp1252']
    df = None
    for encoding in encodings:
        try:
            print(f"Trying to read with {encoding} encoding...")
            df = pd.read_csv(input_file, encoding=encoding)
            print(f"Successfully read with {encoding} encoding")
            break
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"Error with {encoding}: {str(e)}")
            continue

    if df is None:
        raise ValueError("Could not read the CSV file with any encoding")

    # Clean the data
    def clean_text(text):
        if pd.isna(text):
            return ""
        # Remove problematic characters and normalize newlines
        text = str(text).replace('\r\n', ' ').replace('\n', ' ')
        # Remove any double quotes that might interfere with CSV formatting
        text = text.replace('"', "'")
        # Remove null bytes and other problematic characters
        text = ''.join(char for char in text if ord(char) >= 32)
        return text.strip()

    # Clean all text columns
    print("Cleaning data...")
    for col in df.columns:
        df[col] = df[col].apply(clean_text)

    # Generate output filenames with timestamp
    import time
    timestamp = int(time.time())
    excel_file = f'army_results_{timestamp}.xlsx'
    csv_file = f'army_results_{timestamp}_clean.csv'

    # Write to Excel with error handling
    print(f"Creating Excel file: {excel_file}")
    try:
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Results')
            worksheet = writer.sheets['Results']
            
            # Optimize column widths
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(str(col))
                )
                # Limit max width to 100 characters
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 100)
        print("Excel file created successfully")
    except Exception as e:
        print(f"Warning: Could not create Excel file: {str(e)}")
        print("Continuing with CSV creation...")

    # Write clean CSV with proper quoting
    print(f"Creating clean CSV file: {csv_file}")
    df.to_csv(csv_file, 
              index=False, 
              quoting=csv.QUOTE_ALL,  # Quote all fields
              encoding='utf-8-sig')   # Add BOM for Excel

    print("\nDone! Created:")
    if os.path.exists(excel_file):
        print(f"1. {excel_file} - Excel file")
    print(f"2. {csv_file} - Clean CSV file with proper quoting")

except Exception as e:
    print(f"Error: {str(e)}")
    print("Please provide the path to your CSV file when running the script:")
    print("Example: python fix_csv.py army_results_1743444527.csv")
