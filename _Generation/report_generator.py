"""
INVESTIGATION REPORT GENERATOR
Create professional reports from investigation data
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import json
from typing import Dict, List

# Import Phase 1 systems
sys.path.append(str(Path(__file__).parent.parent / '_System'))
from database_manager import DatabaseManager

class ReportGenerator:
    """
    Generate professional investigation reports in multiple formats
    """
    
    def __init__(self, research_dir: str = None):
        """Initialize with research directory"""
        if research_dir is None:
            research_dir = r"C:\Users\jonat\Documents\Research"
        self.research_dir = Path(research_dir)
        self.db_manager = DatabaseManager()
    
    def gather_investigation_data(self, investigation_path: Path) -> Dict:
        """
        Gather all data from an investigation folder
        
        Args:
            investigation_path: Path to investigation folder
        
        Returns:
            Dictionary with all investigation data
        """
        data = {
            'investigation_name': investigation_path.name,
            'path': str(investigation_path),
            'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'metadata': {},
            'overview': '',
            'timeline': [],
            'entities': [],
            'evidence': [],
            'analysis': []
        }
        
        # Load metadata
        metadata_path = investigation_path / 'investigation_metadata.json'
        if metadata_path.exists():
            with open(metadata_path, 'r', encoding='utf-8') as f:
                data['metadata'] = json.load(f)
        
        # Load overview
        overview_path = investigation_path / 'investigation_overview.md'
        if overview_path.exists():
            with open(overview_path, 'r', encoding='utf-8') as f:
                data['overview'] = f.read()
        
        # Load timeline
        timeline_path = investigation_path / 'Timeline' / 'timeline.md'
        if timeline_path.exists():
            with open(timeline_path, 'r', encoding='utf-8') as f:
                data['timeline'] = f.read()
        
        # Load entity database
        entity_path = investigation_path / 'entity_database.csv'
        if entity_path.exists():
            import pandas as pd
            df = pd.read_csv(entity_path)
            data['entities'] = df.to_dict('records')
        
        # Scan Evidence folder
        evidence_dir = investigation_path / 'Evidence'
        if evidence_dir.exists():
            for file_path in evidence_dir.rglob('*'):
                if file_path.is_file():
                    data['evidence'].append({
                        'filename': file_path.name,
                        'path': str(file_path.relative_to(investigation_path)),
                        'size': file_path.stat().st_size,
                        'modified': datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d')
                    })
        
        # Scan Analysis folder
        analysis_dir = investigation_path / 'Analysis'
        if analysis_dir.exists():
            for file_path in analysis_dir.rglob('*.md'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data['analysis'].append({
                        'filename': file_path.name,
                        'content': f.read()
                    })
        
        return data
    
    def export_markdown(self, investigation_path: Path, output_path: str):
        """
        Export investigation as comprehensive markdown report
        
        Args:
            investigation_path: Path to investigation folder
            output_path: Path to save report
        """
        data = self.gather_investigation_data(investigation_path)
        
        lines = [
            f"# {data['investigation_name']} Investigation Report",
            "",
            f"**Generated:** {data['generated_date']}",
            "",
            "---",
            ""
        ]
        
        # Table of contents
        lines.extend([
            "## Table of Contents",
            "",
            "1. [Executive Summary](#executive-summary)",
            "2. [Investigation Overview](#investigation-overview)",
            "3. [Timeline](#timeline)",
            "4. [Key Entities](#key-entities)",
            "5. [Evidence Inventory](#evidence-inventory)",
            "6. [Detailed Analysis](#detailed-analysis)",
            "",
            "---",
            ""
        ])
        
        # Executive Summary
        lines.extend([
            "## Executive Summary",
            "",
            f"**Investigation:** {data['investigation_name']}",
            f"**Entities Tracked:** {len(data['entities'])}",
            f"**Evidence Files:** {len(data['evidence'])}",
            f"**Analysis Reports:** {len(data['analysis'])}",
            ""
        ])
        
        if data['metadata']:
            lines.append("**Metadata:**")
            for key, value in data['metadata'].items():
                lines.append(f"- {key}: {value}")
            lines.append("")
        
        lines.extend([
            "---",
            ""
        ])
        
        # Investigation Overview
        lines.extend([
            "## Investigation Overview",
            "",
            data['overview'] if data['overview'] else "*No overview available*",
            "",
            "---",
            ""
        ])
        
        # Timeline
        lines.extend([
            "## Timeline",
            "",
            data['timeline'] if data['timeline'] else "*No timeline available*",
            "",
            "---",
            ""
        ])
        
        # Key Entities
        lines.extend([
            "## Key Entities",
            "",
            f"Total entities tracked: **{len(data['entities'])}**",
            ""
        ])
        
        if data['entities']:
            # Group by type if available
            entity_types = {}
            for entity in data['entities']:
                entity_type = entity.get('Entity_Type', 'Unknown')
                if entity_type not in entity_types:
                    entity_types[entity_type] = []
                entity_types[entity_type].append(entity)
            
            for entity_type, entities in sorted(entity_types.items()):
                lines.append(f"### {entity_type} ({len(entities)})")
                lines.append("")
                
                for entity in entities:
                    name = entity.get('Entity_Name', 'Unknown')
                    lines.append(f"**{name}**")
                    
                    # Add key fields
                    for key, value in entity.items():
                        if key not in ['Entity_Name', 'Entity_Type'] and value:
                            lines.append(f"- {key}: {value}")
                    lines.append("")
        else:
            lines.append("*No entities tracked*")
            lines.append("")
        
        lines.extend([
            "---",
            ""
        ])
        
        # Evidence Inventory
        lines.extend([
            "## Evidence Inventory",
            "",
            f"Total evidence files: **{len(data['evidence'])}**",
            ""
        ])
        
        if data['evidence']:
            lines.append("| Filename | Path | Size | Modified |")
            lines.append("|----------|------|------|----------|")
            for evidence in data['evidence']:
                size_kb = evidence['size'] / 1024
                lines.append(
                    f"| {evidence['filename']} | {evidence['path']} | "
                    f"{size_kb:.1f} KB | {evidence['modified']} |"
                )
            lines.append("")
        else:
            lines.append("*No evidence files*")
            lines.append("")
        
        lines.extend([
            "---",
            ""
        ])
        
        # Detailed Analysis
        lines.extend([
            "## Detailed Analysis",
            ""
        ])
        
        if data['analysis']:
            for analysis in data['analysis']:
                lines.append(f"### {analysis['filename']}")
                lines.append("")
                lines.append(analysis['content'])
                lines.append("")
                lines.append("---")
                lines.append("")
        else:
            lines.append("*No analysis reports available*")
            lines.append("")
        
        # Write file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        return output_path
    
    def export_html(self, investigation_path: Path, output_path: str):
        """
        Export investigation as professional HTML report
        
        Args:
            investigation_path: Path to investigation folder
            output_path: Path to save HTML
        """
        data = self.gather_investigation_data(investigation_path)
        
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{investigation_name} Investigation Report</title>
    <style>
        @media print {{
            body {{ margin: 0; }}
            .no-print {{ display: none; }}
            .page-break {{ page-break-after: always; }}
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
            background: #f8f9fa;
            color: #333;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2c5aa0 0%, #1a3a6b 100%);
            color: white;
            padding: 40px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        h1 {{
            margin: 0 0 10px 0;
            font-size: 36px;
        }}
        
        .header-meta {{
            opacity: 0.9;
            font-size: 14px;
        }}
        
        .section {{
            background: white;
            padding: 30px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        }}
        
        h2 {{
            color: #2c5aa0;
            border-bottom: 2px solid #2c5aa0;
            padding-bottom: 10px;
            margin-top: 0;
        }}
        
        h3 {{
            color: #1a3a6b;
            margin-top: 25px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .stat-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            border-left: 4px solid #2c5aa0;
        }}
        
        .stat-value {{
            font-size: 32px;
            font-weight: bold;
            color: #2c5aa0;
            margin: 0;
        }}
        
        .stat-label {{
            font-size: 14px;
            color: #666;
            margin: 5px 0 0 0;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        
        th {{
            background: #2c5aa0;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        
        td {{
            padding: 12px;
            border-bottom: 1px solid #ddd;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .entity-card {{
            background: #f8f9fa;
            padding: 20px;
            margin: 15px 0;
            border-radius: 6px;
            border-left: 4px solid #2c5aa0;
        }}
        
        .entity-name {{
            font-size: 18px;
            font-weight: bold;
            color: #1a3a6b;
            margin-bottom: 10px;
        }}
        
        .entity-details {{
            font-size: 14px;
            color: #666;
            line-height: 1.8;
        }}
        
        .toc {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            margin-bottom: 20px;
        }}
        
        .toc a {{
            color: #2c5aa0;
            text-decoration: none;
            display: block;
            padding: 5px 0;
        }}
        
        .toc a:hover {{
            text-decoration: underline;
        }}
        
        .print-button {{
            background: #2c5aa0;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            margin: 20px 0;
        }}
        
        .print-button:hover {{
            background: #1a3a6b;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{investigation_name} Investigation Report</h1>
        <div class="header-meta">
            Generated: {generated_date}
        </div>
    </div>
    
    <button class="print-button no-print" onclick="window.print()">🖨️ Print Report</button>
    
    <div class="section toc">
        <h2>Table of Contents</h2>
        <a href="#executive-summary">1. Executive Summary</a>
        <a href="#overview">2. Investigation Overview</a>
        <a href="#timeline">3. Timeline</a>
        <a href="#entities">4. Key Entities</a>
        <a href="#evidence">5. Evidence Inventory</a>
        <a href="#analysis">6. Detailed Analysis</a>
    </div>
    
    <div id="executive-summary" class="section">
        <h2>Executive Summary</h2>
        
        <div class="stats-grid">
            <div class="stat-card">
                <p class="stat-value">{entity_count}</p>
                <p class="stat-label">Entities Tracked</p>
            </div>
            <div class="stat-card">
                <p class="stat-value">{evidence_count}</p>
                <p class="stat-label">Evidence Files</p>
            </div>
            <div class="stat-card">
                <p class="stat-value">{analysis_count}</p>
                <p class="stat-label">Analysis Reports</p>
            </div>
        </div>
    </div>
    
    <div id="overview" class="section">
        <h2>Investigation Overview</h2>
        {overview_content}
    </div>
    
    <div id="timeline" class="section page-break">
        <h2>Timeline</h2>
        {timeline_content}
    </div>
    
    <div id="entities" class="section page-break">
        <h2>Key Entities</h2>
        <p>Total entities tracked: <strong>{entity_count}</strong></p>
        {entities_content}
    </div>
    
    <div id="evidence" class="section page-break">
        <h2>Evidence Inventory</h2>
        <p>Total evidence files: <strong>{evidence_count}</strong></p>
        {evidence_content}
    </div>
    
    <div id="analysis" class="section page-break">
        <h2>Detailed Analysis</h2>
        {analysis_content}
    </div>
</body>
</html>
"""
        
        # Build entities content
        entities_html = []
        if data['entities']:
            entity_types = {}
            for entity in data['entities']:
                entity_type = entity.get('Entity_Type', 'Unknown')
                if entity_type not in entity_types:
                    entity_types[entity_type] = []
                entity_types[entity_type].append(entity)
            
            for entity_type, entities in sorted(entity_types.items()):
                entities_html.append(f'<h3>{entity_type} ({len(entities)})</h3>')
                
                for entity in entities:
                    name = entity.get('Entity_Name', 'Unknown')
                    entities_html.append('<div class="entity-card">')
                    entities_html.append(f'<div class="entity-name">{name}</div>')
                    entities_html.append('<div class="entity-details">')
                    
                    for key, value in entity.items():
                        if key not in ['Entity_Name', 'Entity_Type'] and value:
                            entities_html.append(f'<strong>{key}:</strong> {value}<br>')
                    
                    entities_html.append('</div></div>')
        else:
            entities_html.append('<p><em>No entities tracked</em></p>')
        
        # Build evidence table
        evidence_html = []
        if data['evidence']:
            evidence_html.append('<table>')
            evidence_html.append('<tr><th>Filename</th><th>Path</th><th>Size</th><th>Modified</th></tr>')
            for evidence in data['evidence']:
                size_kb = evidence['size'] / 1024
                evidence_html.append(
                    f'<tr>'
                    f'<td>{evidence["filename"]}</td>'
                    f'<td>{evidence["path"]}</td>'
                    f'<td>{size_kb:.1f} KB</td>'
                    f'<td>{evidence["modified"]}</td>'
                    f'</tr>'
                )
            evidence_html.append('</table>')
        else:
            evidence_html.append('<p><em>No evidence files</em></p>')
        
        # Build analysis content
        analysis_html = []
        if data['analysis']:
            for analysis in data['analysis']:
                analysis_html.append(f'<h3>{analysis["filename"]}</h3>')
                # Convert markdown to basic HTML
                content = analysis["content"].replace('\n\n', '</p><p>').replace('\n', '<br>')
                analysis_html.append(f'<p>{content}</p>')
        else:
            analysis_html.append('<p><em>No analysis reports available</em></p>')
        
        # Generate final HTML
        html = html_template.format(
            investigation_name=data['investigation_name'],
            generated_date=data['generated_date'],
            entity_count=len(data['entities']),
            evidence_count=len(data['evidence']),
            analysis_count=len(data['analysis']),
            overview_content=data['overview'].replace('\n', '<br>') if data['overview'] else '<em>No overview available</em>',
            timeline_content=data['timeline'].replace('\n', '<br>') if data['timeline'] else '<em>No timeline available</em>',
            entities_content='\n'.join(entities_html),
            evidence_content='\n'.join(evidence_html),
            analysis_content='\n'.join(analysis_html)
        )
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return output_path


