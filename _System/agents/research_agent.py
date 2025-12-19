"""
RESEARCH AGENT BASE CLASS
Foundation for all automated research agents
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from abc import ABC, abstractmethod


class ResearchAgent(ABC):
    """
    Base class for all research agents

    All agents inherit from this and implement execute_research()
    """

    def __init__(self, agent_id: str, question: str, investigation: str,
                 research_dir: str = None):
        """
        Initialize research agent

        Args:
            agent_id: Unique identifier for this agent
            question: Research question to answer
            investigation: Which investigation this belongs to
            research_dir: Root research directory
        """
        if research_dir is None:
            research_dir = r"C:\Users\jonat\Documents\Research"

        self.agent_id = agent_id
        self.question = question
        self.investigation = investigation
        self.research_dir = Path(research_dir)

        # Setup paths
        self.investigation_dir = self.research_dir / 'Active_Investigations' / investigation
        self.findings_dir = self.investigation_dir / 'Agent_Findings' / agent_id
        self.findings_dir.mkdir(parents=True, exist_ok=True)

        # Initialize findings structure
        self.findings = {
            'agent_id': agent_id,
            'question': question,
            'parent_investigation': investigation,
            'execution': {
                'started': None,
                'completed': None,
                'status': 'pending'
            },
            'findings': {
                'summary': '',
                'entities_discovered': [],
                'glossary_terms': [],
                'timeline_events': [],
                'sources': [],
                'cross_references': []
            },
            'integration_status': {
                'entities_integrated': False,
                'glossary_integrated': False,
                'timeline_integrated': False,
                'integrated_at': None
            }
        }

    @abstractmethod
    def execute_research(self) -> Dict:
        """
        Execute the research

        This method must be implemented by all subclasses
        Returns dict with research results
        """
        pass

    def execute(self) -> Dict:
        """
        Main execution pipeline:
        1. Start tracking
        2. Execute research (subclass implements this)
        3. Extract entities, events, terms
        4. Save findings
        5. Return results
        """
        print(f"\n[AGENT {self.agent_id}] Starting research...")
        print(f"Question: {self.question}")

        # Start tracking
        self.findings['execution']['started'] = datetime.now().isoformat()
        self.findings['execution']['status'] = 'running'

        try:
            # Execute research (subclass-specific logic)
            research_results = self.execute_research()

            # Extract structured data from results
            if research_results.get('content'):
                content = research_results['content']

                # Extract entities
                entities = self.extract_entities(content)
                self.findings['findings']['entities_discovered'] = entities
                print(f"[AGENT {self.agent_id}] Extracted {len(entities)} entities")

                # Extract timeline events
                events = self.extract_timeline_events(content)
                self.findings['findings']['timeline_events'] = events
                print(f"[AGENT {self.agent_id}] Extracted {len(events)} events")

                # Extract glossary terms (basic implementation)
                terms = self.extract_glossary_terms(content)
                self.findings['findings']['glossary_terms'] = terms
                print(f"[AGENT {self.agent_id}] Extracted {len(terms)} terms")

                # Store sources
                if research_results.get('sources'):
                    self.findings['findings']['sources'] = research_results['sources']

                # Summary
                self.findings['findings']['summary'] = research_results.get('summary', content[:500])

            # Mark as completed
            self.findings['execution']['completed'] = datetime.now().isoformat()
            self.findings['execution']['status'] = 'completed'

            # Save findings
            self.save_findings()

            print(f"[AGENT {self.agent_id}] Research completed successfully")
            return self.findings

        except Exception as e:
            print(f"[AGENT {self.agent_id}] Error: {str(e)}")
            self.findings['execution']['status'] = 'failed'
            self.findings['execution']['error'] = str(e)
            self.findings['execution']['completed'] = datetime.now().isoformat()
            self.save_findings()
            raise

    def extract_entities(self, content: str) -> List[Dict]:
        """
        Extract entities from content

        Uses capitalization patterns + known entity types
        """
        entities = []

        # Pattern: Capitalized words (potential proper nouns)
        # Look for sequences of 1-4 capitalized words
        pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})\b'
        matches = re.findall(pattern, content)

        # Count frequency
        entity_counts = {}
        for match in matches:
            entity_counts[match] = entity_counts.get(match, 0) + 1

        # Filter: only keep entities mentioned 2+ times or known types
        known_types = {
            'Corporation', 'Organization', 'Government', 'Institution',
            'Person', 'Agency', 'Company', 'Technology'
        }

        for entity_name, count in entity_counts.items():
            if count >= 2 or any(t in entity_name for t in known_types):
                # Determine entity type (basic heuristic)
                entity_type = self._classify_entity(entity_name)

                entities.append({
                    'name': entity_name,
                    'type': entity_type,
                    'role': f'Mentioned {count} times in research',
                    'description': f'Entity discovered during research on: {self.question}',
                    'connections': '',
                    'first_mentioned': datetime.now().strftime('%Y-%m-%d'),
                    'source': f'Agent {self.agent_id}'
                })

        return entities[:20]  # Limit to top 20

    def _classify_entity(self, name: str) -> str:
        """Basic entity type classification"""
        if any(word in name.lower() for word in ['corporation', 'corp', 'inc', 'llc', 'ltd']):
            return 'Corporation'
        elif any(word in name.lower() for word in ['fda', 'cdc', 'who', 'nih', 'agency']):
            return 'Government'
        elif any(word in name.lower() for word in ['university', 'institute', 'lab', 'center']):
            return 'Institution'
        else:
            return 'Organization'

    def extract_timeline_events(self, content: str) -> List[Dict]:
        """
        Extract timeline events from content

        Looks for dates + surrounding context
        """
        events = []

        # Pattern: Various date formats
        date_patterns = [
            r'\b(\d{4}-\d{2}-\d{2})\b',  # 2025-12-19
            r'\b([A-Z][a-z]+ \d{1,2}, \d{4})\b',  # December 19, 2025
            r'\b(\d{1,2}/\d{1,2}/\d{4})\b',  # 12/19/2025
            r'\b([A-Z][a-z]+ \d{4})\b',  # December 2025
        ]

        for pattern in date_patterns:
            matches = re.finditer(pattern, content)

            for match in matches:
                date_str = match.group(1)

                # Get context around the date (100 chars before/after)
                start = max(0, match.start() - 100)
                end = min(len(content), match.end() + 100)
                context = content[start:end]

                # Extract a title from the context (sentence containing the date)
                sentences = re.split(r'[.!?]', context)
                title = next((s.strip() for s in sentences if date_str in s), context[:100])

                events.append({
                    'date': date_str,
                    'title': title[:100],
                    'description': context,
                    'event_type': 'discovery',
                    'entities_involved': [],  # TODO: Link to extracted entities
                    'sources': [{
                        'source_id': self.agent_id,
                        'citation': f'Research Agent {self.agent_id}',
                        'reliability': 'automated'
                    }],
                    'created_by': self.agent_id
                })

        return events[:15]  # Limit to top 15

    def extract_glossary_terms(self, content: str) -> List[Dict]:
        """
        Extract potential glossary terms

        Looks for: acronyms, technical terms, defined terms
        """
        terms = []

        # Pattern 1: Acronyms in parentheses: "Something (ABC)"
        acronym_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\(([A-Z]{2,})\)'
        acronym_matches = re.findall(acronym_pattern, content)

        for full_term, acronym in acronym_matches:
            # Get context for definition
            pattern = re.escape(f'{full_term} ({acronym})')
            match = re.search(pattern + r'([^.!?]*[.!?])', content)
            definition = match.group(1) if match else f'{full_term}'

            terms.append({
                'term': acronym,
                'definition': definition[:200],
                'category': 'acronym',
                'source': f'Agent {self.agent_id}',
                'first_mentioned': datetime.now().strftime('%Y-%m-%d')
            })

        # Pattern 2: Defined terms: "X is defined as..." or "X means..."
        definition_pattern = r'([A-Z][a-z]+(?:\s+[A-Z]?[a-z]+)*)\s+(?:is defined as|means|refers to)\s+([^.!?]+[.!?])'
        definition_matches = re.findall(definition_pattern, content)

        for term, definition in definition_matches:
            terms.append({
                'term': term,
                'definition': definition[:200],
                'category': 'technical',
                'source': f'Agent {self.agent_id}',
                'first_mentioned': datetime.now().strftime('%Y-%m-%d')
            })

        return terms[:10]  # Limit to top 10

    def save_findings(self):
        """Save findings to JSON file"""
        findings_file = self.findings_dir / 'findings.json'

        with open(findings_file, 'w') as f:
            json.dump(self.findings, f, indent=2)

        print(f"[AGENT {self.agent_id}] Saved findings to {findings_file}")

        # Also save a human-readable summary
        summary_file = self.findings_dir / 'summary.md'
        self._save_summary_markdown(summary_file)

    def _save_summary_markdown(self, filepath: Path):
        """Save human-readable summary"""
        content = f"""# Research Agent Summary

