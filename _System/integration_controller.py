"""
INTEGRATION CONTROLLER
Orchestrates the "Full Circle" knowledge integration pipeline
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List

sys.path.append(str(Path(__file__).parent))

from entity_integrator import EntityIntegrator
from glossary_integrator import GlossaryIntegrator
from timeline_integrator import TimelineIntegrator
from network_integrator import NetworkIntegrator
from agent_manager import AgentManager


class IntegrationController:
    """
    Orchestrates the complete integration pipeline:
    1. Find completed agents
    2. Load findings
    3. Integrate entities, glossary, timeline, network
    4. Update integration status
    5. Git auto-commit
    """

    def __init__(self, research_dir: str = None, auto_commit: bool = True):
        """
        Initialize integration controller

        Args:
            research_dir: Research directory path
            auto_commit: Automatically commit changes to Git
        """
        if research_dir is None:
            research_dir = r"C:\Users\jonat\Documents\Research"

        self.research_dir = Path(research_dir)
        self.auto_commit = auto_commit

        # Initialize integrators
        self.entity_integrator = EntityIntegrator(str(research_dir))

        # Initialize agent manager
        self.agent_manager = AgentManager(str(research_dir))

        # Logs directory
        self.logs_dir = self.research_dir / '_System' / 'logs'
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def run_integration_pipeline(self) -> Dict:
        """
        Main integration pipeline:
        1. Find pending agents
        2. Integrate each one
        3. Report results
        """
        print(f"\n{'='*70}")
        print("INTEGRATION PIPELINE - Starting")
        print(f"{'='*70}\n")

        # Find pending integrations
        pending = self.agent_manager.list_pending_integrations()

        if not pending:
            print("[INTEGRATION] No pending integrations")
            return {
                'status': 'no_pending',
                'total_processed': 0
            }

        print(f"[INTEGRATION] Found {len(pending)} agents to integrate")

        # Process each agent
        results = []
        for agent_info in pending:
            print(f"\n{'='*70}")
            result = self.integrate_agent_findings(agent_info['findings_path'])
            results.append(result)

        # Summary
        successful = sum(1 for r in results if r['status'] == 'success')
        failed = sum(1 for r in results if r['status'] == 'error')

        print(f"\n{'='*70}")
        print("INTEGRATION PIPELINE - Complete")
        print(f"{'='*70}")
        print(f"\nProcessed: {len(results)} agents")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")

        return {
            'status': 'completed',
            'total_processed': len(results),
            'successful': successful,
            'failed': failed,
            'results': results
        }

    def integrate_agent_findings(self, findings_path: str) -> Dict:
        """
        Integrate findings from a single agent

        Args:
            findings_path: Path to findings.json file

        Returns:
            Integration report dict
        """
        findings_file = Path(findings_path)

        if not findings_file.exists():
            return {
                'status': 'error',
                'error': f'Findings file not found: {findings_path}'
            }

        print(f"\n[INTEGRATION] Processing: {findings_file.parent.name}")

        try:
            # Load findings
            with open(findings_file, 'r') as f:
                findings = json.load(f)

            agent_id = findings['agent_id']
            investigation = findings['parent_investigation']

            # Integration stats
            integration_report = {
                'agent_id': agent_id,
                'investigation': investigation,
                'timestamp': datetime.now().isoformat(),
                'entities': None,
                'glossary': None,
                'timeline': None,
                'network': None
            }

            # 1. ENTITY INTEGRATION
            entities = findings['findings']['entities_discovered']
            if entities:
                print(f"[INTEGRATION] Integrating {len(entities)} entities...")
                entity_stats = self.entity_integrator.integrate_entities(entities, investigation)
                integration_report['entities'] = entity_stats
            else:
                print("[INTEGRATION] No entities to integrate")
                integration_report['entities'] = {'total_new': 0, 'added': 0, 'merged': 0}

            # 2. GLOSSARY INTEGRATION
            glossary_terms = findings['findings']['glossary_terms']
            if glossary_terms:
                print(f"[INTEGRATION] Integrating {len(glossary_terms)} glossary terms...")
                glossary_integrator = GlossaryIntegrator(investigation)
                glossary_stats = glossary_integrator.integrate_terms(glossary_terms)
                integration_report['glossary'] = glossary_stats
                print(f"[INTEGRATION] Glossary: {glossary_stats['new_terms']} new, {glossary_stats['updated_terms']} updated")
            else:
                print("[INTEGRATION] No glossary terms to integrate")
                integration_report['glossary'] = {'new_terms': 0, 'updated_terms': 0}

            # 3. TIMELINE INTEGRATION
            timeline_events = findings['findings']['timeline_events']
            if timeline_events:
                print(f"[INTEGRATION] Integrating {len(timeline_events)} timeline events...")
                timeline_integrator = TimelineIntegrator(investigation)
                timeline_stats = timeline_integrator.integrate_events(timeline_events)
                integration_report['timeline'] = timeline_stats
                print(f"[INTEGRATION] Timeline: {timeline_stats['new_events']} new, {timeline_stats['updated_events']} updated")
            else:
                print("[INTEGRATION] No timeline events to integrate")
                integration_report['timeline'] = {'new_events': 0, 'updated_events': 0}

            # 4. NETWORK INTEGRATION
            print("[INTEGRATION] Building knowledge network...")
            network_integrator = NetworkIntegrator(investigation)
            network_stats = network_integrator.integrate_relationships(entities)
            integration_report['network'] = network_stats
            print(f"[INTEGRATION] Network: {network_stats['new_nodes']} new nodes, {network_stats['new_edges']} new edges")

            # UPDATE INTEGRATION STATUS
            findings['integration_status']['entities_integrated'] = True
            findings['integration_status']['glossary_integrated'] = True
            findings['integration_status']['timeline_integrated'] = True
            findings['integration_status']['network_integrated'] = True
            findings['integration_status']['integrated_at'] = datetime.now().isoformat()

            # Save updated findings
            with open(findings_file, 'w') as f:
                json.dump(findings, f, indent=2)

            print(f"[INTEGRATION] Updated integration status in {findings_file}")

            # GIT AUTO-COMMIT
            if self.auto_commit:
                self.git_auto_commit(integration_report)

            # LOG INTEGRATION
            self.log_integration(integration_report)

            print(f"[INTEGRATION] Agent {agent_id} integrated successfully")

            return {
                'status': 'success',
                'agent_id': agent_id,
                'report': integration_report
            }

        except Exception as e:
            print(f"[INTEGRATION] Error: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'findings_path': findings_path
            }

    def git_auto_commit(self, integration_report: Dict):
        """
        Auto-commit integration to Git

        Creates a descriptive commit message
        """
        try:
            # Build commit message
            agent_id = integration_report['agent_id']
            investigation = integration_report['investigation']

            entity_stats = integration_report['entities']
            entities_added = entity_stats.get('added', 0)
            entities_merged = entity_stats.get('merged', 0)

            glossary_stats = integration_report.get('glossary', {})
            glossary_new = glossary_stats.get('new_terms', 0)
            glossary_updated = glossary_stats.get('updated_terms', 0)

            timeline_stats = integration_report.get('timeline', {})
            timeline_new = timeline_stats.get('new_events', 0)

            network_stats = integration_report.get('network', {})
            network_nodes = network_stats.get('new_nodes', 0)
            network_edges = network_stats.get('new_edges', 0)

            message = f"Integrated agent findings: {agent_id}\n\n"
            message += f"Investigation: {investigation}\n"
            message += f"Entities: {entities_added} new, {entities_merged} merged\n"
            message += f"Glossary: {glossary_new} new terms, {glossary_updated} updated\n"
            message += f"Timeline: {timeline_new} new events\n"
            message += f"Network: {network_nodes} new nodes, {network_edges} new edges\n"
            message += f"\n[AUTO] Research Intelligence Platform - Phase 2"

            # Git add
            subprocess.run(['git', 'add', '-A'], cwd=self.research_dir, check=True, capture_output=True)

            # Git commit
            result = subprocess.run(
                ['git', 'commit', '-m', message],
                cwd=self.research_dir,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                print(f"[GIT] Auto-committed integration: {agent_id}")
            else:
                # Check if it's "nothing to commit"
                if 'nothing to commit' in result.stdout.lower():
                    print("[GIT] No changes to commit")
                else:
                    print(f"[GIT] Commit warning: {result.stderr}")

        except Exception as e:
            print(f"[GIT] Auto-commit failed: {e}")
            print("[GIT] Integration completed but not committed")

    def log_integration(self, integration_report: Dict):
        """Save integration report to log file"""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs_dir / f'integration_log_{today}.json'

        # Load existing log
        if log_file.exists():
            with open(log_file, 'r') as f:
                log_data = json.load(f)
        else:
            log_data = {'date': today, 'integrations': []}

        # Add new integration
        log_data['integrations'].append(integration_report)

        # Save log
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)

        print(f"[LOG] Saved integration log to {log_file}")

    def monitor_and_integrate(self, interval: int = 60, max_iterations: int = None):
        """
        Continuous monitoring mode

        Args:
            interval: Check interval in seconds
            max_iterations: Max iterations (None = infinite)
        """
        import time

        print(f"\n[MONITOR] Starting continuous integration monitoring")
        print(f"[MONITOR] Check interval: {interval} seconds")
        print(f"[MONITOR] Press Ctrl+C to stop\n")

        iteration = 0
        try:
            while max_iterations is None or iteration < max_iterations:
                iteration += 1
                print(f"\n[MONITOR] Check #{iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

                # Run integration pipeline
                result = self.run_integration_pipeline()

                if result['status'] == 'completed':
                    print(f"[MONITOR] Integrated {result['total_processed']} agents")

                # Wait
                if max_iterations is None or iteration < max_iterations:
                    print(f"[MONITOR] Sleeping for {interval} seconds...")
                    time.sleep(interval)

        except KeyboardInterrupt:
            print("\n[MONITOR] Stopped by user")


def main():
    """Command-line interface"""
    import argparse

    parser = argparse.ArgumentParser(description='Integration Controller')
    parser.add_argument('command', choices=['run', 'monitor', 'integrate'],
                       help='Command to execute')
    parser.add_argument('--findings', help='Path to findings.json for integrate command')
    parser.add_argument('--interval', type=int, default=60, help='Monitor interval in seconds')
    parser.add_argument('--no-commit', action='store_true', help='Disable Git auto-commit')

    args = parser.parse_args()

    controller = IntegrationController(auto_commit=not args.no_commit)

    if args.command == 'run':
        # Run once
        result = controller.run_integration_pipeline()

    elif args.command == 'monitor':
        # Continuous monitoring
        controller.monitor_and_integrate(interval=args.interval)

    elif args.command == 'integrate':
        # Integrate specific findings file
        if not args.findings:
            print("Error: --findings required for integrate command")
            return

        result = controller.integrate_agent_findings(args.findings)

        if result['status'] == 'success':
            print(f"\n[SUCCESS] Integration complete")
            print(f"Agent: {result['agent_id']}")
        else:
            print(f"\n[ERROR] Integration failed: {result.get('error', 'Unknown error')}")


if __name__ == '__main__':
    main()