def main():
    """Command-line interface"""
    generator = ReportGenerator()
    
    if len(sys.argv) < 2:
        print("Investigation Report Generator - Create professional reports")
        print()
        print("Usage:")
        print('  python report_generator.py export <investigation_path> <format> <output_path>')
        print()
        print("Formats: markdown, html")
        print()
        print("Examples:")
        print('  python report_generator.py export "C:/Research/Active_Investigations/Fox_News" markdown report.md')
        print('  python report_generator.py export "C:/Research/Active_Investigations/Fox_News" html report.html')
        return
    
    command = sys.argv[1].lower()
    
    if command == 'export':
        if len(sys.argv) < 5:
            print("Error: Missing arguments")
            print('Usage: python report_generator.py export <investigation_path> <format> <output_path>')
            return
        
        investigation_path = Path(sys.argv[2])
        format_type = sys.argv[3].lower()
        output_path = sys.argv[4]
        
        if not investigation_path.exists():
            print(f"[FAIL] Investigation path not found: {investigation_path}")
            return
        
        print(f"\n[EXPORT] Generating report...")
        print(f"Investigation: {investigation_path.name}")
        print(f"Format: {format_type}")
        
        if format_type == 'markdown' or format_type == 'md':
            output = generator.export_markdown(investigation_path, output_path)
        elif format_type == 'html':
            output = generator.export_html(investigation_path, output_path)
        else:
            print(f"[FAIL] Unknown format: {format_type}")
            return
        
        print(f"\n[OK] Report generated!")
        print(f"Output: {output}")
    
    else:
        print(f"Unknown command: {command}")
        print("Valid commands: export")


if __name__ == '__main__':
    main()