**Agent ID:** {self.agent_id}
**Question:** {self.question}
**Investigation:** {self.investigation}
**Status:** {self.findings['execution']['status']}
**Started:** {self.findings['execution']['started']}
**Completed:** {self.findings['execution']['completed']}

## Summary

{self.findings['findings']['summary']}

## Entities Discovered ({len(self.findings['findings']['entities_discovered'])})

"""
        for entity in self.findings['findings']['entities_discovered']:
            content += f"- **{entity['name']}** ({entity['type']}): {entity['description']}\n"

        content += f"\n## Timeline Events ({len(self.findings['findings']['timeline_events'])})\n\n"

        for event in self.findings['findings']['timeline_events']:
            content += f"- **{event['date']}**: {event['title']}\n"

        content += f"\n## Glossary Terms ({len(self.findings['findings']['glossary_terms'])})\n\n"

        for term in self.findings['findings']['glossary_terms']:
            content += f"- **{term['term']}**: {term['definition']}\n"

        content += "\n---\n\n*Generated by Research Agent System*\n"

        with open(filepath, 'w') as f:
            f.write(content)


if __name__ == '__main__':
    # Base class cannot be instantiated directly
    print("ResearchAgent is an abstract base class.")
    print("Create a subclass like WebResearchAgent instead.")
