"""
AUTO PROCESS - Smart Research Workflow Launcher
Automatically detects latest research file and processes it
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import subprocess

class AutoProcessor:
    """Automatically process latest research and integrate findings"""

    def __init__(self, research_dir: str = None):
        if research_dir is None:
            research_dir = r"C:\Users\jonat\Documents\Research"

        self.research_dir = Path(research_dir)
        self.inbox_dir = self.research_dir / 'Research_Inbox'
        self.system_dir = self.research_dir / '_System'

    def find_latest_file(self):
        """Find most recent file in Research_Inbox"""
        if not self.inbox_dir.exists():
            return None

        # Get all markdown files
        files = list(self.inbox_dir.glob('*.md'))

        if not files:
            return None

        # Sort by modification time (newest first)
        files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        return files[0]

    def detect_investigation(self, filepath: Path):
        """
        Try to detect which investigation this belongs to
        Reads file content for investigation mentions
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for explicit investigation field
            if 'Investigation:' in content:
                # Extract investigation name
                for line in content.split('\n'):
                    if 'Investigation:' in line:
                        inv = line.split('Investigation:')[1].strip()
                        # Clean markdown bold/italic markers only (** and *)
                        inv = inv.replace('**', '').replace('*', '').strip()
                        return inv

            # Check for investigation mentions in content
            investigations = [
                'COVID_PCR_Truth_Investigation',
                'Weather_Modification',
                'Fox_News_Corp_Investigation',
                'Surveillance_Infrastructure',
                'Flight_Tracking',
                'Media_Ownership'
            ]

            for inv in investigations:
                if inv.replace('_', ' ') in content or inv in content:
                    return inv

            # Default
            return 'General_Research'

        except:
            return 'General_Research'

    def generate_commands(self, filepath: Path, investigation: str):
        """Generate command lines to execute"""
        commands = []

        # Command 1: Process with agent manager
        cmd1 = f'python _System\\agent_manager.py process --document "{filepath.relative_to(self.research_dir)}" --investigation "{investigation}"'
        commands.append(('Spawn Research Agents', cmd1))

        # Command 2: Integrate findings
        cmd2 = 'python _System\\integration_controller.py run'
        commands.append(('Integrate Findings (Full Circle)', cmd2))

        # Command 3: Generate consolidated report
        cmd3 = f'python _System\\consolidate_findings.py --investigation "{investigation}"'
        commands.append(('Generate Consolidated Report', cmd3))

        # Command 4: Export visualizations
        cmd4_timeline = f'python _System\\timeline_integrator.py --investigation "{investigation}" --export-html'
        cmd4_network = f'python _System\\network_integrator.py --investigation "{investigation}" --export-html'
        cmd4_glossary = f'python _System\\glossary_integrator.py --investigation "{investigation}" --export'
        cmd4_xref = 'python _System\\cross_reference_engine.py report'
        cmd4 = f'{cmd4_timeline} && {cmd4_network} && {cmd4_glossary} && {cmd4_xref}'
        commands.append(('Export Visualizations (Timeline/Network/Glossary/XRef)', cmd4))

        # Command 5: Sync to GitHub
        cmd5 = 'python _Automation\\organize_and_sync.py'
        commands.append(('Sync to GitHub', cmd5))

        return commands

    def display_commands(self, filepath: Path, investigation: str, commands: list):
        """Display commands to user"""
        print("\n" + "="*70)
        print("AUTO PROCESS - Research Intelligence Platform")
        print("="*70)
        print(f"\nDetected File: {filepath.name}")
        print(f"Investigation: {investigation}")
        print(f"Modified: {datetime.fromtimestamp(filepath.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n" + "="*70)
        print("COMMANDS TO EXECUTE:")
        print("="*70)

        for i, (desc, cmd) in enumerate(commands, 1):
            print(f"\n{i}. {desc}")
            print(f"   {cmd}")

        print("\n" + "="*70)

    def run_interactive(self):
        """Interactive mode - show commands and ask to run"""
        # Find latest file
        latest = self.find_latest_file()

        if not latest:
            print("\n[ERROR] No files found in Research_Inbox")
            print(f"Please add research files to: {self.inbox_dir}")
            return

        # Detect investigation
        investigation = self.detect_investigation(latest)

        # Generate commands
        commands = self.generate_commands(latest, investigation)

        # Display
        self.display_commands(latest, investigation, commands)

        # Ask user
        print("\nOptions:")
        print("  1 - Run all commands sequentially")
        print("  2 - Run step-by-step (confirm each)")
        print("  3 - Just show commands (don't run)")
        print("  0 - Cancel")

        choice = input("\nYour choice: ").strip()

        if choice == '1':
            self.run_all_commands(commands)
        elif choice == '2':
            self.run_step_by_step(commands)
        elif choice == '3':
            print("\n[INFO] Commands displayed above. Run them manually when ready.")
        else:
            print("\n[CANCELLED]")

    def run_all_commands(self, commands: list):
        """Run all commands sequentially"""
        print("\n" + "="*70)
        print("EXECUTING ALL COMMANDS")
        print("="*70)

        for i, (desc, cmd) in enumerate(commands, 1):
            print(f"\n[{i}/{len(commands)}] {desc}...")
            print(f"Running: {cmd}")
            print("-"*70)

            try:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    cwd=self.research_dir,
                    capture_output=False,
                    text=True
                )

                if result.returncode == 0:
                    print(f"\n[OK] Step {i} completed successfully")
                else:
                    print(f"\n[WARNING] Step {i} completed with warnings")

            except Exception as e:
                print(f"\n[ERROR] Step {i} failed: {e}")
                response = input("\nContinue to next step? (y/n): ")
                if response.lower() != 'y':
                    print("[STOPPED]")
                    return

        print("\n" + "="*70)
        print("[SUCCESS] All commands completed!")
        print("="*70)

    def run_step_by_step(self, commands: list):
        """Run commands one at a time with confirmation"""
        print("\n" + "="*70)
        print("STEP-BY-STEP EXECUTION")
        print("="*70)

        for i, (desc, cmd) in enumerate(commands, 1):
            print(f"\n[{i}/{len(commands)}] {desc}")
            print(f"Command: {cmd}")

            response = input("\nRun this step? (y/n/q to quit): ").strip().lower()

            if response == 'q':
                print("\n[STOPPED]")
                return
            elif response != 'y':
                print("[SKIPPED]")
                continue

            print("-"*70)

            try:
                subprocess.run(
                    cmd,
                    shell=True,
                    cwd=self.research_dir,
                    capture_output=False,
                    text=True
                )
                print(f"\n[OK] Step {i} completed")

            except Exception as e:
                print(f"\n[ERROR] Step {i} failed: {e}")

        print("\n" + "="*70)
        print("[COMPLETE] Step-by-step execution finished")
        print("="*70)

    def run_auto(self):
        """Fully automatic mode - just run everything"""
        latest = self.find_latest_file()

        if not latest:
            print("\n[ERROR] No files found in Research_Inbox")
            return 1

        investigation = self.detect_investigation(latest)
        commands = self.generate_commands(latest, investigation)

        print(f"\n[AUTO] Processing: {latest.name}")
        print(f"[AUTO] Investigation: {investigation}")

        self.run_all_commands(commands)
        return 0


def main():
    """Command-line interface"""
    import argparse

    parser = argparse.ArgumentParser(description='Auto Process Research')
    parser.add_argument('--auto', action='store_true', help='Fully automatic mode')
    parser.add_argument('--file', help='Specific file to process (instead of latest)')
    parser.add_argument('--investigation', help='Force specific investigation')

    args = parser.parse_args()

    processor = AutoProcessor()

    if args.auto:
        # Fully automatic
        return processor.run_auto()
    else:
        # Interactive
        processor.run_interactive()
        return 0


if __name__ == '__main__':
    sys.exit(main())
