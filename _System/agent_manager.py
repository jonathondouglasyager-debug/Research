"""
AGENT MANAGER
Spawns, tracks, and manages background research agents
"""

import os
import sys
import json
import re
import threading
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Add agents directory to path
sys.path.append(str(Path(__file__).parent))

from agents.web_research_agent import WebResearchAgent


class AgentManager:
    """
    Manages the lifecycle of research agents:
    - Detects "Next Steps" in documents
    - Spawns agents for each question
    - Tracks agent status
    - Manages integration queue
    """

    def __init__(self, research_dir: str = None):
        """Initialize agent manager"""
        if research_dir is None:
            research_dir = r"C:\Users\jonat\Documents\Research"

        self.research_dir = Path(research_dir)
        self.system_dir = self.research_dir / '_System'
        self.state_file = self.system_dir / 'agent_manager_state.json'

        # Load or initialize state
        self.state = self._load_state()

        # Active agents (agent_id -> thread)
        self.active_threads = {}

    def _load_state(self) -> Dict:
        """Load agent manager state from JSON"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        else:
            return {
                'agents': {},  # agent_id -> agent info
                'total_spawned': 0,
                'total_completed': 0,
                'total_failed': 0
            }

    def _save_state(self):
        """Save agent manager state to JSON"""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)

    def detect_next_steps(self, document_path: str) -> List[str]:
        """
        Parse document for "Next Steps" section, extract questions

        Args:
            document_path: Path to markdown document

        Returns:
            List of research questions
        """
        path = Path(document_path)

        if not path.exists():
            print(f"[AGENT MANAGER] Document not found: {document_path}")
            return []

        # Read document
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find "Next Steps" section
        # Pattern: ## Next Steps or ### Next Steps (case-insensitive)
        pattern = r'#{1,3}\s*Next\s+Steps?\s*\n(.*?)(?=\n#{1,3}|$)'
        match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)

        if not match:
            print(f"[AGENT MANAGER] No 'Next Steps' section found in {path.name}")
            return []

        next_steps_content = match.group(1)

        # Extract questions
        # Pattern: Numbered lists (1., 2., etc.) or bullet points (-, *, •)
        question_pattern = r'(?:^|\n)\s*(?:\d+\.|-|\*|•)\s+(.+?)(?=\n|$)'
        questions = re.findall(question_pattern, next_steps_content, re.MULTILINE)

        # Clean up questions (remove extra whitespace)
        questions = [q.strip() for q in questions if q.strip()]

        print(f"[AGENT MANAGER] Found {len(questions)} research questions in {path.name}")
        for i, q in enumerate(questions, 1):
            print(f"  {i}. {q[:80]}...")

        return questions

    def spawn_agent(self, question: str, investigation: str,
                    agent_type: str = "web_research", run_async: bool = True) -> str:
        """
        Create new research agent and optionally run in background

        Args:
            question: Research question
            investigation: Investigation name
            agent_type: Type of agent (currently only 'web_research')
            run_async: Run in background thread

        Returns:
            agent_id
        """
        # Generate unique agent ID
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:19]  # Include microseconds
        agent_id = f"{agent_type}_{timestamp}"

        print(f"\n[AGENT MANAGER] Spawning agent: {agent_id}")
        print(f"  Question: {question}")
        print(f"  Investigation: {investigation}")
        print(f"  Type: {agent_type}")

        # Create agent based on type
        if agent_type == "web_research":
            agent = WebResearchAgent(
                agent_id=agent_id,
                question=question,
                investigation=investigation,
                research_dir=str(self.research_dir)
            )
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")

        # Register in state
        self.state['agents'][agent_id] = {
            'agent_id': agent_id,
            'question': question,
            'investigation': investigation,
            'agent_type': agent_type,
            'created': datetime.now().isoformat(),
            'status': 'pending',
            'run_async': run_async
        }
        self.state['total_spawned'] += 1
        self._save_state()

        # Run agent
        if run_async:
            self.run_agent_background(agent_id, agent)
        else:
            self.run_agent_sync(agent_id, agent)

        return agent_id

    def run_agent_background(self, agent_id: str, agent):
        """Execute agent in background thread"""
        print(f"[AGENT MANAGER] Starting background thread for {agent_id}")

        def run_agent_thread():
            try:
                # Update status
                self.state['agents'][agent_id]['status'] = 'running'
                self.state['agents'][agent_id]['started'] = datetime.now().isoformat()
                self._save_state()

                # Execute agent
                results = agent.execute()

                # Update status
                self.state['agents'][agent_id]['status'] = 'completed'
                self.state['agents'][agent_id]['completed'] = datetime.now().isoformat()
                self.state['agents'][agent_id]['findings_path'] = str(agent.findings_dir / 'findings.json')
                self.state['total_completed'] += 1
                self._save_state()

                print(f"[AGENT MANAGER] Agent {agent_id} completed successfully")

            except Exception as e:
                print(f"[AGENT MANAGER] Agent {agent_id} failed: {e}")
                self.state['agents'][agent_id]['status'] = 'failed'
                self.state['agents'][agent_id]['error'] = str(e)
                self.state['total_failed'] += 1
                self._save_state()

        # Create and start thread
        thread = threading.Thread(target=run_agent_thread, daemon=True)
        self.active_threads[agent_id] = thread
        thread.start()

    def run_agent_sync(self, agent_id: str, agent):
        """Execute agent synchronously (blocking)"""
        print(f"[AGENT MANAGER] Running agent {agent_id} synchronously")

        try:
            # Update status
            self.state['agents'][agent_id]['status'] = 'running'
            self.state['agents'][agent_id]['started'] = datetime.now().isoformat()
            self._save_state()

            # Execute agent
            results = agent.execute()

            # Update status
            self.state['agents'][agent_id]['status'] = 'completed'
            self.state['agents'][agent_id]['completed'] = datetime.now().isoformat()
            self.state['agents'][agent_id]['findings_path'] = str(agent.findings_dir / 'findings.json')
            self.state['total_completed'] += 1
            self._save_state()

            print(f"[AGENT MANAGER] Agent {agent_id} completed successfully")

        except Exception as e:
            print(f"[AGENT MANAGER] Agent {agent_id} failed: {e}")
            self.state['agents'][agent_id]['status'] = 'failed'
            self.state['agents'][agent_id]['error'] = str(e)
            self.state['total_failed'] += 1
            self._save_state()

    def get_agent_status(self, agent_id: str) -> Optional[Dict]:
        """Get status of specific agent"""
        return self.state['agents'].get(agent_id)

    def list_agents(self, status: Optional[str] = None) -> List[Dict]:
        """
        List all agents, optionally filtered by status

        Args:
            status: Filter by status (pending, running, completed, failed)

        Returns:
            List of agent info dicts
        """
        agents = list(self.state['agents'].values())

        if status:
            agents = [a for a in agents if a['status'] == status]

        # Sort by created time (newest first)
        agents.sort(key=lambda x: x['created'], reverse=True)

        return agents

    def list_pending_integrations(self) -> List[Dict]:
        """
        Find completed agents that haven't been integrated yet

        Returns:
            List of agent info dicts ready for integration
        """
        pending = []

        for agent_info in self.state['agents'].values():
            if agent_info['status'] == 'completed':
                # Check if findings file exists
                findings_path = agent_info.get('findings_path')
                if findings_path and Path(findings_path).exists():
                    # Load findings to check integration status
                    with open(findings_path, 'r') as f:
                        findings = json.load(f)

                    # Check if not yet integrated
                    if not findings['integration_status'].get('entities_integrated'):
                        pending.append(agent_info)

        print(f"[AGENT MANAGER] Found {len(pending)} agents pending integration")
        return pending

    def process_document_next_steps(self, document_path: str, investigation: str,
                                    run_async: bool = True) -> List[str]:
        """
        Complete workflow: detect next steps and spawn agents

        Args:
            document_path: Path to markdown document
            investigation: Investigation name
            run_async: Run agents in background

        Returns:
            List of agent IDs spawned
        """
        print(f"\n[AGENT MANAGER] Processing document: {Path(document_path).name}")

        # Detect questions
        questions = self.detect_next_steps(document_path)

        if not questions:
            print("[AGENT MANAGER] No research questions found")
            return []

        # Spawn agents
        agent_ids = []
        for question in questions:
            agent_id = self.spawn_agent(
                question=question,
                investigation=investigation,
                agent_type="web_research",
                run_async=run_async
            )
            agent_ids.append(agent_id)

        print(f"\n[AGENT MANAGER] Spawned {len(agent_ids)} agents")
        return agent_ids

    def get_stats(self) -> Dict:
        """Get agent manager statistics"""
        return {
            'total_spawned': self.state['total_spawned'],
            'total_completed': self.state['total_completed'],
            'total_failed': self.state['total_failed'],
            'pending': len([a for a in self.state['agents'].values() if a['status'] == 'pending']),
            'running': len([a for a in self.state['agents'].values() if a['status'] == 'running']),
            'completed': len([a for a in self.state['agents'].values() if a['status'] == 'completed']),
            'failed': len([a for a in self.state['agents'].values() if a['status'] == 'failed']),
        }


def main():
    """Command-line interface"""
    import argparse

    parser = argparse.ArgumentParser(description='Research Agent Manager')
    parser.add_argument('command', choices=['detect', 'process', 'list', 'status', 'stats'],
                       help='Command to execute')
    parser.add_argument('--document', help='Path to document')
    parser.add_argument('--investigation', help='Investigation name')
    parser.add_argument('--agent-id', help='Agent ID for status command')
    parser.add_argument('--filter', help='Filter agents by status (pending/running/completed/failed)')

    args = parser.parse_args()

    manager = AgentManager()

    if args.command == 'detect':
        if not args.document:
            print("Error: --document required for detect command")
            return

        questions = manager.detect_next_steps(args.document)
        print(f"\nFound {len(questions)} questions:")
        for i, q in enumerate(questions, 1):
            print(f"  {i}. {q}")

    elif args.command == 'process':
        if not args.document or not args.investigation:
            print("Error: --document and --investigation required for process command")
            return

        agent_ids = manager.process_document_next_steps(
            args.document,
            args.investigation,
            run_async=False  # Synchronous for CLI
        )

        print(f"\nSpawned {len(agent_ids)} agents:")
        for agent_id in agent_ids:
            print(f"  - {agent_id}")

    elif args.command == 'list':
        agents = manager.list_agents(status=args.filter)
        print(f"\nAgents ({len(agents)}):")
        for agent in agents:
            print(f"\n  Agent: {agent['agent_id']}")
            print(f"    Status: {agent['status']}")
            print(f"    Question: {agent['question'][:60]}...")
            print(f"    Investigation: {agent['investigation']}")

    elif args.command == 'status':
        if not args.agent_id:
            print("Error: --agent-id required for status command")
            return

        status = manager.get_agent_status(args.agent_id)
        if status:
            print(f"\nAgent: {args.agent_id}")
            for key, value in status.items():
                print(f"  {key}: {value}")
        else:
            print(f"Agent not found: {args.agent_id}")

    elif args.command == 'stats':
        stats = manager.get_stats()
        print("\nAgent Manager Statistics:")
        print(f"  Total Spawned: {stats['total_spawned']}")
        print(f"  Completed: {stats['completed']}")
        print(f"  Running: {stats['running']}")
        print(f"  Pending: {stats['pending']}")
        print(f"  Failed: {stats['failed']}")


if __name__ == '__main__':
    main()
