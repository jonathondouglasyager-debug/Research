"""
EVIDENCE CHAIN BUILDER
Link documents together to create proof chains
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import json
from typing import Dict, List, Tuple

# Import Phase 1 systems
sys.path.append(str(Path(__file__).parent.parent / '_System'))
from file_intelligence import FileIntelligence

class EvidenceChainBuilder:
    """
    Build chains of evidence showing logical connections between documents
    """
    
    def __init__(self, research_dir: str = None):
        """Initialize with research directory"""
        if research_dir is None:
            research_dir = r"C:\Users\jonat\Documents\Research"
        self.research_dir = Path(research_dir)
        self.file_intel = FileIntelligence()
    
    def analyze_document(self, file_path: Path) -> Dict:
        """
        Analyze a document for evidence value
        
        Args:
            file_path: Path to document
        
        Returns:
            Document analysis dictionary
        """
        info = self.file_intel.get_file_info(str(file_path))
        
        analysis = {
            'path': str(file_path),
            'filename': file_path.name,
            'type': file_path.suffix.lower(),
            'size': file_path.stat().st_size,
            'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
            'extracted_info': info,
            'evidence_type': self._classify_evidence_type(file_path, info),
            'key_terms': self._extract_key_terms(info),
            'dates': self._extract_dates(info),
            'entities': self._extract_entities(info)
        }
        
        return analysis
    
    def _classify_evidence_type(self, file_path: Path, info: Dict) -> str:
        """Classify type of evidence"""
        filename_lower = file_path.name.lower()
        content = info.get('text_content', '').lower()
        
        # Check filename patterns
        if any(word in filename_lower for word in ['contract', 'agreement', 'deed']):
            return 'Legal Document'
        elif any(word in filename_lower for word in ['invoice', 'receipt', 'payment']):
            return 'Financial Record'
        elif any(word in filename_lower for word in ['email', 'message', 'correspondence']):
            return 'Communication'
        elif any(word in filename_lower for word in ['report', 'analysis', 'study']):
            return 'Report'
        elif any(word in filename_lower for word in ['photo', 'image', 'picture']):
            return 'Visual Evidence'
        
        # Check content patterns
        if any(word in content for word in ['hereby', 'whereas', 'pursuant to']):
            return 'Legal Document'
        elif any(word in content for word in ['dear', 'sincerely', 'from:', 'to:']):
            return 'Communication'
        elif any(word in content for word in ['$', 'usd', 'payment', 'invoice']):
            return 'Financial Record'
        
        return 'General Document'
    
    def _extract_key_terms(self, info: Dict) -> List[str]:
        """Extract key terms from document"""
        content = info.get('text_content', '')
        
        # Simple keyword extraction (could be enhanced with NLP)
        # Look for capitalized words, proper nouns
        words = content.split()
        key_terms = set()
        
        for i, word in enumerate(words):
            # Capitalize proper nouns (simple heuristic)
            if word and word[0].isupper() and len(word) > 3:
                # Not at start of sentence
                if i > 0 and not words[i-1].endswith('.'):
                    key_terms.add(word)
        
        return list(key_terms)[:20]  # Limit to 20
    
    def _extract_dates(self, info: Dict) -> List[str]:
        """Extract dates from document"""
        import re
        content = info.get('text_content', '')
        
        date_patterns = [
            r'\b(\d{4})-(\d{2})-(\d{2})\b',  # 2023-04-18
            r'\b(\d{2})/(\d{2})/(\d{4})\b',  # 04/18/2023
            r'\b(\w+)\s+(\d{1,2}),?\s+(\d{4})\b',  # April 18, 2023
        ]
        
        dates = set()
        for pattern in date_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                dates.add(' '.join(match))
        
        return list(dates)[:10]  # Limit to 10
    
    def _extract_entities(self, info: Dict) -> List[str]:
        """Extract entity names from document"""
        # This is a simplified version - could use NER
        content = info.get('text_content', '')
        
        # Look for words that might be entities
        # Corporation suffixes
        entity_suffixes = [
            'Corporation', 'Corp', 'Inc', 'LLC', 'Ltd', 'Company', 'Co',
            'Foundation', 'Institute', 'University', 'Department'
        ]
        
        entities = set()
        words = content.split()
        
        for i, word in enumerate(words):
            for suffix in entity_suffixes:
                if suffix.lower() in word.lower():
                    # Get preceding words (likely entity name)
                    start = max(0, i - 3)
                    entity_name = ' '.join(words[start:i+1])
                    entities.add(entity_name)
        
        return list(entities)[:15]  # Limit to 15
    
    def find_connections(self, doc1: Dict, doc2: Dict) -> Dict:
        """
        Find connections between two documents
        
        Args:
            doc1: First document analysis
            doc2: Second document analysis
        
        Returns:
            Dictionary describing connections
        """
        connections = {
            'shared_terms': [],
            'shared_dates': [],
            'shared_entities': [],
            'temporal_proximity': None,
            'connection_strength': 0.0
        }
        
        # Find shared key terms
        terms1 = set(doc1['key_terms'])
        terms2 = set(doc2['key_terms'])
        connections['shared_terms'] = list(terms1 & terms2)
        
        # Find shared dates
        dates1 = set(doc1['dates'])
        dates2 = set(doc2['dates'])
        connections['shared_dates'] = list(dates1 & dates2)
        
        # Find shared entities
        entities1 = set(doc1['entities'])
        entities2 = set(doc2['entities'])
        connections['shared_entities'] = list(entities1 & entities2)
        
        # Calculate temporal proximity
        try:
            time1 = datetime.fromisoformat(doc1['modified'])
            time2 = datetime.fromisoformat(doc2['modified'])
            days_apart = abs((time2 - time1).days)
            connections['temporal_proximity'] = days_apart
        except:
            pass
        
        # Calculate connection strength (0-1 scale)
        strength = 0.0
        strength += len(connections['shared_terms']) * 0.05  # Each term +5%
        strength += len(connections['shared_dates']) * 0.15  # Each date +15%
        strength += len(connections['shared_entities']) * 0.20  # Each entity +20%
        
        # Temporal bonus
        if connections['temporal_proximity'] is not None:
            if connections['temporal_proximity'] < 7:
                strength += 0.15  # Within a week
            elif connections['temporal_proximity'] < 30:
                strength += 0.10  # Within a month
        
        connections['connection_strength'] = min(1.0, strength)
        
        return connections
    
    def build_chain(self, evidence_dir: Path, min_strength: float = 0.2) -> Dict:
        """
        Build evidence chain from directory
        
        Args:
            evidence_dir: Directory containing evidence
            min_strength: Minimum connection strength to include
        
        Returns:
            Chain dictionary with documents and connections
        """
        print(f"\n[SCAN] Analyzing evidence in: {evidence_dir}")
        
        # Analyze all documents
        documents = []
        for file_path in evidence_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in ['.pdf', '.txt', '.md', '.docx', '.doc']:
                print(f"  Analyzing: {file_path.name}")
                doc_analysis = self.analyze_document(file_path)
                documents.append(doc_analysis)
        
        print(f"\n[ANALYZE] Found {len(documents)} documents")
        print(f"[CONNECT] Finding connections...")
        
        # Find all connections
        connections = []
        for i in range(len(documents)):
            for j in range(i + 1, len(documents)):
                connection = self.find_connections(documents[i], documents[j])
                
                if connection['connection_strength'] >= min_strength:
                    connections.append({
                        'doc1': documents[i]['filename'],
                        'doc2': documents[j]['filename'],
                        **connection
                    })
        
        print(f"[OK] Found {len(connections)} connections (strength >= {min_strength})")
        
        return {
            'evidence_dir': str(evidence_dir),
            'generated': datetime.now().isoformat(),
            'total_documents': len(documents),
            'total_connections': len(connections),
            'documents': documents,
            'connections': sorted(connections, key=lambda x: x['connection_strength'], reverse=True),
            'min_strength': min_strength
        }
    
    def export_json(self, chain_data: Dict, output_path: str):
        """Export chain as JSON"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chain_data, f, indent=2)
        return output_path
    
    def export_markdown(self, chain_data: Dict, output_path: str):
        """
        Export chain as markdown report
        
        Args:
            chain_data: Chain dictionary
            output_path: Path to save markdown
        """
        lines = [
            "# Evidence Chain Analysis",
            "",
            f"**Evidence Directory:** {chain_data['evidence_dir']}",
            f"**Generated:** {chain_data['generated']}",
            f"**Documents Analyzed:** {chain_data['total_documents']}",
            f"**Connections Found:** {chain_data['total_connections']}",
            f"**Minimum Strength:** {chain_data['min_strength']}",
            "",
            "---",
            ""
        ]
        
        # Document inventory
        lines.extend([
            "## Document Inventory",
            ""
        ])
        
        for doc in chain_data['documents']:
            lines.append(f"### {doc['filename']}")
            lines.append(f"- **Type:** {doc['evidence_type']}")
            lines.append(f"- **Size:** {doc['size'] / 1024:.1f} KB")
            lines.append(f"- **Modified:** {doc['modified'][:10]}")
            
            if doc['dates']:
                lines.append(f"- **Dates Mentioned:** {', '.join(doc['dates'][:5])}")
            
            if doc['entities']:
                lines.append(f"- **Entities:** {', '.join(doc['entities'][:5])}")
            
            lines.append("")
        
        lines.extend([
            "---",
            "",
            "## Connection Network",
            ""
        ])
        
        # Connections by strength
        strong_connections = [c for c in chain_data['connections'] if c['connection_strength'] >= 0.5]
        medium_connections = [c for c in chain_data['connections'] if 0.3 <= c['connection_strength'] < 0.5]
        weak_connections = [c for c in chain_data['connections'] if c['connection_strength'] < 0.3]
        
        if strong_connections:
            lines.append("### Strong Connections (≥50%)")
            lines.append("")
            for conn in strong_connections:
                lines.append(f"**{conn['doc1']} ↔ {conn['doc2']}**")
                lines.append(f"- Strength: {conn['connection_strength']:.0%}")
                
                if conn['shared_entities']:
                    lines.append(f"- Shared Entities: {', '.join(conn['shared_entities'])}")
                if conn['shared_dates']:
                    lines.append(f"- Shared Dates: {', '.join(conn['shared_dates'])}")
                if conn['shared_terms']:
                    lines.append(f"- Shared Terms: {', '.join(conn['shared_terms'][:5])}")
                
                lines.append("")
        
        if medium_connections:
            lines.append("### Medium Connections (30-50%)")
            lines.append("")
            for conn in medium_connections:
                lines.append(f"**{conn['doc1']} ↔ {conn['doc2']}** ({conn['connection_strength']:.0%})")
                if conn['shared_entities']:
                    lines.append(f"- Entities: {', '.join(conn['shared_entities'])}")
                lines.append("")
        
        if weak_connections:
            lines.append(f"### Weak Connections (<30%) - {len(weak_connections)} total")
            lines.append("")
        
        # Write file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        return output_path
    
    def export_html(self, chain_data: Dict, output_path: str):
        """
        Export chain as interactive HTML visualization
        
        Args:
            chain_data: Chain dictionary
            output_path: Path to save HTML
        """
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Evidence Chain Analysis</title>
    <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            margin: 0;
            padding: 0;
            background: #f5f5f5;
        }}
        .header {{
            background: white;
            padding: 20px 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            margin: 0 0 10px 0;
            color: #333;
        }}
        .stats {{
            color: #666;
            font-size: 14px;
        }}
        .container {{
            display: flex;
            height: calc(100vh - 120px);
        }}
        #network {{
            flex: 1;
            background: white;
        }}
        .sidebar {{
            width: 350px;
            background: white;
            border-left: 1px solid #ddd;
            overflow-y: auto;
            padding: 20px;
        }}
        .doc-card {{
            background: #f8f9fa;
            padding: 15px;
            margin: 10px 0;
            border-radius: 6px;
            cursor: pointer;
            border-left: 4px solid #2c5aa0;
        }}
        .doc-card:hover {{
            background: #e9ecef;
        }}
        .doc-name {{
            font-weight: bold;
            color: #2c5aa0;
            margin-bottom: 5px;
        }}
        .doc-details {{
            font-size: 12px;
            color: #666;
        }}
        .connection-info {{
            background: #fff3cd;
            padding: 15px;
            margin: 20px 0;
            border-radius: 6px;
            border-left: 4px solid #ffc107;
            display: none;
        }}
        .strength-bar {{
            height: 8px;
            background: #ddd;
            border-radius: 4px;
            margin: 10px 0;
            overflow: hidden;
        }}
        .strength-fill {{
            height: 100%;
            background: linear-gradient(90deg, #ff6b6b, #ffd93d, #6bcf7f);
            transition: width 0.3s;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Evidence Chain Analysis</h1>
        <div class="stats">
            <strong>{total_documents}</strong> documents | 
            <strong>{total_connections}</strong> connections | 
            Min strength: {min_strength}%
        </div>
    </div>
    
    <div class="container">
        <div id="network"></div>
        
        <div class="sidebar">
            <h3>Documents</h3>
            <div id="doc-list">{doc_list_html}</div>
            
            <div id="connection-detail" class="connection-info">
                <h4>Connection Details</h4>
                <div id="connection-content"></div>
            </div>
        </div>
    </div>
    
    <script>
        // Network data
        const documents = {documents_json};
        const connections = {connections_json};
        
        // Build nodes
        const nodes = new vis.DataSet(
            documents.map(doc => ({{
                id: doc.filename,
                label: doc.filename,
                title: `${{doc.evidence_type}}\\n${{(doc.size / 1024).toFixed(1)}} KB`,
                color: {{
                    background: '#e3f2fd',
                    border: '#2c5aa0'
                }}
            }}))
        );
        
        // Build edges
        const edges = new vis.DataSet(
            connections.map((conn, idx) => ({{
                id: idx,
                from: conn.doc1,
                to: conn.doc2,
                label: `${{(conn.connection_strength * 100).toFixed(0)}}%`,
                width: Math.max(1, conn.connection_strength * 5),
                color: {{
                    color: conn.connection_strength >= 0.5 ? '#6bcf7f' : 
                           conn.connection_strength >= 0.3 ? '#ffd93d' : '#ff6b6b'
                }},
                data: conn
            }}))
        );
        
        // Network options
        const options = {{
            nodes: {{
                shape: 'box',
                margin: 10,
                font: {{
                    size: 14
                }}
            }},
            edges: {{
                smooth: {{
                    type: 'continuous'
                }},
                font: {{
                    size: 12,
                    align: 'top'
                }}
            }},
            physics: {{
                barnesHut: {{
                    gravitationalConstant: -3000,
                    springLength: 150
                }}
            }}
        }};
        
        // Create network
        const container = document.getElementById('network');
        const data = {{ nodes: nodes, edges: edges }};
        const network = new vis.Network(container, data, options);
        
        // Edge click handler
        network.on('selectEdge', function(params) {{
            if (params.edges.length > 0) {{
                const edge = edges.get(params.edges[0]);
                const conn = edge.data;
                
                let html = `
                    <strong>${{conn.doc1}} ↔ ${{conn.doc2}}</strong>
                    <div class="strength-bar">
                        <div class="strength-fill" style="width: ${{conn.connection_strength * 100}}%"></div>
                    </div>
                    <p><strong>Strength:</strong> ${{(conn.connection_strength * 100).toFixed(0)}}%</p>
                `;
                
                if (conn.shared_entities && conn.shared_entities.length > 0) {{
                    html += `<p><strong>Shared Entities:</strong> ${{conn.shared_entities.join(', ')}}</p>`;
                }}
                if (conn.shared_dates && conn.shared_dates.length > 0) {{
                    html += `<p><strong>Shared Dates:</strong> ${{conn.shared_dates.join(', ')}}</p>`;
                }}
                if (conn.shared_terms && conn.shared_terms.length > 0) {{
                    html += `<p><strong>Shared Terms:</strong> ${{conn.shared_terms.slice(0, 5).join(', ')}}</p>`;
                }}
                
                document.getElementById('connection-content').innerHTML = html;
                document.getElementById('connection-detail').style.display = 'block';
            }}
        }});
    </script>
</body>
</html>
"""
        
        # Build document list HTML
        doc_list_html = []
        for doc in chain_data['documents']:
            doc_list_html.append(f'''
            <div class="doc-card">
                <div class="doc-name">{doc['filename']}</div>
                <div class="doc-details">
                    {doc['evidence_type']} | {doc['size'] / 1024:.1f} KB
                </div>
            </div>
            ''')
        
        # Generate HTML
        html = html_template.format(
            total_documents=chain_data['total_documents'],
            total_connections=chain_data['total_connections'],
            min_strength=int(chain_data['min_strength'] * 100),
            documents_json=json.dumps(chain_data['documents']),
            connections_json=json.dumps(chain_data['connections']),
            doc_list_html=''.join(doc_list_html)
        )
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return output_path


def main():
    """Command-line interface"""
    builder = EvidenceChainBuilder()
    
    if len(sys.argv) < 2:
        print("Evidence Chain Builder - Link documents into proof chains")
        print()
        print("Usage:")
        print('  python evidence_chain_builder.py build <evidence_dir> [min_strength]')
        print('  python evidence_chain_builder.py export <evidence_dir> <format> <output_path> [min_strength]')
        print()
        print("Formats: json, markdown, html")
        print()
        print("Examples:")
        print('  python evidence_chain_builder.py build "C:/Research/Evidence" 0.2')
        print('  python evidence_chain_builder.py export "C:/Research/Evidence" html chain.html 0.3')
        return
    
    command = sys.argv[1].lower()
    
    if command == 'build':
        if len(sys.argv) < 3:
            print("Error: Missing evidence directory")
            return
        
        evidence_dir = Path(sys.argv[2])
        min_strength = float(sys.argv[3]) if len(sys.argv) > 3 else 0.2
        
        if not evidence_dir.exists():
            print(f"[FAIL] Evidence directory not found: {evidence_dir}")
            return
        
        chain = builder.build_chain(evidence_dir, min_strength)
        
        print(f"\n[OK] Chain analysis complete!")
        print(f"Documents: {chain['total_documents']}")
        print(f"Connections: {chain['total_connections']}")
    
    elif command == 'export':
        if len(sys.argv) < 5:
            print("Error: Missing arguments")
            return
        
        evidence_dir = Path(sys.argv[2])
        format_type = sys.argv[3].lower()
        output_path = sys.argv[4]
        min_strength = float(sys.argv[5]) if len(sys.argv) > 5 else 0.2
        
        if not evidence_dir.exists():
            print(f"[FAIL] Evidence directory not found: {evidence_dir}")
            return
        
        chain = builder.build_chain(evidence_dir, min_strength)
        
        if format_type == 'json':
            output = builder.export_json(chain, output_path)
        elif format_type == 'markdown' or format_type == 'md':
            output = builder.export_markdown(chain, output_path)
        elif format_type == 'html':
            output = builder.export_html(chain, output_path)
        else:
            print(f"[FAIL] Unknown format: {format_type}")
            return
        
        print(f"\n[OK] Chain exported!")
        print(f"Format: {format_type}")
        print(f"Documents: {chain['total_documents']}")
        print(f"Connections: {chain['total_connections']}")
        print(f"Output: {output}")
    
    else:
        print(f"Unknown command: {command}")
        print("Valid commands: build, export")


if __name__ == '__main__':
    main()
