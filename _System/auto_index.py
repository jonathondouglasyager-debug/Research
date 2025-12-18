"""
ENHANCED AUTO-INDEX SYSTEM
Automatically maintains INDEX.html with intelligent categorization
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import json

# Import our other systems
from file_intelligence import FileIntelligence
from database_manager import DatabaseManager
from source_tracker import SourceTracker

class AutoIndex:
    """
    Enhanced auto-indexing system that integrates all intelligence
    """
    
    def __init__(self, research_dir: str = None):
        """Initialize with research directory"""
        if research_dir is None:
            research_dir = r"C:\Users\jonat\Documents\Research"
        self.research_dir = Path(research_dir)
        
        self.index_file = self.research_dir / 'INDEX.html'
        
        # Initialize intelligence systems
        self.file_intel = FileIntelligence(str(self.research_dir))
        self.db_manager = DatabaseManager(str(self.research_dir))
        self.source_tracker = SourceTracker(str(self.research_dir))
        
        # State file to track what's been indexed
        self.state_file = self.research_dir / '_System' / 'index_state.json'
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.state = self.load_state()
    
    def load_state(self) -> Dict:
        """Load indexing state"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except:
                return {'indexed_files': {}, 'last_scan': None}
        return {'indexed_files': {}, 'last_scan': None}
    
    def save_state(self):
        """Save indexing state"""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def scan_for_new_files(self) -> List[Path]:
        """
        Scan research directory for new files not yet indexed
        """
        new_files = []
        
        # Skip these directories
        skip_dirs = {'_System', '_Automation', '_Intelligence', '_Generation', 
                    '__pycache__', '.git', 'node_modules'}
        
        for item in self.research_dir.rglob('*'):
            # Skip directories in skip list
            if any(skip_dir in item.parts for skip_dir in skip_dirs):
                continue
            
            # Skip hidden files
            if item.name.startswith('.') or item.name.startswith('~'):
                continue
            
            # Only process files
            if not item.is_file():
                continue
            
            # Check if already indexed
            file_key = str(item.relative_to(self.research_dir))
            
            if file_key not in self.state['indexed_files']:
                new_files.append(item)
            else:
                # Check if file was modified since last index
                last_indexed = self.state['indexed_files'][file_key].get('indexed_date')
                file_modified = datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                
                if file_modified > last_indexed:
                    new_files.append(item)
        
        return new_files
    
    def process_file(self, filepath: Path) -> Dict:
        """
        Process a file with full intelligence analysis
        """
        print(f"Processing: {filepath.name}")
        
        # Run file intelligence
        analysis = self.file_intel.analyze_file(str(filepath))
        
        # Register as source
        source_id = self.source_tracker.register_source(
            str(filepath),
            metadata={
                'title': filepath.name,
                'type': analysis['file_info'].get('category', 'unknown')
            }
        )
        
        # Determine investigation category
        investigations = analysis.get('suggested_investigations', [])
        
        if not investigations:
            # Default to folder structure
            relative_path = filepath.relative_to(self.research_dir)
            if 'Active_Investigations' in relative_path.parts:
                # Extract investigation from folder name
                idx = relative_path.parts.index('Active_Investigations')
                if len(relative_path.parts) > idx + 1:
                    folder = relative_path.parts[idx + 1]
                    investigations = [folder.lower().replace(' ', '_')]
        
        result = {
            'filepath': str(filepath),
            'filename': filepath.name,
            'relative_path': str(filepath.relative_to(self.research_dir)),
            'analysis': analysis,
            'source_id': source_id,
            'investigations': investigations,
            'processed_date': datetime.now().isoformat()
        }
        
        # Update state
        file_key = str(filepath.relative_to(self.research_dir))
        self.state['indexed_files'][file_key] = {
            'indexed_date': datetime.now().isoformat(),
            'source_id': source_id,
            'investigations': investigations
        }
        
        return result
    
    def update_index_html(self, new_file: Path, investigations: List[str]):
        """
        Add new file to INDEX.html in appropriate section(s)
        """
        if not self.index_file.exists():
            print(f"Warning: INDEX.html not found at {self.index_file}")
            return
        
        # Read current INDEX.html
        with open(self.index_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Determine file type for color coding
        extension = new_file.suffix.lower()
        
        if extension == '.csv':
            link_class = 'csv-link'
            icon = '📊'
        elif extension == '.md':
            link_class = 'md-link'
            icon = '📝'
        elif extension == '.html':
            link_class = 'html-link'
            icon = '🌐'
        elif extension in ['.pdf', '.docx', '.doc']:
            link_class = 'other-link'
            icon = '📄'
        elif extension == '.py':
            link_class = 'other-link'
            icon = '🐍'
        else:
            link_class = 'other-link'
            icon = '📎'
        
        # Build file link
        file_url = f"file:///{str(new_file.absolute()).replace(chr(92), '/')}"
        link_html = f'                        <a href="{file_url}" class="{link_class}" data-type="{extension[1:]}">{icon} {new_file.name}</a>'
        
        # Try to find appropriate section in INDEX.html
        # This is simplified - in production we'd parse HTML properly
        
        # For now, just update file count stats
        import re
        
        # Update total files count
        html_content = re.sub(
            r'<span class="stat-number">(\d+)</span>\s*<span class="stat-label">Total Files</span>',
            lambda m: f'<span class="stat-number">{int(m.group(1)) + 1}</span>\n                <span class="stat-label">Total Files</span>',
            html_content
        )
        
        # Update last updated date
        html_content = re.sub(
            r'Last Updated: [^|]+',
            f'Last Updated: {datetime.now().strftime("%B %d, %Y")}',
            html_content
        )
        
        # Write back
        with open(self.index_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"  [OK] Updated INDEX.html")
    
    def run_full_scan(self) -> Dict:
        """
        Run complete scan and update INDEX
        """
        print("\n=== AUTO-INDEX SCAN ===\n")
        
        # Find new files
        new_files = self.scan_for_new_files()
        
        if not new_files:
            print("No new files found")
            self.state['last_scan'] = datetime.now().isoformat()
            self.save_state()
            return {'new_files': 0, 'processed': 0}
        
        print(f"Found {len(new_files)} new/modified files\n")
        
        processed = []
        errors = []
        
        for filepath in new_files:
            try:
                result = self.process_file(filepath)
                processed.append(result)
                
                # Update INDEX.html
                self.update_index_html(filepath, result['investigations'])
                
            except Exception as e:
                errors.append({
                    'file': str(filepath),
                    'error': str(e)
                })
                print(f"  [FAIL] Error processing {filepath.name}: {e}")
        
        # Save state
        self.state['last_scan'] = datetime.now().isoformat()
        self.save_state()
        
        print(f"\n[OK] Processed {len(processed)} files")
        
        if errors:
            print(f"[FAIL] {len(errors)} errors")
        
        return {
            'new_files': len(new_files),
            'processed': len(processed),
            'errors': errors
        }
    
    def get_statistics(self) -> Dict:
        """Get auto-index statistics"""
        total_indexed = len(self.state['indexed_files'])
        last_scan = self.state.get('last_scan', 'Never')
        
        # Count by investigation
        by_investigation = {}
        for file_data in self.state['indexed_files'].values():
            for inv in file_data.get('investigations', []):
                by_investigation[inv] = by_investigation.get(inv, 0) + 1
        
        return {
            'total_indexed': total_indexed,
            'last_scan': last_scan,
            'by_investigation': by_investigation,
            'db_stats': self.db_manager.get_statistics(),
            'source_stats': self.source_tracker.get_statistics()
        }


# Command-line interface
if __name__ == '__main__':
    auto_index = AutoIndex()
    
    if len(sys.argv) == 1 or sys.argv[1] == 'scan':
        # Run full scan
        results = auto_index.run_full_scan()
        
        if results['errors']:
            print("\nErrors:")
            for error in results['errors']:
                print(f"  {error['file']}: {error['error']}")
    
    elif sys.argv[1] == 'stats':
        # Show statistics
        print("\n=== AUTO-INDEX STATISTICS ===\n")
        
        stats = auto_index.get_statistics()
        
        print(f"Total indexed files: {stats['total_indexed']}")
        print(f"Last scan: {stats['last_scan']}")
        
        if stats['by_investigation']:
            print("\nBy investigation:")
            for inv, count in sorted(stats['by_investigation'].items()):
                print(f"  {inv}: {count} files")
        
        print("\nDatabase Statistics:")
        db_stats = stats['db_stats']
        print(f"  Databases: {db_stats['total_databases']}")
        print(f"  Total rows: {db_stats['total_rows']}")
        
        print("\nSource Statistics:")
        src_stats = stats['source_stats']
        print(f"  Sources: {src_stats['total_sources']}")
        print(f"  Claims: {src_stats['total_claims']}")
        print(f"  Evidence chains: {src_stats['evidence_chains']}")
    
    elif sys.argv[1] == 'process':
        if len(sys.argv) < 3:
            print("Usage: python auto_index.py process <filepath>")
            sys.exit(1)
        
        filepath = Path(sys.argv[2])
        
        if not filepath.exists():
            print(f"Error: File not found: {filepath}")
            sys.exit(1)
        
        result = auto_index.process_file(filepath)
        print(json.dumps(result, indent=2))
    
    else:
        print("Unknown command")
        print("\nAvailable commands:")
        print("  scan              - Scan for new files and update INDEX")
        print("  stats             - Show statistics")
        print("  process <file>    - Process a specific file")
