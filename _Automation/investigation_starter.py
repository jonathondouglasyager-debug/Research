"""
INVESTIGATION STARTER
Create new investigation folders and files instantly
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import json

class InvestigationStarter:
    """
    Rapidly create new investigation structures
    """
    
    def __init__(self, research_dir: str = None):
        """Initialize with research directory"""
        if research_dir is None:
            research_dir = r"C:\Users\jonat\Documents\Research"
        self.research_dir = Path(research_dir)
        self.active_investigations_dir = self.research_dir / 'Active_Investigations'
        
        # Template for investigation overview
        self.overview_template = """# {investigation_name} Investigation

**Created:** {date}
**Status:** Active
**Lead Researcher:** Your Name

---

## 🎯 Investigation Objectives

[What are you trying to prove or discover?]

- Objective 1
- Objective 2
- Objective 3

---

## 🔍 Research Questions

1. [Key question 1]
2. [Key question 2]
3. [Key question 3]

---

## 📊 Current Findings

### Key Entities Identified
- Entity 1: [Brief description]
- Entity 2: [Brief description]

### Important Dates
- [Date]: [Event]

### Connections Discovered
- [Entity A] → [Entity B]: [Type of connection]

---

## 📁 File Organization

- **Evidence/**: Primary source documents
- **Timeline/**: Chronological documentation
- **Corporate_Networks/**: Entity relationship mapping
- **Analysis/**: Research notes and conclusions

---

## 🚧 Next Steps

1. [Next research task]
2. [Next research task]
3. [Next research task]

---

## 📝 Research Log

### {date}
- Started investigation
- Created folder structure
- [Your first notes here]

"""
        
        # CSV database template
        self.entity_db_template = """Entity_Name,Entity_Type,Description,First_Mentioned,Source,Role,Connections,Status,Notes
"""
        
        # Research log template
        self.research_log_template = """# Research Log: {investigation_name}

---

## {date}

### Activities
- Investigation started
- Folder structure created

### Findings
- [Your findings here]

### Questions
- [Questions that arose]

### Next Steps
- [What to investigate next]

---

"""
    
    def create_investigation(self, investigation_name: str, description: str = None) -> dict:
        """
        Create complete investigation structure
        
        Args:
            investigation_name: Name of investigation (e.g., "Bill_Gates_Funding")
            description: Optional brief description
        
        Returns:
            Dictionary with created paths
        """
        # Sanitize name for folder
        folder_name = investigation_name.replace(' ', '_').replace('/', '_').replace('\\', '_')
        
        investigation_path = self.active_investigations_dir / folder_name
        
        # Check if already exists
        if investigation_path.exists():
            return {
                'error': f'Investigation already exists at {investigation_path}',
                'path': str(investigation_path)
            }
        
        # Create folder structure
        folders = {
            'main': investigation_path,
            'evidence': investigation_path / 'Evidence',
            'timeline': investigation_path / 'Timeline',
            'corporate_networks': investigation_path / 'Corporate_Networks',
            'analysis': investigation_path / 'Analysis'
        }
        
        for name, path in folders.items():
            path.mkdir(parents=True, exist_ok=True)
        
        # Create overview file
        overview_content = self.overview_template.format(
            investigation_name=investigation_name,
            date=datetime.now().strftime('%Y-%m-%d')
        )
        overview_path = investigation_path / 'investigation_overview.md'
        with open(overview_path, 'w', encoding='utf-8') as f:
            f.write(overview_content)
        
        # Create entity database
        entity_db_path = investigation_path / 'entity_database.csv'
        with open(entity_db_path, 'w', encoding='utf-8') as f:
            f.write(self.entity_db_template)
        
        # Create research log
        research_log_content = self.research_log_template.format(
            investigation_name=investigation_name,
            date=datetime.now().strftime('%Y-%m-%d')
        )
        research_log_path = investigation_path / 'research_log.md'
        with open(research_log_path, 'w', encoding='utf-8') as f:
            f.write(research_log_content)
        
        # Create timeline template
        timeline_path = investigation_path / 'Timeline' / 'timeline.md'
        with open(timeline_path, 'w', encoding='utf-8') as f:
            f.write(f"# {investigation_name} Timeline\n\n")
            f.write("## Chronological Events\n\n")
            f.write("- **[Date]**: [Event description]\n")
        
        # Create README in each subfolder
        for folder_name, folder_path in folders.items():
            if folder_name != 'main':
                readme_path = folder_path / 'README.md'
                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write(f"# {folder_name.replace('_', ' ').title()}\n\n")
                    f.write(f"Store {folder_name.replace('_', ' ')} files here.\n")
        
        # Create metadata file
        metadata = {
            'name': investigation_name,
            'description': description or f'Investigation into {investigation_name}',
            'created_date': datetime.now().isoformat(),
            'status': 'active',
            'folder_path': str(investigation_path),
            'files_created': [
                str(overview_path.relative_to(self.research_dir)),
                str(entity_db_path.relative_to(self.research_dir)),
                str(research_log_path.relative_to(self.research_dir)),
                str(timeline_path.relative_to(self.research_dir))
            ]
        }
        
        metadata_path = investigation_path / 'investigation_metadata.json'
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        return {
            'success': True,
            'investigation_name': investigation_name,
            'path': str(investigation_path),
            'folders': {k: str(v) for k, v in folders.items()},
            'files': {
                'overview': str(overview_path),
                'entity_database': str(entity_db_path),
                'research_log': str(research_log_path),
                'timeline': str(timeline_path),
                'metadata': str(metadata_path)
            }
        }
    
    def list_investigations(self) -> list:
        """List all existing investigations"""
        if not self.active_investigations_dir.exists():
            return []
        
        investigations = []
        for item in self.active_investigations_dir.iterdir():
            if item.is_dir() and not item.name.startswith('_'):
                metadata_path = item / 'investigation_metadata.json'
                if metadata_path.exists():
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                    investigations.append(metadata)
                else:
                    investigations.append({
                        'name': item.name,
                        'path': str(item),
                        'status': 'active'
                    })
        
        return investigations
    
    def get_investigation_stats(self, investigation_name: str) -> dict:
        """Get statistics for an investigation"""
        folder_name = investigation_name.replace(' ', '_')
        investigation_path = self.active_investigations_dir / folder_name
        
        if not investigation_path.exists():
            return {'error': 'Investigation not found'}
        
        # Count files in each subfolder
        stats = {
            'total_files': 0,
            'evidence_files': 0,
            'timeline_files': 0,
            'analysis_files': 0
        }
        
        for root, dirs, files in os.walk(investigation_path):
            for file in files:
                stats['total_files'] += 1
                if 'Evidence' in root:
                    stats['evidence_files'] += 1
                elif 'Timeline' in root:
                    stats['timeline_files'] += 1
                elif 'Analysis' in root:
                    stats['analysis_files'] += 1
        
        return stats


def main():
    """Command-line interface"""
    starter = InvestigationStarter()
    
    if len(sys.argv) < 2:
        print("Investigation Starter - Create new investigations instantly")
        print()
        print("Usage:")
        print("  python investigation_starter.py create <name> [description]")
        print("  python investigation_starter.py list")
        print("  python investigation_starter.py stats <name>")
        print()
        print("Examples:")
        print('  python investigation_starter.py create "Bill Gates Funding Networks"')
        print('  python investigation_starter.py create "Pfizer Weather Patents" "Investigation into pharmaceutical weather modification"')
        print('  python investigation_starter.py list')
        print('  python investigation_starter.py stats "Bill Gates Funding Networks"')
        return
    
    command = sys.argv[1].lower()
    
    if command == 'create':
        if len(sys.argv) < 3:
            print("Error: Investigation name required")
            print('Usage: python investigation_starter.py create "Investigation Name" [description]')
            return
        
        name = sys.argv[2]
        description = sys.argv[3] if len(sys.argv) > 3 else None
        
        print(f"\nCreating investigation: {name}")
        result = starter.create_investigation(name, description)
        
        if 'error' in result:
            print(f"\n[FAIL] {result['error']}")
        else:
            print(f"\n[SUCCESS] Investigation created!")
            print(f"\nPath: {result['path']}")
            print(f"\nFolders created:")
            for folder_type, path in result['folders'].items():
                print(f"  - {folder_type}: {Path(path).name}")
            print(f"\nFiles created:")
            for file_type, path in result['files'].items():
                print(f"  - {file_type}: {Path(path).name}")
            print(f"\nNext steps:")
            print(f"  1. Open investigation_overview.md and fill in objectives")
            print(f"  2. Add source documents to Evidence/ folder")
            print(f"  3. Start building timeline in Timeline/timeline.md")
    
    elif command == 'list':
        investigations = starter.list_investigations()
        
        if not investigations:
            print("\nNo investigations found.")
            print('Create one with: python investigation_starter.py create "Investigation Name"')
        else:
            print(f"\n[OK] Found {len(investigations)} investigations:")
            print()
            for inv in investigations:
                print(f"  - {inv['name']}")
                if 'created_date' in inv:
                    print(f"    Created: {inv['created_date'][:10]}")
                print(f"    Status: {inv.get('status', 'active')}")
                print()
    
    elif command == 'stats':
        if len(sys.argv) < 3:
            print("Error: Investigation name required")
            print('Usage: python investigation_starter.py stats "Investigation Name"')
            return
        
        name = sys.argv[2]
        stats = starter.get_investigation_stats(name)
        
        if 'error' in stats:
            print(f"\n[FAIL] {stats['error']}")
        else:
            print(f"\n[OK] Statistics for: {name}")
            print(f"\nTotal files: {stats['total_files']}")
            print(f"Evidence files: {stats['evidence_files']}")
            print(f"Timeline files: {stats['timeline_files']}")
            print(f"Analysis files: {stats['analysis_files']}")
    
    else:
        print(f"Unknown command: {command}")
        print("Valid commands: create, list, stats")


if __name__ == '__main__':
    main()
