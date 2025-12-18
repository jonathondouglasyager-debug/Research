"""
ENTITY NETWORK MAPPER
Create visual connection graphs from investigation data
"""

import os
import sys
from pathlib import Path
import json
from collections import defaultdict
from typing import Dict, List, Set, Tuple

# Import Phase 1 systems
sys.path.append(str(Path(__file__).parent.parent / '_System'))
from database_manager import DatabaseManager

class EntityNetworkMapper:
    """
    Map relationships between entities and create network visualizations
    """
    
    def __init__(self, research_dir: str = None):
        """Initialize with research directory"""
        if research_dir is None:
            research_dir = r"C:\Users\jonat\Documents\Research"
        self.research_dir = Path(research_dir)
        self.db_manager = DatabaseManager()
        
        # Connection keywords to look for
        self.connection_keywords = [
            'connection', 'relationship', 'ties', 'linked', 'associated',
            'partner', 'subsidiary', 'owns', 'owned by', 'board member',
            'executive', 'invested', 'shareholder', 'funds', 'funded by'
        ]
    
    def extract_entities_from_database(self, db_name: str) -> List[Dict]:
        """
        Extract entities from a database
        
        Args:
            db_name: Name of database to scan
        
        Returns:
            List of entity dictionaries
        """
        databases = self.db_manager.list_databases()
        if db_name not in databases:
            return []
        
        df = databases[db_name]['dataframe']
        entities = []
        
        # Look for name/entity columns
        name_cols = [col for col in df.columns if any(
            keyword in col.lower() 
            for keyword in ['name', 'entity', 'person', 'organization', 'company']
        )]
        
        # Look for type columns
        type_cols = [col for col in df.columns if any(
            keyword in col.lower()
            for keyword in ['type', 'category', 'kind']
        )]
        
        # Look for connection columns
        connection_cols = [col for col in df.columns if any(
            keyword in col.lower()
            for keyword in self.connection_keywords
        )]
        
        for idx, row in df.iterrows():
            entity = {
                'source_db': db_name,
                'row_index': idx,
                'connections': []
            }
            
            # Extract name
            for name_col in name_cols:
                if pd.notna(row[name_col]):
                    entity['name'] = str(row[name_col])
                    break
            
            # Extract type
            for type_col in type_cols:
                if pd.notna(row[type_col]):
                    entity['type'] = str(row[type_col])
                    break
            
            # Extract connections
            for conn_col in connection_cols:
                if pd.notna(row[conn_col]):
                    entity['connections'].append({
                        'field': conn_col,
                        'value': str(row[conn_col])
                    })
            
            # Add other fields as metadata
            entity['metadata'] = {}
            for col in df.columns:
                if col not in name_cols and col not in type_cols and col not in connection_cols:
                    if pd.notna(row[col]):
                        entity['metadata'][col] = str(row[col])
            
            if 'name' in entity:
                entities.append(entity)
        
        return entities
    
    def build_network(self, investigation_name: str = None) -> Dict:
        """
        Build complete entity network
        
        Args:
            investigation_name: Optional filter for specific investigation
        
        Returns:
            Network dictionary with nodes and edges
        """
        # Get all databases
        databases = self.db_manager.list_databases()
        
        # Filter by investigation if specified
        if investigation_name:
            databases = {
                name: info for name, info in databases.items()
                if investigation_name.lower() in name.lower()
            }
        
        # Extract all entities
        all_entities = []
        for db_name in databases.keys():
            entities = self.extract_entities_from_database(db_name)
            all_entities.extend(entities)
        
        # Build nodes
        nodes = {}
        for entity in all_entities:
            node_id = entity['name']
            if node_id not in nodes:
                nodes[node_id] = {
                    'id': node_id,
                    'name': entity['name'],
                    'type': entity.get('type', 'Unknown'),
                    'sources': [entity['source_db']],
                    'metadata': entity['metadata'],
                    'connections': entity['connections']
                }
            else:
                # Merge if entity appears in multiple databases
                if entity['source_db'] not in nodes[node_id]['sources']:
                    nodes[node_id]['sources'].append(entity['source_db'])
                nodes[node_id]['metadata'].update(entity['metadata'])
                nodes[node_id]['connections'].extend(entity['connections'])
        
        # Build edges by analyzing connections
        edges = []
        edge_id = 0
        
        for node_id, node_data in nodes.items():
            # Look for other entities mentioned in connections
            for connection in node_data['connections']:
                conn_text = connection['value'].lower()
                
                # Check if any other entity is mentioned
                for other_id, other_data in nodes.items():
                    if other_id != node_id:
                        if other_data['name'].lower() in conn_text:
                            edges.append({
                                'id': edge_id,
                                'source': node_id,
                                'target': other_id,
                                'type': connection['field'],
                                'description': connection['value']
                            })
                            edge_id += 1
        
        # Calculate network statistics
        stats = {
            'total_nodes': len(nodes),
            'total_edges': len(edges),
            'entity_types': defaultdict(int)
        }
        
        for node in nodes.values():
            stats['entity_types'][node['type']] += 1
        
        return {
            'investigation': investigation_name or 'All Investigations',
            'nodes': list(nodes.values()),
            'edges': edges,
            'statistics': stats
        }
    
    def export_json(self, network_data: Dict, output_path: str):
        """
        Export network as JSON
        
        Args:
            network_data: Network dictionary
            output_path: Path to save JSON
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(network_data, f, indent=2)
        
        return output_path
    
    def export_graphviz(self, network_data: Dict, output_path: str):
        """
        Export network as Graphviz DOT format
        
        Args:
            network_data: Network dictionary
            output_path: Path to save DOT file
        """
        lines = [
            'digraph EntityNetwork {',
            '  // Graph settings',
            '  rankdir=LR;',
            '  node [shape=box, style=filled, fontname="Arial"];',
            '  edge [fontname="Arial", fontsize=10];',
            ''
        ]
        
        # Define node colors by type
        type_colors = {
            'Person': '#FFE5B4',
            'Organization': '#B4D7FF',
            'Corporation': '#B4FFB4',
            'Institution': '#FFB4FF',
            'Government': '#FFB4B4',
            'Unknown': '#E0E0E0'
        }
        
        # Add nodes
        lines.append('  // Nodes')
        for node in network_data['nodes']:
            node_type = node['type']
            color = type_colors.get(node_type, '#E0E0E0')
            
            # Escape quotes in name
            name = node['name'].replace('"', '\\"')
            
            lines.append(f'  "{name}" [fillcolor="{color}", label="{name}\\n({node_type})"];')
        
        lines.append('')
        lines.append('  // Edges')
        
        # Add edges
        for edge in network_data['edges']:
            source = edge['source'].replace('"', '\\"')
            target = edge['target'].replace('"', '\\"')
            edge_type = edge['type'].replace('"', '\\"')
            
            lines.append(f'  "{source}" -> "{target}" [label="{edge_type}"];')
        
        lines.append('}')
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        return output_path
    
    def export_html(self, network_data: Dict, output_path: str):
        """
        Export network as interactive HTML with vis.js
        
        Args:
            network_data: Network dictionary
            output_path: Path to save HTML
        """
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{investigation} Network Map</title>
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
        #network {{
            width: 100%;
            height: calc(100vh - 140px);
            border: none;
        }}
        .legend {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            z-index: 1000;
        }}
        .legend h3 {{
            margin: 0 0 10px 0;
            font-size: 14px;
            color: #333;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            margin: 5px 0;
            font-size: 12px;
        }}
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 4px;
            margin-right: 8px;
            border: 1px solid #ddd;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{investigation} Entity Network</h1>
        <div class="stats">
            <strong>{total_nodes}</strong> entities | 
            <strong>{total_edges}</strong> connections
        </div>
    </div>
    
    <div id="network"></div>
    
    <div class="legend">
        <h3>Entity Types</h3>
        {legend_items}
    </div>
    
    <script>
        // Network data
        const nodes = new vis.DataSet({nodes_json});
        const edges = new vis.DataSet({edges_json});
        
        // Network options
        const options = {{
            nodes: {{
                shape: 'box',
                margin: 10,
                widthConstraint: {{
                    maximum: 200
                }},
                font: {{
                    size: 14,
                    face: 'Arial'
                }}
            }},
            edges: {{
                arrows: 'to',
                smooth: {{
                    type: 'cubicBezier',
                    forceDirection: 'horizontal',
                    roundness: 0.4
                }},
                font: {{
                    size: 12,
                    align: 'top'
                }}
            }},
            physics: {{
                enabled: true,
                barnesHut: {{
                    gravitationalConstant: -2000,
                    springConstant: 0.001,
                    springLength: 200
                }},
                stabilization: {{
                    iterations: 1000
                }}
            }},
            interaction: {{
                hover: true,
                tooltipDelay: 200
            }}
        }};
        
        // Create network
        const container = document.getElementById('network');
        const data = {{ nodes: nodes, edges: edges }};
        const network = new vis.Network(container, data, options);
        
        // Click handler for node details
        network.on('selectNode', function(params) {{
            if (params.nodes.length > 0) {{
                const nodeId = params.nodes[0];
                const node = nodes.get(nodeId);
                alert('Entity: ' + node.label + '\\nType: ' + node.title);
            }}
        }});
    </script>
</body>
</html>
"""
        
        # Define colors by type
        type_colors = {
            'Person': '#FFE5B4',
            'Organization': '#B4D7FF',
            'Corporation': '#B4FFB4',
            'Institution': '#FFB4FF',
            'Government': '#FFB4B4',
            'Unknown': '#E0E0E0'
        }
        
        # Build nodes for vis.js
        vis_nodes = []
        for node in network_data['nodes']:
            node_type = node['type']
            color = type_colors.get(node_type, '#E0E0E0')
            
            vis_nodes.append({
                'id': node['name'],
                'label': node['name'],
                'title': f"{node['type']}\\nSources: {', '.join(node['sources'])}",
                'color': color,
                'font': {'color': '#333'}
            })
        
        # Build edges for vis.js
        vis_edges = []
        for edge in network_data['edges']:
            vis_edges.append({
                'from': edge['source'],
                'to': edge['target'],
                'label': edge['type'],
                'title': edge['description']
            })
        
        # Build legend
        legend_items = []
        for entity_type, count in network_data['statistics']['entity_types'].items():
            color = type_colors.get(entity_type, '#E0E0E0')
            legend_items.append(
                f'<div class="legend-item">'
                f'<div class="legend-color" style="background-color: {color};"></div>'
                f'<span>{entity_type} ({count})</span>'
                f'</div>'
            )
        
        # Generate HTML
        html = html_template.format(
            investigation=network_data['investigation'],
            total_nodes=network_data['statistics']['total_nodes'],
            total_edges=network_data['statistics']['total_edges'],
            nodes_json=json.dumps(vis_nodes),
            edges_json=json.dumps(vis_edges),
            legend_items='\n        '.join(legend_items)
        )
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return output_path


