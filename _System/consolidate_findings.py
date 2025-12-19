"""
FINDINGS CONSOLIDATOR - Generate Executive Summary from All Agent Research
Reads all agent findings and creates a single consolidated report
"""

import json
import csv
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class FindingsConsolidator:
    """Consolidate findings from multiple research agents"""

    def __init__(self, investigation: str = "COVID_PCR_Truth_Investigation"):
        self.research_dir = Path(r"C:\Users\jonat\Documents\Research")
        self.investigation = investigation
        self.investigation_dir = self.research_dir / "Active_Investigations" / investigation
        self.agent_findings_dir = self.investigation_dir / "Agent_Findings"

    def load_all_findings(self):
        """Load findings from all agents"""
        all_findings = []

        if not self.agent_findings_dir.exists():
            print(f"[WARN] No agent findings found for {self.investigation}")
            return []

        # Find all findings.json files
        for agent_dir in self.agent_findings_dir.iterdir():
            if agent_dir.is_dir():
                findings_file = agent_dir / "findings.json"
                if findings_file.exists():
                    try:
                        with open(findings_file, 'r', encoding='utf-8') as f:
                            finding = json.load(f)
                            finding['agent_id'] = agent_dir.name
                            all_findings.append(finding)
                    except Exception as e:
                        print(f"[WARN] Could not load {findings_file}: {e}")

        return all_findings

    def consolidate_entities(self, findings_list):
        """Extract and deduplicate entities"""
        entities = {}

        for finding in findings_list:
            for entity in finding.get('entities', []):
                name = entity.get('name', '')
                if name and len(name) > 2:  # Filter out noise
                    if name not in entities:
                        entities[name] = {
                            'name': name,
                            'type': entity.get('type', 'Unknown'),
                            'mentions': 1,
                            'sources': []
                        }
                    else:
                        entities[name]['mentions'] += 1

                    # Track which agents found this
                    entities[name]['sources'].append(finding.get('agent_id', 'unknown'))

        # Sort by mentions (most mentioned first)
        sorted_entities = sorted(entities.values(), key=lambda x: x['mentions'], reverse=True)
        return sorted_entities

    def consolidate_timeline(self, findings_list):
        """Extract and sort timeline events"""
        events = []

        for finding in findings_list:
            for event in finding.get('timeline_events', []):
                events.append({
                    'date': event.get('date', 'Unknown'),
                    'description': event.get('event', 'No description'),
                    'context': event.get('context', ''),
                    'source_agent': finding.get('agent_id', 'unknown')
                })

        # Sort by date
        events.sort(key=lambda x: x['date'], reverse=True)
        return events

    def consolidate_glossary(self, findings_list):
        """Extract glossary terms"""
        terms = {}

        for finding in findings_list:
            for term in finding.get('glossary_terms', []):
                term_name = term.get('term', '')
                if term_name and term_name not in terms:
                    terms[term_name] = {
                        'term': term_name,
                        'definition': term.get('definition', 'No definition'),
                        'context': term.get('context', '')
                    }

        return list(terms.values())

    def extract_sources(self, findings_list):
        """Extract all unique sources"""
        sources = set()

        for finding in findings_list:
            for source in finding.get('sources', []):
                if source.get('url'):
                    sources.add((source.get('title', 'Untitled'), source.get('url')))

        return sorted(list(sources))

    def generate_next_steps(self, findings_list, entities):
        """Suggest next research questions based on findings"""
        suggestions = []

        # Suggest research for top entities
        top_entities = [e['name'] for e in entities[:5] if e['mentions'] > 1]

        if top_entities:
            suggestions.append(f"Deep dive into connections between: {', '.join(top_entities)}")
            suggestions.append(f"Investigate financial records and funding sources for {top_entities[0]}")

        # Suggest based on number of agents
        if len(findings_list) >= 3:
            suggestions.append("Cross-reference findings to identify patterns and contradictions")

        # Generic suggestions
        suggestions.append("Search for whistleblower testimonies or leaked documents")
        suggestions.append("Analyze regulatory filings and public disclosures")

        return suggestions

    def generate_html_report(self, findings_list, entities, timeline, glossary, sources, next_steps):
        """Generate beautiful HTML report"""

        total_agents = len(findings_list)
        total_entities = len(entities)
        total_events = len(timeline)
        total_terms = len(glossary)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Consolidated Research Report - {self.investigation}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0a0e14 0%, #1a2332 100%);
            color: #e6edf3;
            padding: 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.03);
            padding: 40px;
            border-radius: 15px;
        }}
        header {{
            background: linear-gradient(135deg, #00d9ff 0%, #00ff9f 100%);
            color: #0a0e14;
            padding: 40px;
            border-radius: 10px;
            margin-bottom: 40px;
            text-align: center;
        }}
        h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .subtitle {{
            font-size: 1.2em;
            opacity: 0.8;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .stat-card {{
            background: rgba(0, 217, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #00d9ff;
            text-align: center;
        }}
        .stat-number {{
            font-size: 3em;
            font-weight: bold;
            color: #00d9ff;
            display: block;
        }}
        .stat-label {{
            color: #8b95a1;
            margin-top: 5px;
        }}
        .section {{
            margin-bottom: 40px;
        }}
        h2 {{
            color: #00d9ff;
            font-size: 2em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(0, 217, 255, 0.3);
        }}
        h3 {{
            color: #00ff9f;
            font-size: 1.5em;
            margin-top: 30px;
            margin-bottom: 15px;
        }}
        .entity-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .entity-card {{
            background: rgba(255, 255, 255, 0.05);
            padding: 15px;
            border-radius: 8px;
            border-left: 3px solid #00ff9f;
        }}
        .entity-name {{
            font-weight: bold;
            color: #00ff9f;
            font-size: 1.1em;
            margin-bottom: 5px;
        }}
        .entity-type {{
            color: #00d9ff;
            font-size: 0.9em;
            margin-bottom: 5px;
        }}
        .entity-mentions {{
            color: #8b95a1;
            font-size: 0.85em;
        }}
        .timeline-event {{
            background: rgba(255, 255, 255, 0.05);
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 8px;
            border-left: 3px solid #ffa500;
        }}
        .event-date {{
            color: #ffa500;
            font-weight: bold;
            font-size: 1.1em;
            margin-bottom: 5px;
        }}
        .event-description {{
            color: #e6edf3;
            margin-bottom: 5px;
        }}
        .glossary-term {{
            background: rgba(255, 255, 255, 0.05);
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 8px;
            border-left: 3px solid #ff6b35;
        }}
        .term-name {{
            color: #ff6b35;
            font-weight: bold;
            font-size: 1.1em;
            margin-bottom: 5px;
        }}
        .term-definition {{
            color: #e6edf3;
        }}
        .next-steps {{
            background: rgba(0, 255, 159, 0.1);
            padding: 25px;
            border-radius: 10px;
            border: 2px solid #00ff9f;
        }}
        .next-steps li {{
            margin-bottom: 15px;
            padding-left: 10px;
        }}
        .sources {{
            background: rgba(255, 255, 255, 0.05);
            padding: 20px;
            border-radius: 10px;
        }}
        .sources a {{
            color: #00d9ff;
            text-decoration: none;
            display: block;
            margin-bottom: 10px;
            padding: 5px;
            border-radius: 4px;
            transition: background 0.3s;
        }}
        .sources a:hover {{
            background: rgba(0, 217, 255, 0.1);
        }}
        .agent-card {{
            background: rgba(255, 255, 255, 0.05);
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 8px;
            border-left: 3px solid #00d9ff;
        }}
        .agent-question {{
            color: #e6edf3;
            font-style: italic;
            margin-bottom: 5px;
        }}
        .agent-meta {{
            color: #8b95a1;
            font-size: 0.85em;
        }}
        .timestamp {{
            text-align: center;
            color: #8b95a1;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Consolidated Research Report</h1>
            <div class="subtitle">{self.investigation}</div>
        </header>

        <div class="stats-grid">
            <div class="stat-card">
                <span class="stat-number">{total_agents}</span>
                <div class="stat-label">Research Agents</div>
            </div>
            <div class="stat-card">
                <span class="stat-number">{total_entities}</span>
                <div class="stat-label">Entities Discovered</div>
            </div>
            <div class="stat-card">
                <span class="stat-number">{total_events}</span>
                <div class="stat-label">Timeline Events</div>
            </div>
            <div class="stat-card">
                <span class="stat-number">{total_terms}</span>
                <div class="stat-label">Glossary Terms</div>
            </div>
        </div>

        <div class="section">
            <h2>Executive Summary</h2>
            <p>This consolidated report synthesizes findings from {total_agents} autonomous research agents investigating {self.investigation}. The agents collectively discovered {total_entities} entities, documented {total_events} timeline events, and defined {total_terms} glossary terms.</p>
        </div>

        <div class="section">
            <h2>Research Questions Investigated</h2>
"""

        # Add agent questions
        for i, finding in enumerate(findings_list, 1):
            question = finding.get('research_question', 'No question recorded')
            agent_id = finding.get('agent_id', 'unknown')
            status = finding.get('execution', {}).get('status', 'unknown')

            html += f"""
            <div class="agent-card">
                <div class="agent-question">{i}. {question}</div>
                <div class="agent-meta">Agent: {agent_id} | Status: {status}</div>
            </div>
"""

        html += """
        </div>

        <div class="section">
            <h2>Key Entities Discovered</h2>
            <div class="entity-grid">
"""

        # Add entities
        for entity in entities[:20]:  # Top 20
            html += f"""
                <div class="entity-card">
                    <div class="entity-name">{entity['name']}</div>
                    <div class="entity-type">Type: {entity['type']}</div>
                    <div class="entity-mentions">Mentioned by {entity['mentions']} agent(s)</div>
                </div>
"""

        html += """
            </div>
        </div>
"""

        # Timeline
        if timeline:
            html += """
        <div class="section">
            <h2>Timeline of Events</h2>
"""
            for event in timeline[:20]:  # Top 20 most recent
                html += f"""
            <div class="timeline-event">
                <div class="event-date">{event['date']}</div>
                <div class="event-description">{event['description']}</div>
            </div>
"""
            html += """
        </div>
"""

        # Glossary
        if glossary:
            html += """
        <div class="section">
            <h2>Glossary of Terms</h2>
"""
            for term in glossary:
                html += f"""
            <div class="glossary-term">
                <div class="term-name">{term['term']}</div>
                <div class="term-definition">{term['definition']}</div>
            </div>
"""
            html += """
        </div>
"""

        # Next Steps
        html += """
        <div class="section">
            <h2>Recommended Next Steps</h2>
            <div class="next-steps">
                <ol>
"""
        for step in next_steps:
            html += f"                    <li>{step}</li>\n"

        html += """
                </ol>
            </div>
        </div>
"""

        # Sources
        if sources:
            html += """
        <div class="section">
            <h2>Sources Referenced</h2>
            <div class="sources">
"""
            for title, url in sources:
                html += f'                <a href="{url}" target="_blank">{title}</a>\n'

            html += """
            </div>
        </div>
"""

        # Footer
        html += f"""
        <div class="timestamp">
            Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
            Research Intelligence Platform
        </div>
    </div>
</body>
</html>
"""

        return html

    def consolidate(self):
        """Main consolidation workflow"""
        print(f"\n[INFO] Consolidating findings for: {self.investigation}")

        # Load all findings
        findings_list = self.load_all_findings()

        if not findings_list:
            print("[ERROR] No findings to consolidate")
            return None

        print(f"[OK] Loaded {len(findings_list)} agent findings")

        # Consolidate data
        entities = self.consolidate_entities(findings_list)
        timeline = self.consolidate_timeline(findings_list)
        glossary = self.consolidate_glossary(findings_list)
        sources = self.extract_sources(findings_list)
        next_steps = self.generate_next_steps(findings_list, entities)

        print(f"[OK] Consolidated: {len(entities)} entities, {len(timeline)} events, {len(glossary)} terms")

        # Generate report
        html = self.generate_html_report(findings_list, entities, timeline, glossary, sources, next_steps)

        # Save report
        output_file = self.investigation_dir / "Consolidated_Research_Report.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"[OK] Report saved: {output_file}")
        return output_file


def main():
    """Command-line interface"""
    import argparse

    parser = argparse.ArgumentParser(description='Consolidate research findings')
    parser.add_argument('--investigation', default='COVID_PCR_Truth_Investigation',
                        help='Investigation name')
    parser.add_argument('--open', action='store_true',
                        help='Open report in browser after generation')

    args = parser.parse_args()

    consolidator = FindingsConsolidator(investigation=args.investigation)
    output_file = consolidator.consolidate()

    if output_file and args.open:
        import subprocess
        subprocess.run(['cmd', '/c', 'start', '', str(output_file)])


if __name__ == '__main__':
    main()
