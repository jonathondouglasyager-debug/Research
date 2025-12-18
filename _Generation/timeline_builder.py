"""
TIMELINE AUTO-BUILDER
Automatically generate chronological timelines from investigation data
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import json
import re
from collections import defaultdict

# Import Phase 1 systems
sys.path.append(str(Path(__file__).parent.parent / '_System'))
from database_manager import DatabaseManager

class TimelineBuilder:
    """
    Automatically generate timelines from investigation data
    """
    
    def __init__(self, research_dir: str = None):
        """Initialize with research directory"""
        if research_dir is None:
            research_dir = r"C:\Users\jonat\Documents\Research"
        self.research_dir = Path(research_dir)
        self.db_manager = DatabaseManager()
        
        # Common date patterns to extract
        self.date_patterns = [
            # Full dates
            (r'\b(\d{4})-(\d{2})-(\d{2})\b', '%Y-%m-%d'),  # 2023-04-18
            (r'\b(\d{2})/(\d{2})/(\d{4})\b', '%m/%d/%Y'),  # 04/18/2023
            (r'\b(\w+)\s+(\d{1,2}),?\s+(\d{4})\b', '%B %d %Y'),  # April 18, 2023
            # Year only
            (r'\b(19\d{2}|20\d{2})\b', '%Y'),  # 1996, 2023
            # Month Year
            (r'\b(\w+)\s+(19\d{2}|20\d{2})\b', '%B %Y'),  # April 2023
        ]
    
    def extract_dates_from_text(self, text: str) -> list:
        """
        Extract dates from text using multiple patterns
        
        Args:
            text: Text to extract dates from
        
        Returns:
            List of (date_string, parsed_date) tuples
        """
        dates = []
        
        for pattern, date_format in self.date_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                date_str = match.group(0)
                try:
                    # Try to parse the date
                    if date_format == '%Y':
                        # For year-only, use January 1
                        parsed = datetime(int(match.group(1)), 1, 1)
                    else:
                        parsed = datetime.strptime(date_str, date_format)
                    dates.append((date_str, parsed))
                except:
                    continue
        
        return dates
    
    def scan_databases_for_events(self, investigation_name: str = None) -> list:
        """
        Scan databases for events with dates
        
        Args:
            investigation_name: Optional filter for specific investigation
        
        Returns:
            List of event dictionaries
        """
        events = []
        databases = self.db_manager.list_databases()
        
        for db_name, db_info in databases.items():
            # Skip if filtering by investigation
            if investigation_name and investigation_name.lower() not in db_name.lower():
                continue
            
            df = db_info['dataframe']
            
            # Look for date columns
            date_cols = [col for col in df.columns if any(
                keyword in col.lower() 
                for keyword in ['date', 'time', 'year', 'when']
            )]
            
            # Look for event/description columns
            event_cols = [col for col in df.columns if any(
                keyword in col.lower()
                for keyword in ['event', 'description', 'title', 'summary']
            )]
            
            # Process each row
            for idx, row in df.iterrows():
                event_data = {}
                
                # Extract dates
                for date_col in date_cols:
                    if pd.notna(row[date_col]):
                        date_value = str(row[date_col])
                        extracted_dates = self.extract_dates_from_text(date_value)
                        if extracted_dates:
                            event_data['date'] = extracted_dates[0][1]
                            event_data['date_str'] = extracted_dates[0][0]
                            break
                
                # Extract event description
                for event_col in event_cols:
                    if pd.notna(row[event_col]):
                        event_data['description'] = str(row[event_col])
                        break
                
                # Add source
                event_data['source'] = db_name
                event_data['row_index'] = idx
                
                # Add other relevant fields
                for col in df.columns:
                    if col not in date_cols and col not in event_cols:
                        if pd.notna(row[col]):
                            event_data[col] = str(row[col])
                
                # Only add if we have a date and description
                if 'date' in event_data and 'description' in event_data:
                    events.append(event_data)
        
        return events
    
    def build_timeline(self, investigation_name: str = None, 
                      start_date: datetime = None, 
                      end_date: datetime = None) -> dict:
        """
        Build a complete timeline
        
        Args:
            investigation_name: Optional investigation filter
            start_date: Optional start date filter
            end_date: Optional end date filter
        
        Returns:
            Dictionary with timeline data
        """
        # Scan for events
        events = self.scan_databases_for_events(investigation_name)
        
        # Filter by date range
        if start_date:
            events = [e for e in events if e['date'] >= start_date]
        if end_date:
            events = [e for e in events if e['date'] <= end_date]
        
        # Sort chronologically
        events.sort(key=lambda x: x['date'])
        
        # Group by year
        events_by_year = defaultdict(list)
        for event in events:
            year = event['date'].year
            events_by_year[year].append(event)
        
        return {
            'investigation': investigation_name or 'All Investigations',
            'total_events': len(events),
            'date_range': {
                'start': min(e['date'] for e in events).isoformat() if events else None,
                'end': max(e['date'] for e in events).isoformat() if events else None
            },
            'events': events,
            'events_by_year': dict(events_by_year)
        }
    
    def export_markdown(self, timeline_data: dict, output_path: str):
        """
        Export timeline as markdown
        
        Args:
            timeline_data: Timeline dictionary from build_timeline
            output_path: Path to save markdown file
        """
        md_lines = [
            f"# {timeline_data['investigation']} Timeline",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**Total Events:** {timeline_data['total_events']}",
            ""
        ]
        
        if timeline_data['date_range']['start']:
            start = timeline_data['date_range']['start'][:10]
            end = timeline_data['date_range']['end'][:10]
            md_lines.append(f"**Date Range:** {start} to {end}")
            md_lines.append("")
        
        md_lines.append("---")
        md_lines.append("")
        
        # Group by year
        for year in sorted(timeline_data['events_by_year'].keys()):
            md_lines.append(f"## {year}")
            md_lines.append("")
            
            year_events = timeline_data['events_by_year'][year]
            for event in sorted(year_events, key=lambda x: x['date']):
                date_str = event['date'].strftime('%B %d, %Y')
                md_lines.append(f"### {date_str}")
                md_lines.append("")
                md_lines.append(f"**{event['description']}**")
                md_lines.append("")
                
                # Add additional fields
                for key, value in event.items():
                    if key not in ['date', 'date_str', 'description', 'source', 'row_index']:
                        md_lines.append(f"- {key}: {value}")
                
                md_lines.append(f"- Source: {event['source']}")
                md_lines.append("")
        
        # Write file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_lines))
        
        return output_path
    
    def export_json(self, timeline_data: dict, output_path: str):
        """
        Export timeline as JSON
        
        Args:
            timeline_data: Timeline dictionary
            output_path: Path to save JSON file
        """
        # Convert datetime objects to strings
        json_data = {
            'investigation': timeline_data['investigation'],
            'total_events': timeline_data['total_events'],
            'date_range': timeline_data['date_range'],
            'events': [
                {
                    **event,
                    'date': event['date'].isoformat()
                }
                for event in timeline_data['events']
            ]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2)
        
        return output_path
    
    def export_html(self, timeline_data: dict, output_path: str):
        """
        Export timeline as interactive HTML
        
        Args:
            timeline_data: Timeline dictionary
            output_path: Path to save HTML file
        """
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{investigation} Timeline</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 20px;
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
        .timeline {{
            position: relative;
            padding-left: 40px;
        }}
        .timeline:before {{
            content: '';
            position: absolute;
            left: 15px;
            top: 0;
            bottom: 0;
            width: 2px;
            background: #ddd;
        }}
        .year {{
            margin: 40px 0 20px 0;
        }}
        .year h2 {{
            color: #2c5aa0;
            font-size: 24px;
            margin: 0;
        }}
        .event {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin: 15px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            position: relative;
        }}
        .event:before {{
            content: '';
            position: absolute;
            left: -33px;
            top: 25px;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #2c5aa0;
            border: 3px solid white;
            box-shadow: 0 0 0 2px #2c5aa0;
        }}
        .event-date {{
            color: #2c5aa0;
            font-weight: 600;
            font-size: 14px;
            margin-bottom: 8px;
        }}
        .event-description {{
            color: #333;
            font-size: 16px;
            margin-bottom: 12px;
            font-weight: 500;
        }}
        .event-details {{
            color: #666;
            font-size: 14px;
            line-height: 1.6;
        }}
        .event-details div {{
            margin: 4px 0;
        }}
        .source {{
            color: #999;
            font-size: 12px;
            font-style: italic;
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{investigation} Timeline</h1>
        <div class="stats">
            <strong>{total_events}</strong> events tracked | 
            Generated: {generated_date}
        </div>
    </div>
    
    <div class="timeline">
        {timeline_content}
    </div>
</body>
</html>
"""
        
        # Build timeline content
        timeline_html = []
        for year in sorted(timeline_data['events_by_year'].keys()):
            timeline_html.append(f'<div class="year"><h2>{year}</h2></div>')
            
            year_events = timeline_data['events_by_year'][year]
            for event in sorted(year_events, key=lambda x: x['date']):
                date_str = event['date'].strftime('%B %d, %Y')
                
                details = []
                for key, value in event.items():
                    if key not in ['date', 'date_str', 'description', 'source', 'row_index']:
                        details.append(f'<div><strong>{key}:</strong> {value}</div>')
                
                details_html = '\n'.join(details)
                
                event_html = f"""
        <div class="event">
            <div class="event-date">{date_str}</div>
            <div class="event-description">{event['description']}</div>
            <div class="event-details">
                {details_html}
            </div>
            <div class="source">Source: {event['source']}</div>
        </div>
"""
                timeline_html.append(event_html)
        
        # Generate final HTML
        html = html_template.format(
            investigation=timeline_data['investigation'],
            total_events=timeline_data['total_events'],
            generated_date=datetime.now().strftime('%Y-%m-%d %H:%M'),
            timeline_content='\n'.join(timeline_html)
        )
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return output_path