import pandas as pd

def main():
    """Command-line interface"""
    mapper = EntityNetworkMapper()
    
    if len(sys.argv) < 2:
        print("Entity Network Mapper - Create connection visualizations")
        print()
        print("Usage:")
        print('  python entity_network_mapper.py build [investigation_name]')
        print('  python entity_network_mapper.py export <investigation> <format> <output_path>')
        print()
        print("Formats: json, graphviz, html")
        print()
        print("Examples:")
        print('  python entity_network_mapper.py build')
        print('  python entity_network_mapper.py build "Fox_News_Corp"')
        print('  python entity_network_mapper.py export "Fox_News" json network.json')
        print('  python entity_network_mapper.py export "Fox_News" html network.html')
        print('  python entity_network_mapper.py export "Fox_News" graphviz network.dot')
        return
    
    command = sys.argv[1].lower()
    
    if command == 'build':
        investigation = sys.argv[2] if len(sys.argv) > 2 else None
        
        print(f"\n[BUILD] Mapping entity network...")
        if investigation:
            print(f"Investigation: {investigation}")
        else:
            print("Scope: All investigations")
        
        network = mapper.build_network(investigation)
        
        print(f"\n[OK] Network mapped!")
        print(f"Entities: {network['statistics']['total_nodes']}")
        print(f"Connections: {network['statistics']['total_edges']}")
        
        print(f"\nEntity types:")
        for entity_type, count in network['statistics']['entity_types'].items():
            print(f"  {entity_type}: {count}")
    
    elif command == 'export':
        if len(sys.argv) < 5:
            print("Error: Missing arguments")
            print('Usage: python entity_network_mapper.py export <investigation> <format> <output_path>')
            return
        
        investigation = sys.argv[2]
        format_type = sys.argv[3].lower()
        output_path = sys.argv[4]
        
        print(f"\n[EXPORT] Building network...")
        network = mapper.build_network(investigation)
        
        if format_type == 'json':
            output = mapper.export_json(network, output_path)
        elif format_type == 'graphviz' or format_type == 'dot':
            output = mapper.export_graphviz(network, output_path)
        elif format_type == 'html':
            output = mapper.export_html(network, output_path)
        else:
            print(f"[FAIL] Unknown format: {format_type}")
            return
        
        print(f"\n[OK] Network exported!")
        print(f"Format: {format_type}")
        print(f"Entities: {network['statistics']['total_nodes']}")
        print(f"Connections: {network['statistics']['total_edges']}")
        print(f"Output: {output}")
    
    else:
        print(f"Unknown command: {command}")
        print("Valid commands: build, export")


if __name__ == '__main__':
    main()
