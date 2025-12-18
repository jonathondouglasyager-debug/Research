"""
DUPLICATE DETECTOR
Find and manage duplicate files and data across research
"""

import os
import sys
from pathlib import Path
import hashlib
import json
from datetime import datetime
from collections import defaultdict

# Import database manager
sys.path.append(str(Path(__file__).parent.parent / '_System'))
try:
    from database_manager import DatabaseManager
except ImportError:
    DatabaseManager = None

class DuplicateDetector:
    """
    Detect duplicate files, entities, and data across research infrastructure
    """
    
    def __init__(self, research_dir: str = None):
        """Initialize with research directory"""
        if research_dir is None:
            research_dir = r"C:\Users\jonat\Documents\Research"
        self.research_dir = Path(research_dir)
        
        # Initialize database manager if available
        if DatabaseManager:
            self.db_manager = DatabaseManager()
        else:
            self.db_manager = None
    
    def calculate_file_hash(self, filepath: str) -> str:
        """Calculate MD5 hash of file"""
        hash_md5 = hashlib.md5()
        
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            return None
    
    def scan_for_duplicate_files(self, directory: str = None) -> dict:
        """
        Scan directory for duplicate files based on content hash
        
        Args:
            directory: Directory to scan (defaults to research directory)
        
        Returns:
            Dictionary with duplicate files grouped by hash
        """
        if directory is None:
            directory = self.research_dir
        
        scan_path = Path(directory)
        
        if not scan_path.exists():
            return {'error': f'Directory not found: {directory}'}
        
        # Track files by hash
        file_hashes = defaultdict(list)
        
        # Skip system directories
        skip_dirs = {'_System', '_Automation', '_Intelligence', '_Generation', '__pycache__', '.git'}
        
        print(f"Scanning: {scan_path}")
        file_count = 0
        
        for root, dirs, files in os.walk(scan_path):
            # Filter out skip directories
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for filename in files:
                filepath = Path(root) / filename
                file_count += 1
                
                if file_count % 50 == 0:
                    print(f"  Scanned {file_count} files...")
                
                # Calculate hash
                file_hash = self.calculate_file_hash(str(filepath))
                
                if file_hash:
                    file_hashes[file_hash].append({
                        'path': str(filepath),
                        'size': filepath.stat().st_size,
                        'modified': datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()
                    })
        
        # Filter to only duplicates
        duplicates = {
            hash_val: files
            for hash_val, files in file_hashes.items()
            if len(files) > 1
        }
        
        return {
            'total_files_scanned': file_count,
            'unique_files': len(file_hashes),
            'duplicate_groups': len(duplicates),
            'duplicate_files_total': sum(len(files) - 1 for files in duplicates.values()),
            'duplicates': duplicates
        }
    
    def find_duplicate_entities(self) -> dict:
        """
        Find duplicate entities across all databases
        
        Returns:
            Dictionary with potential duplicate entities
        """
        if not self.db_manager:
            return {'error': 'Database manager not available'}
        
        # Get all databases
        databases = self.db_manager.list_databases()
        
        if not databases:
            return {'no_databases': True}
        
        # Track entities across databases
        entity_occurrences = defaultdict(list)
        
        for db_name, db_info in databases.items():
            df = db_info['dataframe']
            
            # Look for entity columns (common column names)
            entity_cols = [col for col in df.columns if any(
                keyword in col.lower() 
                for keyword in ['entity', 'name', 'actor', 'company', 'organization']
            )]
            
            if not entity_cols:
                continue
            
            # Extract entities from each column
            for col in entity_cols:
                unique_entities = df[col].dropna().unique()
                
                for entity in unique_entities:
                    entity_str = str(entity).strip()
                    if entity_str and len(entity_str) > 2:  # Skip very short names
                        entity_occurrences[entity_str.lower()].append({
                            'database': db_name,
                            'column': col,
                            'original_value': entity_str
                        })
        
        # Find potential duplicates (case-insensitive matches across databases)
        duplicates = {
            entity: occurrences
            for entity, occurrences in entity_occurrences.items()
            if len(occurrences) > 1
        }
        
        # Find similar names (within same database, different spellings)
        similar_names = self.find_similar_entity_names(entity_occurrences)
        
        return {
            'total_entities': len(entity_occurrences),
            'cross_database_duplicates': len(duplicates),
            'duplicates': duplicates,
            'similar_names': similar_names
        }
    
    def find_similar_entity_names(self, entity_occurrences: dict) -> list:
        """
        Find entities with similar names (potential typos or variations)
        
        Args:
            entity_occurrences: Dictionary of entity occurrences
        
        Returns:
            List of similar entity groups
        """
        similar_groups = []
        entities = list(entity_occurrences.keys())
        
        checked = set()
        
        for i, entity1 in enumerate(entities):
            if entity1 in checked:
                continue
            
            similar = [entity1]
            
            for entity2 in entities[i+1:]:
                if entity2 in checked:
                    continue
                
                # Simple similarity check (Levenshtein would be better but this works)
                similarity = self.calculate_string_similarity(entity1, entity2)
                
                if similarity > 0.8:  # 80% similar
                    similar.append(entity2)
                    checked.add(entity2)
            
            if len(similar) > 1:
                similar_groups.append({
                    'entities': similar,
                    'occurrences': [entity_occurrences[e] for e in similar]
                })
            
            checked.add(entity1)
        
        return similar_groups
    
    def calculate_string_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate similarity between two strings (0-1 scale)
        
        Simple implementation - Levenshtein would be better
        """
        # Tokenize and compare
        words1 = set(str1.split())
        words2 = set(str2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def suggest_cleanups(self, duplicate_scan_result: dict) -> list:
        """
        Suggest cleanup actions for duplicates
        
        Args:
            duplicate_scan_result: Result from scan_for_duplicate_files
        
        Returns:
            List of suggested actions
        """
        suggestions = []
        
        if 'duplicates' not in duplicate_scan_result:
            return suggestions
        
        for hash_val, files in duplicate_scan_result['duplicates'].items():
            # Sort by modification date (keep newest)
            files_sorted = sorted(files, key=lambda x: x['modified'], reverse=True)
            
            keep_file = files_sorted[0]
            delete_files = files_sorted[1:]
            
            suggestions.append({
                'hash': hash_val,
                'keep': keep_file,
                'delete': delete_files,
                'space_saved_mb': sum(f['size'] for f in delete_files) / (1024 * 1024)
            })
        
        return suggestions
    
    def execute_cleanup(self, suggestion: dict, confirm: bool = True) -> dict:
        """
        Execute a cleanup suggestion
        
        Args:
            suggestion: Cleanup suggestion from suggest_cleanups
            confirm: Ask for confirmation before deleting
        
        Returns:
            Dictionary with result
        """
        if confirm:
            print(f"\nKeep: {suggestion['keep']['path']}")
            print(f"Delete {len(suggestion['delete'])} files:")
            for f in suggestion['delete']:
                print(f"  - {f['path']}")
            
            response = input("\nProceed with deletion? (y/n): ").lower()
            if response != 'y':
                return {'status': 'cancelled'}
        
        deleted = []
        errors = []
        
        for file_info in suggestion['delete']:
            try:
                os.remove(file_info['path'])
                deleted.append(file_info['path'])
            except Exception as e:
                errors.append({
                    'file': file_info['path'],
                    'error': str(e)
                })
        
        return {
            'status': 'completed',
            'deleted': deleted,
            'errors': errors,
            'space_saved_mb': suggestion['space_saved_mb']
        }


def main():
    """Command-line interface"""
    detector = DuplicateDetector()
    
    if len(sys.argv) < 2:
        print("Duplicate Detector - Find and manage duplicate files and data")
        print()
        print("Usage:")
        print("  python duplicate_detector.py files [directory]")
        print("  python duplicate_detector.py entities")
        print("  python duplicate_detector.py cleanup [--auto]")
        print()
        print("Examples:")
        print('  python duplicate_detector.py files')
        print('  python duplicate_detector.py files "C:\\Research\\Active_Investigations"')
        print('  python duplicate_detector.py entities')
        print('  python duplicate_detector.py cleanup')
        return
    
    command = sys.argv[1].lower()
    
    if command == 'files':
        directory = sys.argv[2] if len(sys.argv) > 2 else None
        
        print("\n[SCAN] Scanning for duplicate files...")
        result = detector.scan_for_duplicate_files(directory)
        
        if 'error' in result:
            print(f"\n[FAIL] {result['error']}")
            return
        
        print(f"\n[OK] Scan complete!")
        print(f"Total files scanned: {result['total_files_scanned']}")
        print(f"Unique files: {result['unique_files']}")
        print(f"Duplicate groups: {result['duplicate_groups']}")
        print(f"Total duplicate files: {result['duplicate_files_total']}")
        
        if result['duplicates']:
            print(f"\n[DUPLICATES FOUND]")
            
            total_space = 0
            
            for hash_val, files in list(result['duplicates'].items())[:10]:  # Show first 10
                print(f"\n{len(files)} copies of:")
                for f in files:
                    size_mb = f['size'] / (1024 * 1024)
                    print(f"  - {f['path']}")
                    print(f"    Size: {size_mb:.2f} MB, Modified: {f['modified'][:10]}")
                
                # Calculate space wasted
                space_wasted = (len(files) - 1) * files[0]['size'] / (1024 * 1024)
                total_space += space_wasted
                print(f"  Space wasted: {space_wasted:.2f} MB")
            
            if len(result['duplicates']) > 10:
                print(f"\n... and {len(result['duplicates']) - 10} more duplicate groups")
            
            print(f"\n[SUMMARY] Total space wasted by duplicates: {total_space:.2f} MB")
            print("\nRun with 'cleanup' to remove duplicates")
        else:
            print("\n[OK] No duplicates found!")
    
    elif command == 'entities':
        print("\n[SCAN] Scanning for duplicate entities...")
        result = detector.find_duplicate_entities()
        
        if 'error' in result:
            print(f"\n[FAIL] {result['error']}")
            return
        
        if result.get('no_databases'):
            print("\n[INFO] No databases found")
            return
        
        print(f"\n[OK] Scan complete!")
        print(f"Total entities: {result['total_entities']}")
        print(f"Cross-database duplicates: {result['cross_database_duplicates']}")
        
        if result['duplicates']:
            print(f"\n[DUPLICATES FOUND]")
            
            # Show first 10
            for entity, occurrences in list(result['duplicates'].items())[:10]:
                print(f"\n'{entity}' appears in {len(occurrences)} places:")
                for occ in occurrences:
                    print(f"  - {occ['database']}.{occ['column']}: {occ['original_value']}")
        
        if result['similar_names']:
            print(f"\n[SIMILAR NAMES FOUND]")
            for group in result['similar_names'][:5]:  # Show first 5
                print(f"\nPotential variations:")
                for entity in group['entities']:
                    print(f"  - {entity}")
    
    elif command == 'cleanup':
        auto = '--auto' in sys.argv
        
        print("\n[SCAN] Scanning for duplicates...")
        scan_result = detector.scan_for_duplicate_files()
        
        if not scan_result.get('duplicates'):
            print("\n[OK] No duplicates to clean up!")
            return
        
        suggestions = detector.suggest_cleanups(scan_result)
        
        total_space = sum(s['space_saved_mb'] for s in suggestions)
        
        print(f"\n[OK] Found {len(suggestions)} cleanup opportunities")
        print(f"Potential space savings: {total_space:.2f} MB")
        
        if not auto:
            response = input("\nShow cleanup suggestions? (y/n): ").lower()
            if response != 'y':
                return
            
            for i, suggestion in enumerate(suggestions, 1):
                print(f"\n[{i}/{len(suggestions)}] Cleanup suggestion:")
                result = detector.execute_cleanup(suggestion, confirm=True)
                
                if result.get('status') == 'cancelled':
                    print("[SKIP] Cleanup cancelled")
                elif result.get('status') == 'completed':
                    print(f"[OK] Deleted {len(result['deleted'])} files")
                    print(f"    Saved {result['space_saved_mb']:.2f} MB")
                    
                    if result.get('errors'):
                        print(f"[WARN] {len(result['errors'])} errors occurred")
        else:
            print("\n[AUTO] Automatic cleanup mode")
            response = input(f"Delete {scan_result['duplicate_files_total']} duplicate files? (y/n): ").lower()
            
            if response != 'y':
                print("[INFO] Cleanup cancelled")
                return
            
            total_deleted = 0
            total_saved = 0
            
            for suggestion in suggestions:
                result = detector.execute_cleanup(suggestion, confirm=False)
                if result.get('status') == 'completed':
                    total_deleted += len(result['deleted'])
                    total_saved += result['space_saved_mb']
            
            print(f"\n[SUCCESS] Cleanup complete!")
            print(f"Deleted: {total_deleted} files")
            print(f"Space saved: {total_saved:.2f} MB")
    
    else:
        print(f"Unknown command: {command}")
        print("Valid commands: files, entities, cleanup")


if __name__ == '__main__':
    main()
