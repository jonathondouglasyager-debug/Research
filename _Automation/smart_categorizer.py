"""
SMART FILE CATEGORIZER
Automatically sort files into correct investigation folders
"""

import os
import sys
from pathlib import Path
import json
from datetime import datetime
import shutil

# Import our file intelligence system
sys.path.append(str(Path(__file__).parent.parent / '_System'))
from file_intelligence import FileIntelligence

class SmartCategorizer:
    """
    Automatically categorize files into investigations based on content
    """
    
    def __init__(self, research_dir: str = None):
        """Initialize with research directory"""
        if research_dir is None:
            research_dir = r"C:\Users\jonat\Documents\Research"
        self.research_dir = Path(research_dir)
        self.active_investigations_dir = self.research_dir / 'Active_Investigations'
        self.uncategorized_dir = self.research_dir / 'Uncategorized_Files'
        
        # Initialize file intelligence
        self.file_intel = FileIntelligence()
        
        # Load investigation keywords
        self.load_investigation_keywords()
    
    def load_investigation_keywords(self):
        """Load keywords for each investigation"""
        self.investigation_keywords = {}
        
        if not self.active_investigations_dir.exists():
            return
        
        for inv_folder in self.active_investigations_dir.iterdir():
            if inv_folder.is_dir() and not inv_folder.name.startswith('_'):
                # Try to load metadata
                metadata_path = inv_folder / 'investigation_metadata.json'
                if metadata_path.exists():
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                    keywords = metadata.get('keywords', [])
                else:
                    # Generate keywords from folder name
                    keywords = [word.lower() for word in inv_folder.name.replace('_', ' ').split()]
                
                self.investigation_keywords[inv_folder.name] = keywords
    
    def analyze_file_for_categorization(self, filepath: str) -> dict:
        """
        Analyze file and suggest investigations
        
        Args:
            filepath: Path to file to analyze
        
        Returns:
            Dictionary with analysis results and suggestions
        """
        # Analyze file
        analysis = self.file_intel.analyze_file(filepath)
        
        if not analysis['metadata']['success']:
            return {
                'error': 'Could not analyze file',
                'filepath': filepath
            }
        
        # Extract relevant content
        entities = analysis['metadata'].get('found_entities', [])
        potential_entities = analysis['metadata'].get('potential_entities', [])
        all_entities = entities + potential_entities
        
        # Convert to lowercase for matching
        content_keywords = [e.lower() for e in all_entities]
        
        # Also check suggested investigations from file intelligence
        suggested_invs = analysis.get('suggested_investigations', [])
        
        # Score each investigation
        scores = {}
        for inv_name, inv_keywords in self.investigation_keywords.items():
            score = 0
            matches = []
            
            # Check keyword matches
            for keyword in inv_keywords:
                for content_keyword in content_keywords:
                    if keyword in content_keyword or content_keyword in keyword:
                        score += 1
                        matches.append(keyword)
            
            # Bonus for suggested investigations
            if inv_name.lower().replace('_', ' ') in [s.lower() for s in suggested_invs]:
                score += 5
            
            if score > 0:
                scores[inv_name] = {
                    'score': score,
                    'matches': list(set(matches))
                }
        
        # Sort by score
        sorted_invs = sorted(scores.items(), key=lambda x: x[1]['score'], reverse=True)
        
        return {
            'filepath': filepath,
            'filename': Path(filepath).name,
            'entities_found': all_entities,
            'suggested_investigations': [
                {
                    'investigation': inv_name,
                    'score': data['score'],
                    'matches': data['matches']
                }
                for inv_name, data in sorted_invs[:5]  # Top 5
            ],
            'analysis': analysis
        }
    
    def categorize_file(self, filepath: str, investigation_name: str, 
                       subfolder: str = 'Evidence', copy: bool = True) -> dict:
        """
        Move or copy file to investigation folder
        
        Args:
            filepath: Source file path
            investigation_name: Target investigation
            subfolder: Subfolder within investigation (Evidence, Timeline, Analysis)
            copy: If True, copy file; if False, move file
        
        Returns:
            Dictionary with result
        """
        source_path = Path(filepath)
        
        if not source_path.exists():
            return {'error': f'File not found: {filepath}'}
        
        # Find investigation folder
        inv_folder = self.active_investigations_dir / investigation_name
        
        if not inv_folder.exists():
            return {'error': f'Investigation not found: {investigation_name}'}
        
        # Determine target folder
        target_folder = inv_folder / subfolder
        target_folder.mkdir(parents=True, exist_ok=True)
        
        # Determine target path
        target_path = target_folder / source_path.name
        
        # Handle duplicate names
        if target_path.exists():
            base = target_path.stem
            ext = target_path.suffix
            counter = 1
            while target_path.exists():
                target_path = target_folder / f"{base}_{counter}{ext}"
                counter += 1
        
        # Copy or move
        try:
            if copy:
                shutil.copy2(source_path, target_path)
                action = 'copied'
            else:
                shutil.move(source_path, target_path)
                action = 'moved'
            
            return {
                'success': True,
                'action': action,
                'source': str(source_path),
                'destination': str(target_path),
                'investigation': investigation_name,
                'subfolder': subfolder
            }
        except Exception as e:
            return {'error': f'Failed to {action} file: {e}'}
    
    def auto_categorize_file(self, filepath: str, threshold: int = 3, 
                            copy: bool = True, interactive: bool = True) -> dict:
        """
        Automatically categorize file based on content
        
        Args:
            filepath: File to categorize
            threshold: Minimum score to auto-categorize (default 3)
            copy: Copy instead of move (default True)
            interactive: Ask for confirmation (default True)
        
        Returns:
            Dictionary with result
        """
        # Analyze file
        analysis = self.analyze_file_for_categorization(filepath)
        
        if 'error' in analysis:
            return analysis
        
        if not analysis['suggested_investigations']:
            return {
                'filepath': filepath,
                'status': 'no_match',
                'message': 'No matching investigations found'
            }
        
        # Get top suggestion
        top_suggestion = analysis['suggested_investigations'][0]
        
        if top_suggestion['score'] < threshold:
            return {
                'filepath': filepath,
                'status': 'low_confidence',
                'score': top_suggestion['score'],
                'threshold': threshold,
                'message': f"Confidence too low (score: {top_suggestion['score']}, threshold: {threshold})",
                'suggestions': analysis['suggested_investigations']
            }
        
        # Auto-categorize or ask
        if interactive:
            print(f"\nFile: {Path(filepath).name}")
            print(f"Top match: {top_suggestion['investigation']} (score: {top_suggestion['score']})")
            print(f"Matching keywords: {', '.join(top_suggestion['matches'])}")
            response = input("\nCategorize to this investigation? (y/n/other): ").lower()
            
            if response == 'n':
                return {'status': 'skipped', 'filepath': filepath}
            elif response == 'other':
                print("\nAvailable investigations:")
                for i, sug in enumerate(analysis['suggested_investigations'], 1):
                    print(f"  {i}. {sug['investigation']} (score: {sug['score']})")
                choice = input("\nEnter number: ")
                try:
                    idx = int(choice) - 1
                    top_suggestion = analysis['suggested_investigations'][idx]
                except:
                    return {'status': 'cancelled', 'filepath': filepath}
        
        # Categorize
        result = self.categorize_file(
            filepath,
            top_suggestion['investigation'],
            copy=copy
        )
        
        if result.get('success'):
            result['analysis'] = analysis
        
        return result
    
    def batch_categorize(self, directory: str, copy: bool = True, 
                        threshold: int = 3, interactive: bool = True) -> dict:
        """
        Categorize all files in a directory
        
        Args:
            directory: Directory to scan
            copy: Copy instead of move
            threshold: Minimum score for auto-categorization
            interactive: Ask for confirmation
        
        Returns:
            Dictionary with results
        """
        dir_path = Path(directory)
        
        if not dir_path.exists():
            return {'error': f'Directory not found: {directory}'}
        
        results = {
            'categorized': [],
            'skipped': [],
            'errors': [],
            'no_match': []
        }
        
        # Get all files
        files = [f for f in dir_path.iterdir() if f.is_file()]
        
        print(f"\nFound {len(files)} files to categorize")
        
        for filepath in files:
            print(f"\n{'='*60}")
            result = self.auto_categorize_file(
                str(filepath),
                threshold=threshold,
                copy=copy,
                interactive=interactive
            )
            
            status = result.get('status', 'error')
            
            if result.get('success'):
                results['categorized'].append(result)
                print(f"[OK] Categorized to {result['investigation']}")
            elif status == 'skipped':
                results['skipped'].append(result)
                print("[SKIP] File skipped")
            elif status == 'no_match':
                results['no_match'].append(result)
                print("[INFO] No matching investigations")
            else:
                results['errors'].append(result)
                if 'error' in result:
                    print(f"[FAIL] {result['error']}")
                else:
                    print(f"[INFO] {result.get('message', 'Unknown status')}")
        
        return results


