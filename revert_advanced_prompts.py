#!/usr/bin/env python3
import os
import shutil
from pathlib import Path

def revert_files():
    """Revert all advanced prompts files from their backup copies."""
    
    base_dir = "/insight-fast/dnguyen/Q_Benchmark"
    advanced_prompts_dir = os.path.join(base_dir, "advanced_prompts")
    
    # Get all datasets
    datasets = []
    for item in os.listdir(advanced_prompts_dir):
        item_path = os.path.join(advanced_prompts_dir, item)
        if os.path.isdir(item_path):
            datasets.append(item)
    
    print(f"Found datasets: {datasets}")
    
    total_reverted = 0
    total_backups_found = 0
    
    for dataset in datasets:
        print(f"\n🔄 Processing dataset: {dataset}")
        
        dataset_dir = os.path.join(advanced_prompts_dir, dataset)
        
        # Find all backup files in this dataset directory
        backup_files = []
        for file in os.listdir(dataset_dir):
            if file.endswith('.json.backup'):
                backup_files.append(file)
        
        total_backups_found += len(backup_files)
        print(f"  Found backup files: {backup_files}")
        
        for backup_file in backup_files:
            # Get original filename by removing .backup extension
            original_file = backup_file.replace('.json.backup', '.json')
            
            backup_path = os.path.join(dataset_dir, backup_file)
            original_path = os.path.join(dataset_dir, original_file)
            
            print(f"  📝 Reverting {original_file}...")
            
            try:
                # Copy backup to original file
                shutil.copy2(backup_path, original_path)
                print(f"    ✅ Reverted {original_file} from backup")
                total_reverted += 1
                
                # Remove the backup file
                os.remove(backup_path)
                print(f"    🗑️  Removed backup file {backup_file}")
                
            except Exception as e:
                print(f"    ❌ Failed to revert {original_file}: {e}")
    
    print(f"\n🎉 Summary:")
    print(f"  Total backup files found: {total_backups_found}")
    print(f"  Total files reverted: {total_reverted}")
    print(f"  All advanced prompts have been reverted to their original state!")

if __name__ == "__main__":
    revert_files()