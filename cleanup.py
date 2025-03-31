import os
import glob
import shutil
import fnmatch
from config import RESULTS_DIR_ABS, CLEANUP_PATTERNS

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
    
    # Use cleanup patterns from config
    for file in os.listdir(RESULTS_DIR_ABS):
        if any(fnmatch.fnmatch(file, pattern) for pattern in CLEANUP_PATTERNS):
            file_path = os.path.join(RESULTS_DIR_ABS, file)
            try:
                size = os.path.getsize(file_path)
                files_info.append((file, size))
                total_size += size
                total_files += 1
            except OSError as e:
                print(f"Warning: Could not get size of {file}: {e}")
    
    if not files_info:
        print("No result files found in results directory.")
        return
    
    # Print summary before removal
    print(f"\nFound {total_files:,} files (Total size: {total_size / (1024*1024):.2f} MB):")
    for file, size in sorted(files_info):
        print(f"- {file} ({size / 1024:.2f} KB)")
    
    # Ask for confirmation
    print("\nOptions:")
    print("1. Remove individual files")
    print("2. Remove entire results directory")
    print("3. Cancel")
    
    choice = input("\nEnter your choice (1-3): ")
    
    if choice == '1':
        # Remove individual files
        print("\nRemoving files...")
        for file, _ in files_info:
            try:
                os.remove(os.path.join(RESULTS_DIR_ABS, file))
                print(f"✓ Removed {file}")
            except Exception as e:
                print(f"✗ Error removing {file}: {str(e)}")
        print(f"\nCleanup complete. Removed {total_files:,} files ({total_size / (1024*1024):.2f} MB)")
        
    elif choice == '2':
        # Remove entire directory
        confirm = input("\nAre you sure you want to remove the entire results directory? (yes/no): ")
        if confirm.lower() == 'yes':
            try:
                shutil.rmtree(RESULTS_DIR_ABS)
                print(f"✓ Removed results directory with {total_files:,} files ({total_size / (1024*1024):.2f} MB)")
            except Exception as e:
                print(f"✗ Error removing results directory: {str(e)}")
        else:
            print("Operation cancelled.")
    else:
        print("Operation cancelled.")

if __name__ == "__main__":
    cleanup_results()
