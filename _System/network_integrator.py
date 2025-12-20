"""
NETWORK INTEGRATOR - Knowledge Graph Builder
Creates and maintains network of relationships between entities
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set
from collections import defaultdict

class NetworkIntegrator:
    """Build and manage knowledge graph of entity relationships"""

    def __init__(self, investigation: str):
        self.research_dir = Path(r"C:\Users\jonat\Documents\Research")
        self.investigation = investigation
        self.investigation_dir = self.research_dir / "Active_Investigations" / investigation
        self.network_dir = self.investigation_dir / "Knowledge_Graph"

        # Create directory
        self.network_dir.mkdir(parents=True, exist_ok=True)

        # Network file
        self.network_file = self.network_dir / "network.json"

    def load_network(self) -> Dict:
        """Load network from JSON file"""
        if self.network_file.exists():
            try:
                with open(self.network_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"nodes": {}, "edges": [], "metadata": {}}
        return {"nodes": {}, "edges": [], "metadata": {}}

    def save_network(self, network: Dict):
        """Save network to JSON file"""
        with open(self.network_file, 'w', encoding='utf-8') as f:
            json.dump(network, f, indent=2, ensure_ascii=False)

    def add_node(self, network: Dict, entity_name: str, entity_type: str, properties: Dict = None):
        """Add or update node in network"""
        if entity_name not in network["nodes"]:
            network["nodes"][entity_name] = {
                "name": entity_name,
                "type": entity_type,
                "properties": properties or {},
                "first_seen": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "degree": 0  # Will be calculated
            }
        else:
            # Update existing node
            node = network["nodes"][entity_name]
            node["last_updated"] = datetime.now().isoformat()
            if properties:
                node["properties"].update(properties)

    def add_edge(self, network: Dict, source: str, target: str, relationship: str, properties: Dict = None):
        """Add relationship between entities"""

        # Create edge
        edge = {
            "source": source,
            "target": target,
            "relationship": relationship,
            "properties": properties or {},
            "created_at": datetime.now().isoformat()
        }

        # Check if edge already exists
        edge_exists = False
        for existing_edge in network["edges"]:
            if (existing_edge["source"] == source and
                existing_edge["target"] == target and
                existing_edge["relationship"] == relationship):
                # Update properties
                existing_edge["properties"].update(properties or {})
                existing_edge["last_updated"] = datetime.now().isoformat()
                edge_exists = True
                break

        if not edge_exists:
            network["edges"].append(edge)

    def calculate_metrics(self, network: Dict):
        """Calculate network metrics (degree, centrality, etc.)"""

        # Calculate degree for each node
        degree_count = defaultdict(int)
        for edge in network["edges"]:
            degree_count[edge["source"]] += 1
            degree_count[edge["target"]] += 1

        for node_name, node in network["nodes"].items():
            node["degree"] = degree_count[node_name]

        # Find most connected nodes
        sorted_nodes = sorted(
            network["nodes"].items(),
            key=lambda x: x[1]["degree"],
            reverse=True
        )

        return {
            "total_nodes": len(network["nodes"]),
            "total_edges": len(network["edges"]),
            "most_connected": [(name, data["degree"]) for name, data in sorted_nodes[:10]]
        }

    def integrate_relationships(self, entities: List[Dict], connections_data: List[Dict] = None) -> Dict:
        """Integrate entities and their relationships into network"""

        network = self.load_network()

        stats = {
            "new_nodes": 0,
            "updated_nodes": 0,
            "new_edges": 0,
            "total_nodes": 0,
            "total_edges": 0
        }

        # Add nodes from entities
        for entity in entities:
            entity_name = entity.get('name', '')
            entity_type = entity.get('type', 'Unknown')

            if not entity_name:
                continue

            was_new = entity_name not in network["nodes"]

            properties = {
                "description": entity.get('description', ''),
                "role": entity.get('role', ''),
                "source": entity.get('source', '')
            }

            self.add_node(network, entity_name, entity_type, properties)

            if was_new:
                stats["new_nodes"] += 1
            else:
                stats["updated_nodes"] += 1

            # Parse connections field for relationships
            connections_str = entity.get('connections', '')
            if connections_str:
                # Simple parsing: "Entity1, Entity2, Entity3"
                connected_entities = [e.strip() for e in connections_str.split(',') if e.strip()]
                for connected in connected_entities:
                    # Add node if doesn't exist
                    if connected not in network["nodes"]:
                        self.add_node(network, connected, "Unknown", {})

                    # Add edge
                    self.add_edge(network, entity_name, connected, "connected_to")
                    stats["new_edges"] += 1

        # Add explicit connections if provided
        if connections_data:
            for conn in connections_data:
                source = conn.get('source', '')
                target = conn.get('target', '')
                relationship = conn.get('relationship', 'related_to')
                properties = conn.get('properties', {})

                if source and target:
                    self.add_edge(network, source, target, relationship, properties)
                    stats["new_edges"] += 1

        # Calculate metrics
        metrics = self.calculate_metrics(network)

        # Update metadata
        network["metadata"] = {
            "investigation": self.investigation,
            "total_nodes": metrics["total_nodes"],
            "total_edges": metrics["total_edges"],
            "most_connected": metrics["most_connected"],
            "last_updated": datetime.now().isoformat()
        }

        # Save network
        self.save_network(network)

        stats["total_nodes"] = metrics["total_nodes"]
        stats["total_edges"] = metrics["total_edges"]

        return stats

    def export_network_html(self, filepath: Path = None):
        """Export network as interactive HTML visualization"""

        network = self.load_network()
        output_file = filepath or (self.network_dir / "network_visualization.html")

        metadata = network.get("metadata", {})

        # Prepare data for visualization
        nodes_data = []
        for name, node in network["nodes"].items():
            nodes_data.append({
                "id": name,
                "label": name,
                "type": node.get("type", "Unknown"),
                "degree": node.get("degree", 0)
            })

        edges_data = []
        for edge in network["edges"]:
            edges_data.append({
                "from": edge["source"],
                "to": edge["target"],
                "label": edge.get("relationship", "related")
            })

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Knowledge Graph - {self.investigation}</title>
    <script src="https://unpkg.com/vis-network@9.1.2/standalone/umd/vis-network.min.js"></script>
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
        }}
        header {{
            background: rgba(255, 255, 255, 0.05);
            padding: 20px 30px;
            border-bottom: 2px solid rgba(0, 217, 255, 0.3);
        }}
        h1 {{
            font-size: 2em;
            margin-bottom: 10px;
        }}
        #network {{
            width: 100%;
            height: calc(100vh - 100px);
            background: rgba(0, 0, 0, 0.2);
        }}
        .stats {{
            padding: 10px 30px;
            background: rgba(0, 217, 255, 0.1);
            color: #8b95a1;
        }}
    </style>
</head>
<body>
    <header>
        <h1>Knowledge Graph</h1>
        <p>{self.investigation}</p>
    </header>
    <div class="stats">
        Nodes: {metadata.get('total_nodes', 0)} | Edges: {metadata.get('total_edges', 0)} |
        Last Updated: {metadata.get('last_updated', 'Unknown')}
    </div>
    <div id="network"></div>

    <script>
        const nodes = new vis.DataSet({json.dumps(nodes_data)});
        const edges = new vis.DataSet({json.dumps(edges_data)});

        const container = document.getElementById('network');
        const data = {{
            nodes: nodes,
            edges: edges
        }};

        const options = {{
            nodes: {{
                shape: 'dot',
                size: 16,
                font: {{
                    size: 14,
                    color: '#e6edf3'
                }},
                borderWidth: 2,
                shadow: true,
                color: {{
                    border: '#00d9ff',
                    background: '#0a0e14',
                    highlight: {{
                        border: '#00ff9f',
                        background: '#1a2332'
                    }}
                }}
            }},
            edges: {{
                width: 2,
                color: {{
                    color: '#00d9ff',
                    highlight: '#00ff9f'
                }},
                arrows: {{
                    to: {{
                        enabled: true,
                        scaleFactor: 0.5
                    }}
                }},
                font: {{
                    size: 10,
                    color: '#8b95a1',
                    align: 'middle'
                }},
                smooth: {{
                    type: 'continuous'
                }}
            }},
            physics: {{
                forceAtlas2Based: {{
                    gravitationalConstant: -50,
                    centralGravity: 0.01,
                    springLength: 100,
                    springConstant: 0.08
                }},
                maxVelocity: 50,
                solver: 'forceAtlas2Based',
                timestep: 0.35,
                stabilization: {{
                    iterations: 150
                }}
            }}
        }};

        const network = new vis.Network(container, data, options);
    </script>
</body>
</html>
"""

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        return output_file

    def export_network_json(self, filepath: Path = None):
        """Export network in standard graph format"""
        network = self.load_network()
        output_file = filepath or (self.network_dir / "network_export.json")

        # Convert to standard format
        export_data = {
            "nodes": list(network["nodes"].values()),
            "edges": network["edges"],
            "metadata": network["metadata"]
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)

        return output_file


