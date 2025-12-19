"""
GITHUB SYNC
Automatically commit and push research to GitHub
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import json


class GitHubSync:
    """
    Automatically sync research directory to GitHub
    """

    def __init__(self, research_dir: str = None):
        """Initialize with research directory"""
        if research_dir is None:
            research_dir = r"C:\Users\jonat\Documents\Research"

        self.research_dir = Path(research_dir)
        self.log_dir = self.research_dir / '_System' / 'logs'
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def run_git_command(self, command: list) -> dict:
        """
        Run a git command and return result

        Args:
            command: Git command as list (e.g., ['git', 'status'])

        Returns:
            Dictionary with stdout, stderr, and return code
        """
        try:
            result = subprocess.run(
                command,
                cwd=self.research_dir,
                capture_output=True,
                text=True,
                timeout=60
            )

            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_status(self) -> dict:
        """Get current git status"""
        result = self.run_git_command(['git', 'status', '--porcelain'])

        if not result['success']:
            return {'error': 'Failed to get git status'}

        lines = result['stdout'].strip().split('\n') if result['stdout'].strip() else []

        changes = {
            'modified': [],
            'added': [],
            'deleted': [],
            'untracked': []
        }

        for line in lines:
            if not line:
                continue

            status = line[:2]
            filepath = line[3:]

            if status == ' M' or status == 'M ':
                changes['modified'].append(filepath)
            elif status == '??':
                changes['untracked'].append(filepath)
            elif status == ' D' or status == 'D ':
                changes['deleted'].append(filepath)
            elif status == 'A ':
                changes['added'].append(filepath)

        changes['total'] = sum(len(v) for v in changes.values())
        changes['has_changes'] = changes['total'] > 0

        return changes

    def generate_commit_message(self, changes: dict) -> str:
        """
        Generate intelligent commit message based on changes

        Args:
            changes: Dictionary of changes from get_status()

        Returns:
            Commit message string
        """
        # Count changes by type
        modified_count = len(changes['modified'])
        added_count = len(changes['added']) + len(changes['untracked'])
        deleted_count = len(changes['deleted'])

        # Build message parts
        parts = []

        if added_count > 0:
            parts.append(f"Added {added_count} file(s)")
        if modified_count > 0:
            parts.append(f"Updated {modified_count} file(s)")
        if deleted_count > 0:
            parts.append(f"Deleted {deleted_count} file(s)")

        # Main message
        if parts:
            main_msg = ", ".join(parts)
        else:
            main_msg = "Updated research files"

        # Try to identify investigation changes
        all_files = (changes['modified'] + changes['added'] +
                    changes['untracked'] + changes['deleted'])

        investigations = set()
        for filepath in all_files:
            if 'Active_Investigations/' in filepath:
                parts = filepath.split('/')
                if len(parts) > 1:
                    investigations.add(parts[1])

        # Build full message
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        message = f"{main_msg} - {timestamp}"

        if investigations:
            inv_list = ', '.join(sorted(investigations))
            message += f"\n\nInvestigations: {inv_list}"

        message += "\n\n[AUTO] Auto-synced with GitHub Sync"

        return message

    def commit_and_push(self, custom_message: str = None, dry_run: bool = False) -> dict:
        """
        Commit all changes and push to GitHub

        Args:
            custom_message: Optional custom commit message
            dry_run: If True, show what would be done without doing it

        Returns:
            Dictionary with results
        """
        # Get current status
        print("\n Checking for changes...")
        status = self.get_status()

        if 'error' in status:
            return {'error': status['error']}

        if not status['has_changes']:
            print("[OK] No changes to commit")
            return {
                'status': 'no_changes',
                'message': 'Working directory is clean'
            }

        # Show what we found
        print(f"\n Found {status['total']} changes:")
        if status['untracked']:
            print(f"  - {len(status['untracked'])} new files")
        if status['modified']:
            print(f"  - {len(status['modified'])} modified files")
        if status['deleted']:
            print(f"  - {len(status['deleted'])} deleted files")

        # Generate or use custom message
        commit_msg = custom_message or self.generate_commit_message(status)

        print(f"\n Commit message:")
        print(f"{'-'*70}")
        print(commit_msg)
        print(f"{'-'*70}")

        if dry_run:
            print("\n DRY RUN - No changes will be made")
            return {
                'status': 'dry_run',
                'changes': status,
                'message': commit_msg
            }

        # Stage all changes
        print("\n Staging changes...")
        result = self.run_git_command(['git', 'add', '-A'])

        if not result['success']:
            return {
                'error': f"Failed to stage changes: {result.get('stderr', 'Unknown error')}"
            }

        print("[OK] Changes staged")

        # Commit
        print("\n Creating commit...")
        result = self.run_git_command(['git', 'commit', '-m', commit_msg])

        if not result['success']:
            # Check if it's because nothing was staged
            if 'nothing to commit' in result['stdout'].lower():
                print("[OK] No changes to commit")
                return {
                    'status': 'no_changes',
                    'message': 'Nothing to commit'
                }
            return {
                'error': f"Failed to commit: {result.get('stderr', 'Unknown error')}"
            }

        print("[OK] Commit created")

        # Push to GitHub
        print("\n Pushing to GitHub...")
        result = self.run_git_command(['git', 'push'])

        if not result['success']:
            return {
                'error': f"Failed to push to GitHub: {result.get('stderr', 'Unknown error')}",
                'note': 'Commit was created locally but not pushed'
            }

        print("[OK] Pushed to GitHub successfully")

        # Log the sync
        self.log_sync(status, commit_msg)

        return {
            'success': True,
            'changes': status,
            'commit_message': commit_msg,
            'timestamp': datetime.now().isoformat()
        }

    def log_sync(self, changes: dict, commit_msg: str):
        """Log sync action"""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.log_dir / f'github_sync_{today}.json'

        # Load existing log
        if log_file.exists():
            with open(log_file, 'r') as f:
                log_data = json.load(f)
        else:
            log_data = {'date': today, 'syncs': []}

        # Add new sync
        log_data['syncs'].append({
            'timestamp': datetime.now().isoformat(),
            'changes': changes,
            'commit_message': commit_msg
        })

        # Save log
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)


def main():
    """Command-line interface"""
    sync = GitHubSync()

    print("\n GITHUB AUTO-SYNC")
    print("=" * 70)

    # Check for flags
    dry_run = '--dry-run' in sys.argv or '-n' in sys.argv
    custom_msg = None

    # Check for custom message
    if '--message' in sys.argv or '-m' in sys.argv:
        try:
            idx = sys.argv.index('--message') if '--message' in sys.argv else sys.argv.index('-m')
            custom_msg = sys.argv[idx + 1]
        except IndexError:
            print("Error: --message requires an argument")
            return

    # Run sync
    result = sync.commit_and_push(custom_message=custom_msg, dry_run=dry_run)

    print(f"\n{'='*70}")

    if result.get('success'):
        print("\n[OK] SYNC COMPLETE")
        print(f"\nAll changes backed up to:")
        print("https://github.com/jonathondouglasyager-debug/Research")

    elif result.get('status') == 'no_changes':
        print("\n[OK] ALREADY IN SYNC")
        print("No changes to commit")

    elif result.get('status') == 'dry_run':
        print("\n[OK] DRY RUN COMPLETE")
        print("Run without --dry-run to actually sync")

    elif 'error' in result:
        print(f"\n[ERROR] ERROR: {result['error']}")
        if result.get('note'):
            print(f"Note: {result['note']}")

    print(f"\n{'='*70}\n")


if __name__ == '__main__':
    main()
