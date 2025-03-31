from scraper import ArmyWebScraper
from backup_manager import BackupManager
from datetime import datetime
import os
from config import RESULTS_DIR_ABS, SETTINGS

def test_save():
    """Test the save functionality and backup system."""
    # Create a scraper instance
    scraper = ArmyWebScraper()
    
    # Get the current directory and results directory
    print(f"Results directory: {RESULTS_DIR_ABS}")
    print(f"Results directory exists: {os.path.exists(RESULTS_DIR_ABS)}")
    print(f"Results directory is writable: {os.access(RESULTS_DIR_ABS, os.W_OK) if os.path.exists(RESULTS_DIR_ABS) else 'N/A'}")
    
    # Add some test data
    test_data = [
        {
            'url': 'https://test.army.mil/page1',
            'title': 'Test Page 1 with special chars: é,ñ,ü',
            'keywords_found': 'test,keyword1',
            'keyword_contexts': '[{"keyword": "test", "context": "...test context..."}]',
            'last_modified': '2025-03-31',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'page_content': 'This is a test page content with some special characters: é,ñ,ü\nNew line test.'
        },
        {
            'url': 'https://test.army.mil/page2',
            'title': 'Test Page 2 with quotes "test"',
            'keywords_found': 'keyword2',
            'keyword_contexts': '[{"keyword": "keyword2", "context": "...another context..."}]',
            'last_modified': '2025-03-31',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'page_content': 'Another test page with "quotes" and line\nbreaks to test.'
        }
    ]
    
    # Add test data to scraper
    scraper.results = test_data
    
    print("\nTesting save functionality...")
    try:
        # Test normal save
        print("\n1. Testing normal save...")
        scraper.save_results()
        
        # Test backup save
        print("\n2. Testing backup save...")
        scraper.save_results(is_backup=True)
        
        # Test backup manager
        print("\n3. Testing backup manager...")
        backup_manager = BackupManager()
        print("\nListing available backups:")
        backups = backup_manager.list_backups()
        
        if backups:
            print("\n4. Testing backup restore...")
            latest_backup = os.path.basename(backups[0])
            print(f"Attempting to restore: {latest_backup}")
            backup_manager.restore_backup(latest_backup)
        
        # Verify files in results directory
        print("\nChecking saved files in results directory:")
        for root, dirs, files in os.walk(RESULTS_DIR_ABS):
            rel_path = os.path.relpath(root, RESULTS_DIR_ABS)
            if rel_path == '.':
                print(f"\nMain results directory:")
            else:
                print(f"\nSubdirectory: {rel_path}")
                
            for file in sorted(files):
                if file.startswith("army_results_"):
                    file_path = os.path.join(root, file)
                    size = os.path.getsize(file_path)
                    print(f"Found: {file} (size: {size:,} bytes)")
                
    except Exception as e:
        print(f"Error during save test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_save()
