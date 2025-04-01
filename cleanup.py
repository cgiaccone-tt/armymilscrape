import os
import glob
import shutil
import fnmatch
from datetime import datetime, timedelta
from config import RESULTS_DIR_ABS
import sys

# Force unbuffered output
if sys.stdout.isatty():
    sys.stdout.reconfigure(encoding='utf-8')
else:
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

def clean_text_for_display(text):
    """Clean text for terminal display."""
    if not isinstance(text, str):
        return str(text)
    # Replace problematic characters with ASCII alternatives
    replacements = {
        '✓': '[OK]',
        '∞': 'inf',
        '"': '"',
        '"': '"',
        ''': "'",
        ''': "'",
        '–': '-',
        '—': '-',
        '…': '...'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

def cleanup_results():
    """Clean up result files from the scraper output directory."""
    if not os.path.exists(RESULTS_DIR_ABS):
        print("Results directory not found. Nothing to clean up.")
        return
        
    # Count files and total size
    total_size = 0
    total_files = 0
    
    print("Finding result files...")
    files_info = []
    
    # File patterns to match
    cleanup_patterns = [
        'army_results_*.xlsx',
        'army_results_*.csv',
        'detailed_analysis_*.txt',
        'analysis_results_*.txt'
    ]
    
    # Get file information
    for pattern in cleanup_patterns:
        for file in glob.glob(os.path.join(RESULTS_DIR_ABS, pattern)):
            try:
                size = os.path.getsize(file)
                mtime = os.path.getmtime(file)
                files_info.append((file, size, mtime))
                total_size += size
                total_files += 1
            except OSError as e:
                print(f"Warning: Could not get info for {file}: {e}")
    
    if not files_info:
        print("No result files found in results directory.")
        return
    
    # Group files by type
    files_by_type = {
        'Results': [],
        'Analysis': [],
        'Other': []
    }
    
    for file, size, mtime in sorted(files_info, key=lambda x: x[2], reverse=True):
        filename = os.path.basename(file)
        if filename.startswith('army_results_'):
            files_by_type['Results'].append((file, size, mtime))
        elif filename.startswith(('detailed_analysis_', 'analysis_results_')):
            files_by_type['Analysis'].append((file, size, mtime))
        else:
            files_by_type['Other'].append((file, size, mtime))
    
    # Print summary before removal
    print(f"\nFound {total_files:,} files (Total size: {total_size / (1024*1024):.2f} MB):")
    
    for file_type, files in files_by_type.items():
        if files:
            print(f"\n{file_type}:")
            for file, size, mtime in files:
                mtime_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                print(f"- {clean_text_for_display(os.path.basename(file))}")
                print(f"  Size: {size / 1024:.2f} KB")
                print(f"  Modified: {mtime_str}")
    
    # Ask for confirmation
    print("\nOptions:")
    print("1. Remove individual files")
    print("2. Remove all files older than X days")
    print("3. Remove entire results directory")
    print("4. Cancel")
    
    choice = input("\nEnter your choice (1-4): ")
    
    if choice == '1':
        # Remove individual files
        print("\nEnter the numbers of files to remove (comma-separated) or 'all':")
        all_files = []
        for i, (file_type, files) in enumerate(files_by_type.items(), 1):
            if files:
                print(f"\n{file_type}:")
                for j, (file, _, _) in enumerate(files, 1):
                    print(f"{len(all_files) + j}. {clean_text_for_display(os.path.basename(file))}")
                all_files.extend(files)
        
        selection = input("\nFiles to remove: ").strip()
        if selection.lower() == 'all':
            indices = range(len(all_files))
        else:
            try:
                indices = [int(i.strip()) - 1 for i in selection.split(',')]
            except ValueError:
                print("Invalid input. Canceling cleanup.")
                return
        
        for idx in indices:
            if 0 <= idx < len(all_files):
                file = all_files[idx][0]
                try:
                    os.remove(file)
                    print(f"Removed: {clean_text_for_display(os.path.basename(file))}")
                except OSError as e:
                    print(f"Error removing {clean_text_for_display(os.path.basename(file))}: {e}")
    
    elif choice == '2':
        days = input("Remove files older than how many days? ")
        try:
            days = int(days)
            cutoff = datetime.now() - timedelta(days=days)
            removed = 0
            for file, _, mtime in sum(files_by_type.values(), []):
                if datetime.fromtimestamp(mtime) < cutoff:
                    try:
                        os.remove(file)
                        print(f"Removed: {clean_text_for_display(os.path.basename(file))}")
                        removed += 1
                    except OSError as e:
                        print(f"Error removing {clean_text_for_display(os.path.basename(file))}: {e}")
            print(f"\nRemoved {removed} files older than {days} days")
        except ValueError:
            print("Invalid number of days. Canceling cleanup.")
    
    elif choice == '3':
        confirm = input("Are you sure you want to remove ALL files? (yes/no): ")
        if confirm.lower() == 'yes':
            try:
                shutil.rmtree(RESULTS_DIR_ABS)
                os.makedirs(RESULTS_DIR_ABS)
                print("Results directory cleared and recreated.")
            except OSError as e:
                print(f"Error clearing results directory: {e}")
        else:
            print("Cleanup canceled.")
    
    else:
        print("Cleanup canceled.")

if __name__ == "__main__":
    cleanup_results()
