"""
VERSION CONTROL
Track changes to research directory over time
"""

import os
import sys
from pathlib import Path
import json
import hashlib
import shutil
from datetime import datetime
from collections import defaultdict

class VersionControl:
    """
    Simple version control system for research directory
    """
    
    def __init__(self, research_dir: str = None):
        """Initialize with research directory"""
        if research_dir is None:
            research_dir = r"C:\Users\jonat\Documents\Research"
        self.research_dir = Path(research_dir)
        self.versions_dir = self.research_dir / '_System' / 'versions'
        self.versions_dir.mkdir(parents=True, exist_ok=True)
        
        self.state_file = self.versions_dir / 'version_state.json'
        self.load_state()
    
    def load_state(self):
        """Load version control state"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                self.state = json.load(f)
        else:
            self.state = {
                'snapshots': [],
                'current_snapshot': None,
                'total_snapshots': 0
            }
    
    def save_state(self):
        """Save version control state"""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def calculate_directory_hash(self, directory: Path = None) -> dict:
        """
        Calculate hash for all files in directory
        
        Args:
            directory: Directory to hash (defaults to research_dir)
        
        Returns:
            Dictionary mapping file paths to hashes
        """
        if directory is None:
            directory = self.research_dir
        
        file_hashes = {}
        
        # Skip system directories
        skip_dirs = {'_System', '__pycache__', '.git', 'versions'}
        
        for root, dirs, files in os.walk(directory):
            # Filter out skip directories
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for filename in files:
                filepath = Path(root) / filename
                rel_path = filepath.relative_to(directory)
                
                # Calculate hash
                hash_md5 = hashlib.md5()
                try:
                    with open(filepath, 'rb') as f:
                        for chunk in iter(lambda: f.read(4096), b""):
                            hash_md5.update(chunk)
                    
                    file_hashes[str(rel_path)] = {
                        'hash': hash_md5.hexdigest(),
                        'size': filepath.stat().st_size,
                        'modified': datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()
                    }
                except Exception as e:
                    file_hashes[str(rel_path)] = {
                        'error': str(e)
                    }
        
        return file_hashes
    
    def create_snapshot(self, description: str = None) -> dict:
        """
        Create a snapshot of current research state
        
        Args:
            description: Optional description of snapshot
        
        Returns:
            Dictionary with snapshot info
        """
        snapshot_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        snapshot_dir = self.versions_dir / snapshot_id
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        
        # Calculate current state
        print("Calculating directory state...")
        file_hashes = self.calculate_directory_hash()
        
        # Save snapshot manifest
        manifest = {
            'snapshot_id': snapshot_id,
            'timestamp': datetime.now().isoformat(),
            'description': description or f'Snapshot {snapshot_id}',
            'file_count': len(file_hashes),
            'total_size': sum(f.get('size', 0) for f in file_hashes.values()),
            'files': file_hashes
        }
        
        manifest_path = snapshot_dir / 'manifest.json'
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        # Update state
        self.state['snapshots'].append({
            'id': snapshot_id,
            'timestamp': manifest['timestamp'],
            'description': manifest['description'],
            'file_count': manifest['file_count'],
            'total_size_mb': manifest['total_size'] / (1024 * 1024)
        })
        self.state['current_snapshot'] = snapshot_id
        self.state['total_snapshots'] += 1
        self.save_state()
        
        return manifest
    
    def compare_snapshots(self, snapshot1_id: str, snapshot2_id: str) -> dict:
        """
        Compare two snapshots
        
        Args:
            snapshot1_id: First snapshot ID
            snapshot2_id: Second snapshot ID
        
        Returns:
            Dictionary with differences
        """
        # Load manifests
        manifest1_path = self.versions_dir / snapshot1_id / 'manifest.json'
        manifest2_path = self.versions_dir / snapshot2_id / 'manifest.json'
        
        if not manifest1_path.exists():
            return {'error': f'Snapshot not found: {snapshot1_id}'}
        if not manifest2_path.exists():
            return {'error': f'Snapshot not found: {snapshot2_id}'}
        
        with open(manifest1_path, 'r') as f:
            manifest1 = json.load(f)
        with open(manifest2_path, 'r') as f:
            manifest2 = json.load(f)
        
        files1 = manifest1['files']
        files2 = manifest2['files']
        
        # Find differences
        added = []
        deleted = []
        modified = []
        
        for filepath, info2 in files2.items():
            if filepath not in files1:
                added.append(filepath)
            elif files1[filepath].get('hash') != info2.get('hash'):
                modified.append({
                    'path': filepath,
                    'old_size': files1[filepath].get('size', 0),
                    'new_size': info2.get('size', 0)
                })
        
        for filepath in files1:
            if filepath not in files2:
                deleted.append(filepath)
        
        return {
            'snapshot1': snapshot1_id,
            'snapshot2': snapshot2_id,
            'added': added,
            'deleted': deleted,
            'modified': modified,
            'total_changes': len(added) + len(deleted) + len(modified)
        }
    
    def get_changes_since(self, snapshot_id: str) -> dict:
        """
        Get all changes since a specific snapshot
        
        Args:
            snapshot_id: Snapshot ID to compare from
        
        Returns:
            Dictionary with changes
        """
        # Load old manifest
        manifest_path = self.versions_dir / snapshot_id / 'manifest.json'
        
        if not manifest_path.exists():
            return {'error': f'Snapshot not found: {snapshot_id}'}
        
        with open(manifest_path, 'r') as f:
            old_manifest = json.load(f)
        
        # Get current state
        current_files = self.calculate_directory_hash()
        old_files = old_manifest['files']
        
        # Find differences
        added = []
        deleted = []
        modified = []
        
        for filepath, info in current_files.items():
            if filepath not in old_files:
                added.append({
                    'path': filepath,
                    'size': info.get('size', 0),
                    'modified': info.get('modified')
                })
            elif old_files[filepath].get('hash') != info.get('hash'):
                modified.append({
                    'path': filepath,
                    'old_size': old_files[filepath].get('size', 0),
                    'new_size': info.get('size', 0),
                    'modified': info.get('modified')
                })
        
        for filepath in old_files:
            if filepath not in current_files:
                deleted.append({
                    'path': filepath,
                    'size': old_files[filepath].get('size', 0)
                })
        
        return {
            'snapshot_id': snapshot_id,
            'snapshot_date': old_manifest['timestamp'],
            'current_date': datetime.now().isoformat(),
            'added': added,
            'deleted': deleted,
            'modified': modified,
            'total_changes': len(added) + len(deleted) + len(modified)
        }
    
    def list_snapshots(self) -> list:
        """List all snapshots"""
        return self.state.get('snapshots', [])
    
    def get_snapshot_info(self, snapshot_id: str) -> dict:
        """Get detailed info about a snapshot"""
        manifest_path = self.versions_dir / snapshot_id / 'manifest.json'
        
        if not manifest_path.exists():
            return {'error': f'Snapshot not found: {snapshot_id}'}
        
        with open(manifest_path, 'r') as f:
            return json.load(f)


def main():
    """Command-line interface"""
    vc = VersionControl()
    
    if len(sys.argv) < 2:
        print("Version Control - Track research changes over time")
        print()
        print("Usage:")
        print('  python version_control.py snapshot [description]')
        print('  python version_control.py list')
        print('  python version_control.py compare <id1> <id2>')
        print('  python version_control.py changes <snapshot_id>')
        print('  python version_control.py info <snapshot_id>')
        print()
        print("Examples:")
        print('  python version_control.py snapshot "Before major investigation"')
        print('  python version_control.py list')
        print('  python version_control.py compare 20251210_140000 20251210_150000')
        print('  python version_control.py changes 20251210_140000')
        return
    
    command = sys.argv[1].lower()
    
    if command == 'snapshot':
        description = ' '.join(sys.argv[2:]) if len(sys.argv) > 2 else None
        
        print("\n[SNAPSHOT] Creating snapshot...")
        result = vc.create_snapshot(description)
        
        print(f"\n[OK] Snapshot created: {result['snapshot_id']}")
        print(f"Description: {result['description']}")
        print(f"Files: {result['file_count']}")
        print(f"Total size: {result['total_size'] / (1024 * 1024):.2f} MB")
        print(f"Timestamp: {result['timestamp']}")
    
    elif command == 'list':
        snapshots = vc.list_snapshots()
        
        if not snapshots:
            print("\n[INFO] No snapshots found")
            print('Create one with: python version_control.py snapshot "Description"')
            return
        
        print(f"\n[OK] Found {len(snapshots)} snapshots:")
        print()
        
        for snap in sorted(snapshots, key=lambda x: x['timestamp'], reverse=True):
            print(f"ID: {snap['id']}")
            print(f"  Date: {snap['timestamp'][:19]}")
            print(f"  Description: {snap['description']}")
            print(f"  Files: {snap['file_count']}")
            print(f"  Size: {snap['total_size_mb']:.2f} MB")
            print()
    
    elif command == 'compare':
        if len(sys.argv) < 4:
            print("Error: Two snapshot IDs required")
            print('Usage: python version_control.py compare <id1> <id2>')
            return
        
        id1 = sys.argv[2]
        id2 = sys.argv[3]
        
        print(f"\n[COMPARE] Comparing snapshots...")
        result = vc.compare_snapshots(id1, id2)
        
        if 'error' in result:
            print(f"\n[FAIL] {result['error']}")
            return
        
        print(f"\n[OK] Comparison complete")
        print(f"From: {result['snapshot1']}")
        print(f"To: {result['snapshot2']}")
        print(f"Total changes: {result['total_changes']}")
        print()
        
        if result['added']:
            print(f"[ADDED] {len(result['added'])} files:")
            for filepath in result['added'][:10]:
                print(f"  + {filepath}")
            if len(result['added']) > 10:
                print(f"  ... and {len(result['added']) - 10} more")
            print()
        
        if result['deleted']:
            print(f"[DELETED] {len(result['deleted'])} files:")
            for filepath in result['deleted'][:10]:
                print(f"  - {filepath}")
            if len(result['deleted']) > 10:
                print(f"  ... and {len(result['deleted']) - 10} more")
            print()
        
        if result['modified']:
            print(f"[MODIFIED] {len(result['modified'])} files:")
            for file_info in result['modified'][:10]:
                old_mb = file_info['old_size'] / (1024 * 1024)
                new_mb = file_info['new_size'] / (1024 * 1024)
                print(f"  ~ {file_info['path']}")
                print(f"    Size: {old_mb:.2f} MB -> {new_mb:.2f} MB")
            if len(result['modified']) > 10:
                print(f"  ... and {len(result['modified']) - 10} more")
    
    elif command == 'changes':
        if len(sys.argv) < 3:
            print("Error: Snapshot ID required")
            print('Usage: python version_control.py changes <snapshot_id>')
            return
        
        snapshot_id = sys.argv[2]
        
        print(f"\n[CHANGES] Getting changes since {snapshot_id}...")
        result = vc.get_changes_since(snapshot_id)
        
        if 'error' in result:
            print(f"\n[FAIL] {result['error']}")
            return
        
        print(f"\n[OK] Changes found")
        print(f"Since: {result['snapshot_date'][:19]}")
        print(f"Now: {result['current_date'][:19]}")
        print(f"Total changes: {result['total_changes']}")
        print()
        
        if result['added']:
            print(f"[ADDED] {len(result['added'])} files:")
            for file_info in result['added'][:10]:
                size_mb = file_info['size'] / (1024 * 1024)
                print(f"  + {file_info['path']} ({size_mb:.2f} MB)")
            if len(result['added']) > 10:
                print(f"  ... and {len(result['added']) - 10} more")
            print()
        
        if result['deleted']:
            print(f"[DELETED] {len(result['deleted'])} files:")
            for file_info in result['deleted'][:10]:
                size_mb = file_info['size'] / (1024 * 1024)
                print(f"  - {file_info['path']} ({size_mb:.2f} MB)")
            if len(result['deleted']) > 10:
                print(f"  ... and {len(result['deleted']) - 10} more")
            print()
        
        if result['modified']:
            print(f"[MODIFIED] {len(result['modified'])} files:")
            for file_info in result['modified'][:10]:
                old_mb = file_info['old_size'] / (1024 * 1024)
                new_mb = file_info['new_size'] / (1024 * 1024)
                print(f"  ~ {file_info['path']}")
                print(f"    {old_mb:.2f} MB -> {new_mb:.2f} MB")
            if len(result['modified']) > 10:
                print(f"  ... and {len(result['modified']) - 10} more")
    
    elif command == 'info':
        if len(sys.argv) < 3:
            print("Error: Snapshot ID required")
            print('Usage: python version_control.py info <snapshot_id>')
            return
        
        snapshot_id = sys.argv[2]
        
        result = vc.get_snapshot_info(snapshot_id)
        
        if 'error' in result:
            print(f"\n[FAIL] {result['error']}")
            return
        
        print(f"\n[OK] Snapshot information")
        print(f"ID: {result['snapshot_id']}")
        print(f"Timestamp: {result['timestamp']}")
        print(f"Description: {result['description']}")
        print(f"Files: {result['file_count']}")
        print(f"Total size: {result['total_size'] / (1024 * 1024):.2f} MB")
    
    else:
        print(f"Unknown command: {command}")
        print("Valid commands: snapshot, list, compare, changes, info")


if __name__ == '__main__':
    main()
