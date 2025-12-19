"""
ORGANIZE AND SYNC
Master script - Organize files from Inbox and sync to GitHub in one command
"""

import sys
from pathlib import Path

# Import our automation modules
from auto_organizer import AutoOrganizer
from github_sync import GitHubSync


def main():
    """
    Complete workflow:
    1. Process Research Inbox
    2. Sync everything to GitHub
    """
    print("\n" + "=" * 70)
    print("RESEARCH WORKFLOW - Organize & Sync")
    print("=" * 70)

    # Step 1: Organize files from Inbox
    print("\nSTEP 1: Organizing files from Research Inbox...")
    print("-" * 70)

    organizer = AutoOrganizer()

    # Check if interactive mode requested
    interactive = '--interactive' in sys.argv or '-i' in sys.argv

    organize_results = organizer.process_inbox(
        move=True,
        threshold=2,
        interactive=interactive
    )

    # Handle empty inbox
    if organize_results.get('status') == 'empty':
        print(f"\n{organize_results['message']}")
        print("\nNo files to organize. Proceeding to GitHub sync...")
    else:
        print(f"\n[OK] Organization complete:")
        print(f"  - {len(organize_results['organized'])} files organized")
        print(f"  - {len(organize_results['manual_review'])} files need manual review")

    # Step 2: Sync to GitHub
    print("\n" + "=" * 70)
    print("\nSTEP 2: Syncing to GitHub...")
    print("-" * 70)

    syncer = GitHubSync()

    # Check for dry run
    dry_run = '--dry-run' in sys.argv or '-n' in sys.argv

    # Check for custom commit message
    custom_msg = None
    if '--message' in sys.argv or '-m' in sys.argv:
        try:
            idx = sys.argv.index('--message') if '--message' in sys.argv else sys.argv.index('-m')
            custom_msg = sys.argv[idx + 1]
        except IndexError:
            pass

    sync_results = syncer.commit_and_push(
        custom_message=custom_msg,
        dry_run=dry_run
    )

    # Final summary
    print("\n" + "=" * 70)
    print("WORKFLOW COMPLETE")
    print("=" * 70)

    if organize_results.get('status') != 'empty':
        print(f"\n[OK] Organized: {len(organize_results['organized'])} files")

        if organize_results['manual_review']:
            print(f"\n[MANUAL REVIEW] {len(organize_results['manual_review'])} files need review")
            print("   Location: C:\\Users\\jonat\\Documents\\Research\\Manual_Review")

    if sync_results.get('success'):
        print(f"\n[OK] GitHub: All changes synced")
        print("   https://github.com/jonathondouglasyager-debug/Research")
    elif sync_results.get('status') == 'no_changes':
        print(f"\n[OK] GitHub: Already in sync (no changes)")
    elif sync_results.get('status') == 'dry_run':
        print(f"\n[OK] Dry Run: Complete (no actual changes made)")
    elif 'error' in sync_results:
        print(f"\n[ERROR] GitHub: {sync_results['error']}")

    print("\n" + "=" * 70 + "\n")

    # Show quick help
    print("TIPS:")
    print("   - Drop research files into: Research_Inbox\\")
    print("   - Run this script daily to keep everything organized")
    print("   - Files go to GitHub automatically")
    print("\n   Options:")
    print("     --interactive   Ask before organizing each file")
    print("     --dry-run       Show what would happen without doing it")
    print("     --message \"...\"  Custom commit message")
    print("")


if __name__ == '__main__':
    main()
