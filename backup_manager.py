import os
import shutil
import glob
import gzip
import time
from datetime import datetime
from config import RESULTS_DIR_ABS, SETTINGS

class BackupManager:
    """Manages backup files for the scraper results."""
    
    def __init__(self):
        self.backup_dir = os.path.join(RESULTS_DIR_ABS, 'backups')
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_backup(self, file_path):
        """Create a backup of a file."""
        if not SETTINGS['BACKUP_FILES']:
            return
            
        if not os.path.exists(file_path):
            print(f"Warning: Cannot backup non-existent file: {file_path}")
            return
            
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.basename(file_path)
        backup_name = f"{os.path.splitext(filename)[0]}_{timestamp}{os.path.splitext(filename)[1]}"
        
        if SETTINGS['COMPRESS_BACKUPS']:
            backup_name += '.gz'
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            with open(file_path, 'rb') as f_in:
                with gzip.open(backup_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        else:
            backup_path = os.path.join(self.backup_dir, backup_name)
            shutil.copy2(file_path, backup_path)
            
        print(f"✓ Created backup: {backup_name}")
        self._cleanup_old_backups()
    
    def _cleanup_old_backups(self):
        """Remove old backups if we exceed the maximum number."""
        if not SETTINGS['MAX_BACKUPS']:
            return
            
        pattern = os.path.join(self.backup_dir, 'army_results_*')
        backups = glob.glob(pattern)
        
        if len(backups) > SETTINGS['MAX_BACKUPS']:
            # Sort by modification time, oldest first
            backups.sort(key=os.path.getmtime)
            
            # Remove oldest backups
            for backup in backups[:-SETTINGS['MAX_BACKUPS']]:
                try:
                    os.remove(backup)
                    print(f"✓ Removed old backup: {os.path.basename(backup)}")
                except Exception as e:
                    print(f"✗ Error removing old backup {backup}: {str(e)}")
    
    def restore_backup(self, backup_file):
        """Restore a file from backup."""
        backup_path = os.path.join(self.backup_dir, backup_file)
        if not os.path.exists(backup_path):
            print(f"Error: Backup file not found: {backup_file}")
            return False
            
        # Determine target filename
        if backup_file.endswith('.gz'):
            target_file = os.path.splitext(os.path.splitext(backup_file)[0])[0]
        else:
            target_file = os.path.splitext(backup_file)[0]
            
        # Remove timestamp from filename
        target_file = '_'.join(target_file.split('_')[:-1]) + os.path.splitext(backup_file)[1]
        target_path = os.path.join(RESULTS_DIR_ABS, target_file)
        
        try:
            if backup_file.endswith('.gz'):
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(target_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                shutil.copy2(backup_path, target_path)
                
            print(f"✓ Restored {target_file} from backup")
            return True
        except Exception as e:
            print(f"✗ Error restoring backup: {str(e)}")
            return False
    
    def list_backups(self):
        """List all available backups."""
        pattern = os.path.join(self.backup_dir, 'army_results_*')
        backups = glob.glob(pattern)
        
        if not backups:
            print("No backups found.")
            return []
            
        print("\nAvailable backups:")
        backups.sort(key=os.path.getmtime, reverse=True)
        
        for backup in backups:
            name = os.path.basename(backup)
            size = os.path.getsize(backup)
            mtime = datetime.fromtimestamp(os.path.getmtime(backup))
            
            print(f"- {name}")
            print(f"  Size: {size / 1024:.2f} KB")
            print(f"  Modified: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            
        return backups
