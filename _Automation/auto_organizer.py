"""
AUTO ORGANIZER
Automatically process Research Inbox and organize files
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import json

# Import smart categorizer
from smart_categorizer import SmartCategorizer

class AutoOrganizer:
    """
    Automatically organizes files from Research Inbox
    """

    def __init__(self, research_dir: str = None):
        """Initialize with research directory"""
        if research_dir is None:
            research_dir = r"C:\Users\jonat\Documents\Research"

        self.research_dir = Path(research_dir)
        self.inbox_dir = self.research_dir / 'Research_Inbox'
        self.log_dir = self.research_dir / '_System' / 'logs'
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Initialize categorizer
        self.categorizer = SmartCategorizer(research_dir)

    def log_action(self, action: str, details: dict):
        """Log an action to daily log file"""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.log_dir / f'organize_log_{today}.json'

        # Load existing log
        if log_file.exists():
            with open(log_file, 'r') as f:
                log_data = json.load(f)
        else:
            log_data = {'date': today, 'actions': []}

        # Add new action
        log_data['actions'].append({
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'details': details
        })

        # Save log
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)

    def process_inbox(self, move: bool = True, threshold: int = 2,
                     interactive: bool = False) -> dict:
        """
        Process all files in Research Inbox

        Args:
            move: Move files instead of copy (default True)
            threshold: Minimum confidence score (default 2 - more lenient)
            interactive: Ask before each file (default False)

        Returns:
            Summary of processing
        """
        # Check inbox exists
        if not self.inbox_dir.exists():
            return {'error': 'Research Inbox not found. Creating it now...'}

        # Get all files in inbox
        files = list(self.inbox_dir.glob('*.*'))

        if not files:
            return {
                'status': 'empty',
                'message': 'Research Inbox is empty - no files to process'
            }

        print(f"\n{'='*70}")
        print(f"AUTO ORGANIZER - Processing {len(files)} files from Research Inbox")
        print(f"{'='*70}\n")

        results = {
            'total_files': len(files),
            'organized': [],
            'manual_review': [],
            'errors': []
        }

        for filepath in files:
            print(f"\n{'-'*70}")
            print(f"FILE: {filepath.name}")
            print(f"{'-'*70}")

            try:
                # Try to auto-categorize
                result = self.categorizer.auto_categorize_file(
                    str(filepath),
                    threshold=threshold,
                    copy=not move,
                    interactive=interactive
                )

                if result.get('success'):
                    print(f"[OK] ORGANIZED -> {result['investigation']}/{result['subfolder']}")
                    results['organized'].append({
                        'file': filepath.name,
                        'investigation': result['investigation'],
                        'path': result['destination']
                    })

                    # Log it
                    self.log_action('organized', {
                        'file': filepath.name,
                        'investigation': result['investigation'],
                        'destination': result['destination']
                    })

                elif result.get('status') in ['low_confidence', 'no_match']:
                    print(f"[WARN] NEEDS MANUAL REVIEW - Confidence too low or no match")

                    # Move to manual review folder
                    manual_dir = self.research_dir / 'Manual_Review'
                    manual_dir.mkdir(exist_ok=True)

                    dest = manual_dir / filepath.name
                    if move:
                        filepath.rename(dest)
                    else:
                        import shutil
                        shutil.copy2(filepath, dest)

                    results['manual_review'].append({
                        'file': filepath.name,
                        'reason': result.get('message', 'Unknown'),
                        'suggestions': result.get('suggestions', [])
                    })

                    print(f"  -> Moved to Manual_Review folder")

                else:
                    print(f"[FAIL] SKIPPED - {result.get('status', 'unknown')}")
                    results['errors'].append({
                        'file': filepath.name,
                        'error': result.get('error', 'Unknown error')
                    })

            except Exception as e:
                print(f"[FAIL] ERROR: {str(e)}")
                results['errors'].append({
                    'file': filepath.name,
                    'error': str(e)
                })

        # Print summary
        print(f"\n{'='*70}")
        print("SUMMARY")
        print(f"{'='*70}")
        print(f"[OK] Organized: {len(results['organized'])} files")
        print(f"[WARN] Manual Review: {len(results['manual_review'])} files")
        print(f"[FAIL] Errors: {len(results['errors'])} files")
        print(f"{'='*70}\n")

        # Log summary
        self.log_action('batch_process', {
            'total': results['total_files'],
            'organized': len(results['organized']),
            'manual_review': len(results['manual_review']),
            'errors': len(results['errors'])
        })

        return results


def main():
    """Command-line interface"""
    organizer = AutoOrganizer()

    print("\nRESEARCH AUTO-ORGANIZER")
    print("=" * 70)

    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        # Interactive mode - ask before each file
        results = organizer.process_inbox(move=True, threshold=2, interactive=True)
    else:
        # Auto mode - process everything automatically
        results = organizer.process_inbox(move=True, threshold=2, interactive=False)

    if results.get('status') == 'empty':
        print(f"\n{results['message']}")
        print("\nTo use:")
        print("  1. Save research files to: C:\\Users\\jonat\\Documents\\Research\\Research_Inbox")
        print("  2. Run this script again")
        return

    # Show what needs manual review
    if results['manual_review']:
        print("\n[WARN] FILES NEEDING MANUAL REVIEW:")
        print("Located in: C:\\Users\\jonat\\Documents\\Research\\Manual_Review")
        for item in results['manual_review']:
            print(f"\n  - {item['file']}")
            print(f"    Reason: {item['reason']}")
            if item['suggestions']:
                print(f"    Suggestions:")
                for sug in item['suggestions'][:3]:
                    print(f"      - {sug['investigation']} (score: {sug['score']})")


if __name__ == '__main__':
    main()