def main():
    """Command-line interface"""
    categorizer = SmartCategorizer()
    
    if len(sys.argv) < 2:
        print("Smart File Categorizer - Automatically sort files into investigations")
        print()
        print("Usage:")
        print("  python smart_categorizer.py analyze <filepath>")
        print("  python smart_categorizer.py categorize <filepath> <investigation>")
        print("  python smart_categorizer.py auto <filepath> [--move] [--threshold N]")
        print("  python smart_categorizer.py batch <directory> [--move] [--threshold N]")
        print()
        print("Examples:")
        print('  python smart_categorizer.py analyze "document.pdf"')
        print('  python smart_categorizer.py categorize "document.pdf" "Weather_Modification"')
        print('  python smart_categorizer.py auto "document.pdf"')
        print('  python smart_categorizer.py auto "document.pdf" --move --threshold 5')
        print('  python smart_categorizer.py batch "C:\\Downloads" --move')
        return
    
    command = sys.argv[1].lower()
    
    if command == 'analyze':
        if len(sys.argv) < 3:
            print("Error: Filepath required")
            return
        
        filepath = sys.argv[2]
        print(f"\nAnalyzing: {Path(filepath).name}")
        
        result = categorizer.analyze_file_for_categorization(filepath)
        
        if 'error' in result:
            print(f"\n[FAIL] {result['error']}")
            return
        
        print(f"\n[OK] Found {len(result['entities_found'])} entities")
        if result['entities_found']:
            print("Entities:", ', '.join(result['entities_found'][:10]))
        
        print(f"\n[OK] Suggested investigations:")
        if result['suggested_investigations']:
            for sug in result['suggested_investigations']:
                print(f"  - {sug['investigation']} (score: {sug['score']})")
                print(f"    Matches: {', '.join(sug['matches'])}")
        else:
            print("  None found")
    
    elif command == 'categorize':
        if len(sys.argv) < 4:
            print("Error: Filepath and investigation required")
            print('Usage: python smart_categorizer.py categorize <filepath> <investigation>')
            return
        
        filepath = sys.argv[2]
        investigation = sys.argv[3]
        
        print(f"\nCategorizing: {Path(filepath).name}")
        print(f"To investigation: {investigation}")
        
        result = categorizer.categorize_file(filepath, investigation)
        
        if result.get('success'):
            print(f"\n[OK] File {result['action']} successfully!")
            print(f"Destination: {result['destination']}")
        else:
            print(f"\n[FAIL] {result.get('error', 'Unknown error')}")
    
    elif command == 'auto':
        if len(sys.argv) < 3:
            print("Error: Filepath required")
            return
        
        filepath = sys.argv[2]
        
        # Parse options
        copy = '--move' not in sys.argv
        threshold = 3
        
        if '--threshold' in sys.argv:
            try:
                idx = sys.argv.index('--threshold')
                threshold = int(sys.argv[idx + 1])
            except:
                print("Error: Invalid threshold value")
                return
        
        result = categorizer.auto_categorize_file(filepath, threshold=threshold, copy=copy)
        
        if result.get('success'):
            print(f"\n[SUCCESS] File categorized!")
            print(f"Investigation: {result['investigation']}")
            print(f"Action: {result['action']}")
            print(f"Path: {result['destination']}")
        elif result.get('status') == 'skipped':
            print("\n[INFO] File skipped by user")
        elif result.get('status') == 'no_match':
            print("\n[INFO] No matching investigations found")
        elif result.get('status') == 'low_confidence':
            print(f"\n[INFO] Confidence too low (score: {result['score']})")
            print("Suggestions:")
            for sug in result.get('suggestions', []):
                print(f"  - {sug['investigation']} (score: {sug['score']})")
        else:
            print(f"\n[FAIL] {result.get('error', 'Unknown error')}")
    
    elif command == 'batch':
        if len(sys.argv) < 3:
            print("Error: Directory required")
            return
        
        directory = sys.argv[2]
        
        # Parse options
        copy = '--move' not in sys.argv
        threshold = 3
        
        if '--threshold' in sys.argv:
            try:
                idx = sys.argv.index('--threshold')
                threshold = int(sys.argv[idx + 1])
            except:
                print("Error: Invalid threshold value")
                return
        
        results = categorizer.batch_categorize(directory, copy=copy, threshold=threshold)
        
        print(f"\n{'='*60}")
        print("\n[SUMMARY]")
        print(f"Categorized: {len(results['categorized'])}")
        print(f"Skipped: {len(results['skipped'])}")
        print(f"No match: {len(results['no_match'])}")
        print(f"Errors: {len(results['errors'])}")
    
    else:
        print(f"Unknown command: {command}")
        print("Valid commands: analyze, categorize, auto, batch")


if __name__ == '__main__':
    main()
