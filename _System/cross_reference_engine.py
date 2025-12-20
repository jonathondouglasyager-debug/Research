"""
CROSS-REFERENCE ENGINE - Link Entities Across Documents and Investigations
Tracks entity appearances, co-occurrences, and cross-investigation connections
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set
from collections import defaultdict
import csv

class CrossReferenceEngine:
    """Track and analyze entity relationships across the entire research system"""

    def __init__(self):
        self.research_dir = Path(r"C:\Users\jonat\Documents\Research")
        self.intelligence_dir = self.research_dir / "_Intelligence"
        self.intelligence_dir.mkdir(parents=True, exist_ok=True)

        # Cross-reference database
        self.xref_file = self.intelligence_dir / "cross_references.json"

    def load_cross_references(self) -> Dict:
        """Load cross-reference database"""
        if self.xref_file.exists():
            try:
                with open(self.xref_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self._initialize_xref_db()
        return self._initialize_xref_db()

    def _initialize_xref_db(self) -> Dict:
        """Initialize empty cross-reference database"""
        return {
            "entities": {},  # entity_name -> {investigations: [], documents: [], co_occurrences: {}}
            "investigations": {},  # investigation -> {entities: [], entity_count: N}
            "documents": {},  # document -> {entities: [], investigation: str}
            "co_occurrences": {},  # (entity1, entity2) -> count
            "metadata": {
                "last_updated": datetime.now().isoformat(),
                "total_entities": 0,
                "total_investigations": 0,
                "total_documents": 0
            }
        }

    def save_cross_references(self, xref_db: Dict):
        """Save cross-reference database"""
        with open(self.xref_file, 'w', encoding='utf-8') as f:
            json.dump(xref_db, f, indent=2, ensure_ascii=False)

    def update_from_agent_findings(self, findings_path: str) -> Dict:
        """Update cross-references from agent findings"""

        findings_file = Path(findings_path)
        if not findings_file.exists():
            return {"status": "error", "message": "Findings file not found"}

        try:
            with open(findings_file, 'r', encoding='utf-8') as f:
                findings = json.load(f)

            agent_id = findings['agent_id']
            investigation = findings['parent_investigation']
            entities_discovered = findings['findings'].get('entities_discovered', [])

            # Extract entity names
            entity_names = [e['name'] for e in entities_discovered if e.get('name')]

            # Update cross-references
            stats = self.add_document_entities(
                document_id=agent_id,
                investigation=investigation,
                entity_names=entity_names
            )

            return stats

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def add_document_entities(self, document_id: str, investigation: str, entity_names: List[str]) -> Dict:
        """Add entities from a document to cross-reference database"""

        xref_db = self.load_cross_references()

        stats = {
            "entities_added": 0,
            "entities_updated": 0,
            "new_co_occurrences": 0
        }

        # Filter out noise entities
        entity_names = [e for e in entity_names if len(e) > 2 and e not in ['This', 'Agent', 'Provide', 'Investigate']]

        # Update entities
        for entity in entity_names:
            if entity not in xref_db["entities"]:
                xref_db["entities"][entity] = {
                    "investigations": set(),
                    "documents": set(),
                    "co_occurrences": {},
                    "first_seen": datetime.now().isoformat()
                }
                stats["entities_added"] += 1
            else:
                stats["entities_updated"] += 1

            # Add investigation and document (using sets to avoid duplicates)
            xref_db["entities"][entity]["investigations"].add(investigation)
            xref_db["entities"][entity]["documents"].add(document_id)
            xref_db["entities"][entity]["last_updated"] = datetime.now().isoformat()

        # Update co-occurrences (entities appearing together)
        for i, entity1 in enumerate(entity_names):
            for entity2 in entity_names[i+1:]:
                # Create sorted pair to avoid duplicates (A,B) vs (B,A)
                pair = tuple(sorted([entity1, entity2]))
                pair_key = f"{pair[0]}|{pair[1]}"

                if pair_key not in xref_db["co_occurrences"]:
                    xref_db["co_occurrences"][pair_key] = {
                        "entities": pair,
                        "count": 0,
                        "investigations": set(),
                        "documents": set()
                    }
                    stats["new_co_occurrences"] += 1

                xref_db["co_occurrences"][pair_key]["count"] += 1
                xref_db["co_occurrences"][pair_key]["investigations"].add(investigation)
                xref_db["co_occurrences"][pair_key]["documents"].add(document_id)

                # Track in entity records
                if entity2 not in xref_db["entities"][entity1]["co_occurrences"]:
                    xref_db["entities"][entity1]["co_occurrences"][entity2] = 0
                if entity1 not in xref_db["entities"][entity2]["co_occurrences"]:
                    xref_db["entities"][entity2]["co_occurrences"][entity1] = 0

                xref_db["entities"][entity1]["co_occurrences"][entity2] += 1
                xref_db["entities"][entity2]["co_occurrences"][entity1] += 1

        # Update investigation index
        if investigation not in xref_db["investigations"]:
            xref_db["investigations"][investigation] = {
                "entities": set(),
                "documents": set(),
                "created": datetime.now().isoformat()
            }

        for entity in entity_names:
            xref_db["investigations"][investigation]["entities"].add(entity)
        xref_db["investigations"][investigation]["documents"].add(document_id)
        xref_db["investigations"][investigation]["last_updated"] = datetime.now().isoformat()

        # Update document index
        xref_db["documents"][document_id] = {
            "investigation": investigation,
            "entities": list(set(entity_names)),
            "entity_count": len(set(entity_names)),
            "timestamp": datetime.now().isoformat()
        }

        # Convert sets to lists for JSON serialization
        for entity in xref_db["entities"]:
            xref_db["entities"][entity]["investigations"] = list(xref_db["entities"][entity]["investigations"])
            xref_db["entities"][entity]["documents"] = list(xref_db["entities"][entity]["documents"])

        for investigation in xref_db["investigations"]:
            xref_db["investigations"][investigation]["entities"] = list(xref_db["investigations"][investigation]["entities"])
            xref_db["investigations"][investigation]["documents"] = list(xref_db["investigations"][investigation]["documents"])

        for pair_key in xref_db["co_occurrences"]:
            xref_db["co_occurrences"][pair_key]["investigations"] = list(xref_db["co_occurrences"][pair_key]["investigations"])
            xref_db["co_occurrences"][pair_key]["documents"] = list(xref_db["co_occurrences"][pair_key]["documents"])

        # Update metadata
        xref_db["metadata"] = {
            "last_updated": datetime.now().isoformat(),
            "total_entities": len(xref_db["entities"]),
            "total_investigations": len(xref_db["investigations"]),
            "total_documents": len(xref_db["documents"]),
            "total_co_occurrences": len(xref_db["co_occurrences"])
        }

        # Save
        self.save_cross_references(xref_db)

        return stats

    def find_entity_connections(self, entity_name: str) -> Dict:
        """Find all connections for an entity"""
        xref_db = self.load_cross_references()

        if entity_name not in xref_db["entities"]:
            return {"found": False, "entity": entity_name}

        entity_data = xref_db["entities"][entity_name]

        return {
            "found": True,
            "entity": entity_name,
            "investigations": entity_data["investigations"],
            "document_count": len(entity_data["documents"]),
            "co_occurrences": entity_data["co_occurrences"],
            "related_entities": sorted(entity_data["co_occurrences"].items(), key=lambda x: x[1], reverse=True)
        }

    def find_cross_investigation_entities(self) -> List[Dict]:
        """Find entities that appear in multiple investigations"""
        xref_db = self.load_cross_references()

        cross_investigation = []
        for entity, data in xref_db["entities"].items():
            if len(data["investigations"]) > 1:
                cross_investigation.append({
                    "entity": entity,
                    "investigation_count": len(data["investigations"]),
                    "investigations": data["investigations"],
                    "document_count": len(data["documents"])
                })

        # Sort by investigation count
        cross_investigation.sort(key=lambda x: x["investigation_count"], reverse=True)
        return cross_investigation

    def find_strongest_connections(self, min_count: int = 2) -> List[Dict]:
        """Find entity pairs with strongest co-occurrence"""
        xref_db = self.load_cross_references()

        strong_connections = []
        for pair_key, data in xref_db["co_occurrences"].items():
            if data["count"] >= min_count:
                strong_connections.append({
                    "entity1": data["entities"][0],
                    "entity2": data["entities"][1],
                    "count": data["count"],
                    "investigations": data["investigations"],
                    "document_count": len(data["documents"])
                })

        # Sort by count
        strong_connections.sort(key=lambda x: x["count"], reverse=True)
        return strong_connections

    def export_cross_reference_report(self, filepath: Path = None):
        """Export comprehensive cross-reference report as HTML"""

        xref_db = self.load_cross_references()
        output_file = filepath or (self.intelligence_dir / "cross_reference_report.html")

        metadata = xref_db.get("metadata", {})
        cross_inv_entities = self.find_cross_investigation_entities()
        strong_connections = self.find_strongest_connections(min_count=2)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cross-Reference Report</title>
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
            max-width: 1400px;
            margin: 0 auto;
        }}
        header {{
            background: linear-gradient(135deg, #ff6b35 0%, #ffa500 100%);
            color: #0a0e14;
            padding: 40px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: rgba(255, 107, 53, 0.1);
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #ff6b35;
            text-align: center;
        }}
        .stat-number {{
            font-size: 3em;
            font-weight: bold;
            color: #ffa500;
            display: block;
        }}
        .stat-label {{
            color: #8b95a1;
            margin-top: 5px;
        }}
        .section {{
            background: rgba(255, 255, 255, 0.03);
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        h2 {{
            color: #ffa500;
            font-size: 2em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(255, 165, 0, 0.3);
        }}
        .entity-card {{
            background: rgba(255, 255, 255, 0.05);
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 8px;
            border-left: 3px solid #ff6b35;
        }}
        .entity-name {{
            font-weight: bold;
            color: #ffa500;
            font-size: 1.2em;
            margin-bottom: 5px;
        }}
        .entity-meta {{
            color: #8b95a1;
            font-size: 0.9em;
        }}
        .connection-card {{
            background: rgba(255, 255, 255, 0.05);
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 8px;
            border-left: 3px solid #00d9ff;
        }}
        .connection-pair {{
            color: #00d9ff;
            font-weight: bold;
            font-size: 1.1em;
            margin-bottom: 5px;
        }}
        .badge {{
            display: inline-block;
            background: rgba(255, 165, 0, 0.2);
            color: #ffa500;
            padding: 4px 10px;
            border-radius: 4px;
            margin-right: 5px;
            margin-top: 5px;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Cross-Reference Report</h1>
            <p>Entity Connections Across All Research</p>
        </header>

        <div class="stats-grid">
            <div class="stat-card">
                <span class="stat-number">{metadata.get('total_entities', 0)}</span>
                <div class="stat-label">Total Entities</div>
            </div>
            <div class="stat-card">
                <span class="stat-number">{metadata.get('total_investigations', 0)}</span>
                <div class="stat-label">Investigations</div>
            </div>
            <div class="stat-card">
                <span class="stat-number">{metadata.get('total_documents', 0)}</span>
                <div class="stat-label">Documents</div>
            </div>
            <div class="stat-card">
                <span class="stat-number">{metadata.get('total_co_occurrences', 0)}</span>
                <div class="stat-label">Co-occurrences</div>
            </div>
        </div>

        <div class="section">
            <h2>Cross-Investigation Entities</h2>
            <p style="color: #8b95a1; margin-bottom: 20px;">Entities appearing in multiple investigations</p>
"""

        for entity_data in cross_inv_entities[:20]:
            html += f"""
            <div class="entity-card">
                <div class="entity-name">{entity_data['entity']}</div>
                <div class="entity-meta">
                    {entity_data['investigation_count']} investigations | {entity_data['document_count']} documents
                </div>
                <div>
"""
            for inv in entity_data['investigations']:
                html += f'                    <span class="badge">{inv}</span>\n'

            html += """
                </div>
            </div>
"""

        html += """
        </div>

        <div class="section">
            <h2>Strongest Entity Connections</h2>
            <p style="color: #8b95a1; margin-bottom: 20px;">Entity pairs frequently appearing together</p>
"""

        for conn in strong_connections[:20]:
            html += f"""
            <div class="connection-card">
                <div class="connection-pair">{conn['entity1']} ↔ {conn['entity2']}</div>
                <div class="entity-meta">
                    Co-occurred {conn['count']} times | {len(conn['investigations'])} investigations
                </div>
                <div>
"""
            for inv in conn['investigations']:
                html += f'                    <span class="badge">{inv}</span>\n'

            html += """
                </div>
            </div>
"""

        html += f"""
        </div>

        <div style="text-align: center; color: #8b95a1; margin-top: 40px;">
            Last Updated: {metadata.get('last_updated', 'Unknown')}
        </div>
    </div>
</body>
</html>
"""

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        return output_file


