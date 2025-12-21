"""
INTERACTIVE DOCUMENT VIEWER - Phase 3
Converts markdown research documents into rich interactive HTML with:
- Entity hover tooltips (from entity database)
- Glossary term popups (from glossary)
- Clickable source citations
- Links to timeline events
- Links to network visualization
"""

import json
import csv
import re
from pathlib import Path
from typing import Dict, List, Set
import markdown

class InteractiveDocumentViewer:
    """Convert markdown research documents to interactive HTML"""

    def __init__(self, investigation: str):
        self.research_dir = Path(r"C:\Users\jonat\Documents\Research")
        self.investigation = investigation
        self.investigation_dir = self.research_dir / "Active_Investigations" / investigation

        # Load data for interactive features
        self.entities = self._load_entities()
        self.glossary = self._load_glossary()
        self.timeline_events = self._load_timeline()

    def _load_entities(self) -> Dict[str, Dict]:
        """Load entity database"""
        entities = {}
        entity_file = self.investigation_dir / "entity_database.csv"

        if entity_file.exists():
            with open(entity_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    entities[row['Entity_Name']] = row

        return entities

    def _load_glossary(self) -> Dict[str, Dict]:
        """Load glossary terms"""
        glossary_file = self.investigation_dir / "glossary.json"

        if glossary_file.exists():
            with open(glossary_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Convert to dict with lowercase keys for easy lookup
                return {term.lower(): term_data for term, term_data in data.get('terms', {}).items()}

        return {}

    def _load_timeline(self) -> List[Dict]:
        """Load timeline events"""
        timeline_file = self.investigation_dir / "timeline.json"

        if timeline_file.exists():
            with open(timeline_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('events', [])

        return []

    def process_markdown_special_syntax(self, content: str) -> str:
        """
        Process special markdown syntax:
        [[Entity Name]] -> entity link with tooltip
        [[term]] -> glossary term with definition
        [[src_123]] -> source citation
        """

        # Pattern: [[text]]
        def replace_bracket_link(match):
            text = match.group(1)

            # Check if it's a source citation
            if text.startswith('src_'):
                return self._create_source_link(text)

            # Check if it's an entity (capitalized)
            if text in self.entities:
                return self._create_entity_link(text)

            # Check if it's a glossary term
            if text.lower() in self.glossary:
                return self._create_glossary_link(text)

            # Default: just return as bold text
            return f"<strong>{text}</strong>"

        # Replace [[...]] syntax
        content = re.sub(r'\[\[([^\]]+)\]\]', replace_bracket_link, content)

        return content

    def auto_detect_entities(self, html_content: str) -> str:
        """
        Auto-detect entity names in HTML and make them interactive
        (Only exact matches, case-sensitive)
        """

        # Sort entities by length (longest first) to avoid partial replacements
        sorted_entities = sorted(self.entities.keys(), key=len, reverse=True)

        for entity_name in sorted_entities:
            # Only replace whole words, case-sensitive
            pattern = r'\b' + re.escape(entity_name) + r'\b'

            # Replace with entity link (but not if already inside an HTML tag)
            def replace_if_not_in_tag(match):
                # Simple check: if we're inside <...>, don't replace
                return self._create_entity_link(entity_name)

            # This is a simplified version - in production would need more robust HTML parsing
            # For now, just do basic replacement
            html_content = re.sub(pattern, self._create_entity_link(entity_name), html_content, count=3)  # Limit replacements per entity

        return html_content

    def _create_entity_link(self, entity_name: str) -> str:
        """Create interactive entity link with tooltip"""
        entity_data = self.entities.get(entity_name, {})

        # Build tooltip content
        tooltip = f"<strong>{entity_name}</strong><br>"
        tooltip += f"Type: {entity_data.get('Entity_Type', 'Unknown')}<br>"

        description = entity_data.get('Description', 'No description')
        if len(description) > 150:
            description = description[:150] + "..."
        tooltip += f"{description}"

        # Escape quotes for HTML attribute
        tooltip = tooltip.replace('"', '&quot;').replace("'", '&#39;')

        return f'<span class="entity-link" data-entity="{entity_name}" title="{tooltip}" onclick="showEntityDetails(\'{entity_name}\')">{entity_name}</span>'

    def _create_glossary_link(self, term: str) -> str:
        """Create interactive glossary term link"""
        term_data = self.glossary.get(term.lower(), {})

        definition = term_data.get('definition', 'No definition available')
        tooltip = f"<strong>{term}</strong><br>{definition[:200]}"

        tooltip = tooltip.replace('"', '&quot;').replace("'", '&#39;')

        return f'<span class="glossary-term" data-term="{term}" title="{tooltip}">{term}</span>'

    def _create_source_link(self, source_id: str) -> str:
        """Create clickable source citation"""
        return f'<sup class="source-link" data-source="{source_id}" onclick="showSource(\'{source_id}\')">[{source_id.replace("src_", "")}]</sup>'

    def convert_document(self, markdown_file: Path) -> Path:
        """
        Convert markdown document to interactive HTML

        Args:
            markdown_file: Path to markdown file

        Returns:
            Path to generated HTML file
        """

        # Read markdown
        with open(markdown_file, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # Process special syntax first
        md_content = self.process_markdown_special_syntax(md_content)

        # Convert markdown to HTML
        html_content = markdown.markdown(md_content, extensions=['extra', 'codehilite'])

        # Auto-detect entities in content
        # html_content = self.auto_detect_entities(html_content)

        # Generate complete HTML page
        full_html = self._generate_html_page(html_content, markdown_file.stem)

        # Save HTML
        output_file = markdown_file.parent / f"{markdown_file.stem}_interactive.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_html)

        return output_file

    def _generate_html_page(self, content_html: str, title: str) -> str:
        """Generate complete HTML page with interactive features"""

        # Build entity database for JavaScript
        entities_json = json.dumps(self.entities)
        glossary_json = json.dumps({k: v for k, v in self.glossary.items()})

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Interactive Research Document</title>
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
            line-height: 1.8;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.03);
            padding: 50px;
            border-radius: 15px;
            box-shadow: 0 10px 50px rgba(0, 0, 0, 0.5);
        }}
        h1 {{
            color: #00d9ff;
            font-size: 2.5em;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 3px solid rgba(0, 217, 255, 0.3);
        }}
        h2 {{
            color: #00ff9f;
            font-size: 2em;
            margin-top: 40px;
            margin-bottom: 20px;
        }}
        h3 {{
            color: #ffa500;
            font-size: 1.5em;
            margin-top: 30px;
            margin-bottom: 15px;
        }}
        p {{
            margin-bottom: 20px;
            line-height: 1.8;
        }}
        .entity-link {{
            color: #00d9ff;
            font-weight: bold;
            cursor: pointer;
            border-bottom: 2px dotted #00d9ff;
            transition: all 0.2s;
            position: relative;
        }}
        .entity-link:hover {{
            color: #00ff9f;
            border-bottom-color: #00ff9f;
            background: rgba(0, 217, 255, 0.1);
            padding: 2px 4px;
            border-radius: 3px;
        }}
        .glossary-term {{
            color: #ffa500;
            font-weight: 500;
            cursor: help;
            border-bottom: 1px dotted #ffa500;
        }}
        .glossary-term:hover {{
            background: rgba(255, 165, 0, 0.1);
            padding: 2px 4px;
            border-radius: 3px;
        }}
        .source-link {{
            color: #ff6b35;
            cursor: pointer;
            font-weight: bold;
        }}
        .source-link:hover {{
            color: #ffa500;
        }}
        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
        }}
        .modal-content {{
            background: linear-gradient(135deg, #1a2332 0%, #2a3342 100%);
            margin: 10% auto;
            padding: 40px;
            border: 2px solid #00d9ff;
            border-radius: 15px;
            width: 80%;
            max-width: 700px;
            box-shadow: 0 20px 60px rgba(0, 217, 255, 0.3);
        }}
        .close {{
            color: #8b95a1;
            float: right;
            font-size: 35px;
            font-weight: bold;
            cursor: pointer;
            line-height: 0.8;
        }}
        .close:hover {{
            color: #00d9ff;
        }}
        .entity-detail {{
            margin-top: 20px;
        }}
        .entity-detail-row {{
            margin-bottom: 15px;
            padding: 10px;
            background: rgba(0, 217, 255, 0.05);
            border-radius: 5px;
        }}
        .entity-detail-label {{
            color: #00d9ff;
            font-weight: bold;
            margin-right: 10px;
        }}
        .nav-links {{
            margin-top: 30px;
            padding: 20px;
            background: rgba(0, 217, 255, 0.1);
            border-radius: 10px;
            text-align: center;
        }}
        .nav-links a {{
            color: #00d9ff;
            text-decoration: none;
            margin: 0 15px;
            padding: 8px 16px;
            border: 2px solid #00d9ff;
            border-radius: 5px;
            display: inline-block;
            transition: all 0.3s;
        }}
        .nav-links a:hover {{
            background: #00d9ff;
            color: #0a0e14;
        }}
        ul, ol {{
            margin-left: 30px;
            margin-bottom: 20px;
        }}
        li {{
            margin-bottom: 10px;
        }}
        code {{
            background: rgba(0, 0, 0, 0.3);
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        blockquote {{
            border-left: 4px solid #00d9ff;
            padding-left: 20px;
            margin: 20px 0;
            color: #8b95a1;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="container">
        {content_html}

        <div class="nav-links">
            <a href="Consolidated_Research_Report.html">📊 Full Report</a>
            <a href="timeline.html">📅 Timeline</a>
            <a href="Knowledge_Graph/network_visualization.html">🕸️ Network</a>
            <a href="glossary.md">📖 Glossary</a>
            <a href="../../RESEARCH_INDEX.html">🏠 Home</a>
        </div>
    </div>

    <!-- Entity Detail Modal -->
    <div id="entityModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal()">&times;</span>
            <div id="entityDetails"></div>
        </div>
    </div>

    <script>
        // Entity and glossary data
        const entities = {entities_json};
        const glossary = {glossary_json};

        function showEntityDetails(entityName) {{
            const entity = entities[entityName];
            if (!entity) return;

            let html = `<h2 style="color: #00d9ff;">${{entityName}}</h2>`;
            html += '<div class="entity-detail">';

            html += `<div class="entity-detail-row">
                <span class="entity-detail-label">Type:</span>
                ${{entity.Entity_Type || 'Unknown'}}
            </div>`;

            html += `<div class="entity-detail-row">
                <span class="entity-detail-label">Description:</span>
                ${{entity.Description || 'No description'}}
            </div>`;

            if (entity.Role) {{
                html += `<div class="entity-detail-row">
                    <span class="entity-detail-label">Role:</span>
                    ${{entity.Role}}
                </div>`;
            }}

            if (entity.Connections) {{
                html += `<div class="entity-detail-row">
                    <span class="entity-detail-label">Connections:</span>
                    ${{entity.Connections}}
                </div>`;
            }}

            if (entity.First_Mentioned) {{
                html += `<div class="entity-detail-row">
                    <span class="entity-detail-label">First Mentioned:</span>
                    ${{entity.First_Mentioned}}
                </div>`;
            }}

            if (entity.Last_Updated) {{
                html += `<div class="entity-detail-row">
                    <span class="entity-detail-label">Last Updated:</span>
                    ${{entity.Last_Updated}}
                </div>`;
            }}

            html += '</div>';

            document.getElementById('entityDetails').innerHTML = html;
            document.getElementById('entityModal').style.display = 'block';
        }}

        function closeModal() {{
            document.getElementById('entityModal').style.display = 'none';
        }}

        function showSource(sourceId) {{
            alert('Source ' + sourceId + ' - Would link to sources section');
        }}

        // Close modal when clicking outside
        window.onclick = function(event) {{
            const modal = document.getElementById('entityModal');
            if (event.target == modal) {{
                closeModal();
            }}
        }}
    </script>
</body>
</html>
"""

        return html


def main():
    """Command-line interface"""
    import argparse

    parser = argparse.ArgumentParser(description='Interactive Document Viewer')
    parser.add_argument('--document', required=True, help='Path to markdown document')
    parser.add_argument('--investigation', required=True, help='Investigation name')
    parser.add_argument('--open', action='store_true', help='Open in browser after generation')

    args = parser.parse_args()

    viewer = InteractiveDocumentViewer(investigation=args.investigation)
    output_file = viewer.convert_document(Path(args.document))

    print(f"[OK] Interactive document generated: {output_file}")

    if args.open:
        import subprocess
        subprocess.run(['cmd', '/c', 'start', '', str(output_file)])


if __name__ == '__main__':
    main()