import pandas as pd

def main():
    """Command-line interface"""
    builder = TimelineBuilder()
    
    if len(sys.argv) < 2:
        print("Timeline Auto-Builder - Generate chronological timelines from data")
        print()
        print("Usage:")
        print('  python timeline_builder.py build [investigation_name]')
        print('  python timeline_builder.py export <investigation> <format> <output_path>')
        print()
        print("Formats: markdown, json, html")
        print()
        print("Examples:")
        print('  python timeline_builder.py build')
        print('  python timeline_builder.py build "Fox_News_Corp"')
        print('  python timeline_builder.py export "Fox_News" markdown timeline.md')
        print('  python timeline_builder.py export "Fox_News" html timeline.html')
        return
    
    command = sys.argv[1].lower()
    
    if command == 'build':
        investigation = sys.argv[2] if len(sys.argv) > 2 else None
        
        print(f"\n[BUILD] Generating timeline...")
        if investigation:
            print(f"Investigation: {investigation}")
        else:
            print("Scope: All investigations")
        
        timeline = builder.build_timeline(investigation)
        
        print(f"\n[OK] Timeline generated!")
        print(f"Total events: {timeline['total_events']}")
        
        if timeline['date_range']['start']:
            start = timeline['date_range']['start'][:10]
            end = timeline['date_range']['end'][:10]
            print(f"Date range: {start} to {end}")
        
        print(f"\nEvents by year:")
        for year in sorted(timeline['events_by_year'].keys()):
            count = len(timeline['events_by_year'][year])
            print(f"  {year}: {count} events")
    
    elif command == 'export':
        if len(sys.argv) < 5:
            print("Error: Missing arguments")
            print('Usage: python timeline_builder.py export <investigation> <format> <output_path>')
            return
        
        investigation = sys.argv[2]
        format_type = sys.argv[3].lower()
        output_path = sys.argv[4]
        
        print(f"\n[EXPORT] Generating timeline...")
        timeline = builder.build_timeline(investigation)
        
        if format_type == 'markdown' or format_type == 'md':
            output = builder.export_markdown(timeline, output_path)
        elif format_type == 'json':
            output = builder.export_json(timeline, output_path)
        elif format_type == 'html':
            output = builder.export_html(timeline, output_path)
        else:
            print(f"[FAIL] Unknown format: {format_type}")
            return
        
        print(f"\n[OK] Timeline exported!")
        print(f"Format: {format_type}")
        print(f"Events: {timeline['total_events']}")
        print(f"Output: {output}")
    
    else:
        print(f"Unknown command: {command}")
        print("Valid commands: build, export")


if __name__ == '__main__':
    main()
