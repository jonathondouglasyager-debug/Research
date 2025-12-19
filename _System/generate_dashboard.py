"""
Generate standalone HTML dashboard with embedded data
"""

import json
import csv
from pathlib import Path
from datetime import datetime

def generate_dashboard():
    """Generate self-contained HTML dashboard"""

    research_dir = Path(r"C:\Users\jonat\Documents\Research")

    # Load agent state
    state_file = research_dir / "_System" / "agent_manager_state.json"

    if not state_file.exists():
        print("[ERROR] No agent data found yet")
        return

    with open(state_file, 'r') as f:
        state = json.load(f)

    agents = state.get('agents', {})

    # Load entity database
    entity_db = research_dir / "Active_Investigations" / "COVID_PCR_Truth_Investigation" / "entity_database.csv"
    entities = []

    if entity_db.exists():
        with open(entity_db, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            entities = list(reader)

    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Research Intelligence Dashboard</title>
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
            min-height: 100vh;
        }}
        .container {{
            max-width: 1600px;
            margin: 0 auto;
        }}
        header {{
            background: rgba(255, 255, 255, 0.05);
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            border-left: 4px solid #00d9ff;
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
            background: rgba(255, 255, 255, 0.05);
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #00ff9f;
            text-align: center;
        }}
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            display: block;
            margin-bottom: 5px;
        }}
        .stat-label {{
            color: #8b95a1;
            font-size: 0.9em;
        }}
        .section {{
            background: rgba(255, 255, 255, 0.03);
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .section h2 {{
            color: #00d9ff;
            margin-bottom: 20px;
            font-size: 1.5em;
        }}
        .agent-card {{
            background: rgba(255, 255, 255, 0.05);
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 4px solid #00ff9f;
        }}
        .agent-id {{
            font-weight: bold;
            font-family: 'Courier New', monospace;
            color: #00d9ff;
            margin-bottom: 10px;
        }}
        .agent-question {{
            color: #e6edf3;
            margin: 10px 0;
            font-style: italic;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th {{
            background: rgba(0, 217, 255, 0.1);
            color: #00d9ff;
            padding: 12px;
            text-align: left;
            border-bottom: 2px solid #00d9ff;
        }}
        td {{
            padding: 12px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        tr:hover {{
            background: rgba(255, 255, 255, 0.05);
        }}
        .timestamp {{
            text-align: center;
            color: #8b95a1;
            margin-top: 30px;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Research Intelligence Dashboard</h1>
            <p>COVID PCR Truth Investigation</p>
        </header>

        <div class="stats-grid">
            <div class="stat-card">
                <span class="stat-number" style="color: #00d9ff;">{state.get('total_spawned', 0)}</span>
                <span class="stat-label">Total Agents</span>
            </div>
            <div class="stat-card">
                <span class="stat-number" style="color: #00ff9f;">{state.get('total_completed', 0)}</span>
                <span class="stat-label">Completed</span>
            </div>
            <div class="stat-card">
                <span class="stat-number" style="color: #ffa500;">{len(entities)}</span>
                <span class="stat-label">Entities Tracked</span>
            </div>
            <div class="stat-card">
                <span class="stat-number" style="color: #ff6b35;">{state.get('total_failed', 0)}</span>
                <span class="stat-label">Failed</span>
            </div>
        </div>

        <div class="section">
            <h2>Research Agents</h2>
"""

    # Add agents
    for agent_id, agent in agents.items():
        html += f"""
            <div class="agent-card">
                <div class="agent-id">{agent_id}</div>
                <div class="agent-question">"{agent.get('question', 'No question')}"</div>
                <div style="font-size: 0.9em; color: #8b95a1; margin-top: 10px;">
                    Status: <span style="color: #00ff9f;">{agent.get('status', 'unknown')}</span> |
                    Created: {agent.get('created', 'N/A')}
                </div>
            </div>
"""

    html += """
        </div>

        <div class="section">
            <h2>Entity Database</h2>
            <table>
                <thead>
                    <tr>
                        <th>Entity Name</th>
                        <th>Type</th>
                        <th>Description</th>
                        <th>First Mentioned</th>
                        <th>Last Updated</th>
                    </tr>
                </thead>
                <tbody>
"""

    # Add entities
    for entity in entities:
        html += f"""
                    <tr>
                        <td><strong>{entity.get('Entity_Name', 'N/A')}</strong></td>
                        <td>{entity.get('Entity_Type', 'N/A')}</td>
                        <td>{entity.get('Description', 'N/A')[:100]}...</td>
                        <td>{entity.get('First_Mentioned', 'N/A')}</td>
                        <td>{entity.get('Last_Updated', 'N/A')}</td>
                    </tr>
"""

    html += f"""
                </tbody>
            </table>
        </div>

        <div class="timestamp">
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>
"""

    # Save dashboard
    output_file = research_dir / "research_dashboard.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"[OK] Dashboard generated: {output_file}")
    return output_file

if __name__ == '__main__':
    output = generate_dashboard()
    if output:
        import subprocess
        subprocess.run(['cmd', '/c', 'start', '', str(output)])