def main():
    """Command-line interface"""
    import argparse

    parser = argparse.ArgumentParser(description='Cross-Reference Engine')
    parser.add_argument('command', choices=['update', 'report', 'search'],
                       help='Command to execute')
    parser.add_argument('--findings', help='Path to findings.json for update command')
    parser.add_argument('--entity', help='Entity name to search')

    args = parser.parse_args()

    engine = CrossReferenceEngine()

    if args.command == 'update':
        if not args.findings:
            print("Error: --findings required for update command")
            return

        stats = engine.update_from_agent_findings(args.findings)
        print(f"[OK] Cross-references updated:")
        print(f"  - Entities added: {stats.get('entities_added', 0)}")
        print(f"  - Entities updated: {stats.get('entities_updated', 0)}")
        print(f"  - New co-occurrences: {stats.get('new_co_occurrences', 0)}")

    elif args.command == 'report':
        output = engine.export_cross_reference_report()
        print(f"[OK] Cross-reference report generated: {output}")

    elif args.command == 'search':
        if not args.entity:
            print("Error: --entity required for search command")
            return

        result = engine.find_entity_connections(args.entity)
        if result['found']:
            print(f"\n[FOUND] {result['entity']}")
            print(f"Investigations: {', '.join(result['investigations'])}")
            print(f"Documents: {result['document_count']}")
            print(f"\nRelated Entities:")
            for related, count in result['related_entities'][:10]:
                print(f"  - {related}: {count} co-occurrences")
        else:
            print(f"[NOT FOUND] {args.entity}")


if __name__ == '__main__':
    main()