def main():
    """Command-line interface"""
    import argparse

    parser = argparse.ArgumentParser(description='Integrate network relationships')
    parser.add_argument('--investigation', required=True, help='Investigation name')
    parser.add_argument('--entities-file', help='JSON file with entities')
    parser.add_argument('--export-html', action='store_true', help='Export as HTML visualization')
    parser.add_argument('--export-json', action='store_true', help='Export as JSON')

    args = parser.parse_args()

    integrator = NetworkIntegrator(investigation=args.investigation)

    if args.export_html:
        output = integrator.export_network_html()
        print(f"[OK] Network exported (HTML): {output}")
    elif args.export_json:
        output = integrator.export_network_json()
        print(f"[OK] Network exported (JSON): {output}")
    elif args.entities_file:
        with open(args.entities_file, 'r') as f:
            entities = json.load(f)
        stats = integrator.integrate_relationships(entities)
        print(f"[OK] Network integration complete:")
        print(f"  - New nodes: {stats['new_nodes']}")
        print(f"  - Updated nodes: {stats['updated_nodes']}")
        print(f"  - New edges: {stats['new_edges']}")
        print(f"  - Total nodes: {stats['total_nodes']}")
        print(f"  - Total edges: {stats['total_edges']}")


if __name__ == '__main__':
    main()
