"""
TIMELINE INTEGRATOR - Chronological Event Tracking
Maintains timeline of events discovered during research
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import re

class TimelineIntegrator:
    """Manage chronological timeline of research events"""

    def __init__(self, investigation: str):
        self.research_dir = Path(r"C:\Users\jonat\Documents\Research")
        self.investigation = investigation
        self.investigation_dir = self.research_dir / "Active_Investigations" / investigation

        # Timeline file
        self.timeline_file = self.investigation_dir / "timeline.json"

    def load_timeline(self) -> Dict:
        """Load timeline from JSON file"""
        if self.timeline_file.exists():
            try:
                with open(self.timeline_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"events": [], "metadata": {}}
        return {"events": [], "metadata": {}}

    def save_timeline(self, timeline: Dict):
        """Save timeline to JSON file"""
        self.timeline_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.timeline_file, 'w', encoding='utf-8') as f:
            json.dump(timeline, f, indent=2, ensure_ascii=False)

    def parse_date(self, date_str: str) -> str:
        """Parse and normalize date string to YYYY-MM-DD format"""
        if not date_str:
            return None

        # Try common formats
        formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%m/%d/%Y",
            "%m-%d-%Y",
            "%B %d, %Y",
            "%b %d, %Y",
            "%Y"
        ]

        for fmt in formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.strftime("%Y-%m-%d")
            except:
                continue

        # Try to extract year at least
        year_match = re.search(r'\b(19|20)\d{2}\b', date_str)
        if year_match:
            return f"{year_match.group()}-01-01"

        return None

    def generate_event_id(self, event: Dict) -> str:
        """Generate unique ID for event"""
        date = event.get('date', 'unknown')
        title = event.get('title', event.get('description', ''))[:50]
        # Simple hash-like ID
        return f"{date}_{hash(title) % 100000}"

    def integrate_events(self, new_events: List[Dict]) -> Dict:
        """Integrate new events into timeline"""

        timeline = self.load_timeline()

        if "events" not in timeline:
            timeline = {"events": [], "metadata": {}}

        stats = {
            "new_events": 0,
            "updated_events": 0,
            "duplicate_events": 0,
            "total_events": 0
        }

        # Build index of existing events
        existing_ids = {self.generate_event_id(e): e for e in timeline["events"]}

        # Process each new event
        for event_data in new_events:
            # Parse and normalize date
            raw_date = event_data.get('date', '')
            normalized_date = self.parse_date(raw_date)

            if not normalized_date:
                continue  # Skip events without valid dates

            # Build event structure
            event = {
                "date": normalized_date,
                "title": event_data.get('title', event_data.get('event', 'Untitled Event')),
                "description": event_data.get('description', event_data.get('context', '')),
                "event_type": event_data.get('event_type', 'general'),
                "entities_involved": event_data.get('entities_involved', []),
                "sources": event_data.get('sources', []),
                "importance": event_data.get('importance', 'medium'),
                "created_by": event_data.get('created_by', 'unknown'),
                "created_at": datetime.now().isoformat()
            }

            # Check for duplicates
            event_id = self.generate_event_id(event)

            if event_id in existing_ids:
                # Update existing event with new information
                existing = existing_ids[event_id]

                # Merge sources
                existing_sources = existing.get('sources', [])
                for source in event.get('sources', []):
                    if source not in existing_sources:
                        existing_sources.append(source)
                existing['sources'] = existing_sources

                # Merge entities
                existing_entities = existing.get('entities_involved', [])
                for entity in event.get('entities_involved', []):
                    if entity not in existing_entities:
                        existing_entities.append(entity)
                existing['entities_involved'] = existing_entities

                # Use longer description
                if len(event['description']) > len(existing.get('description', '')):
                    existing['description'] = event['description']

                existing['last_updated'] = datetime.now().isoformat()
                stats["updated_events"] += 1
            else:
                # Add new event
                timeline["events"].append(event)
                existing_ids[event_id] = event
                stats["new_events"] += 1

        # Sort events chronologically (newest first)
        timeline["events"].sort(key=lambda x: x.get('date', '9999-99-99'), reverse=True)

        # Update metadata
        timeline["metadata"] = {
            "investigation": self.investigation,
            "event_count": len(timeline["events"]),
            "date_range": self._get_date_range(timeline["events"]),
            "last_updated": datetime.now().isoformat()
        }

        # Save timeline
        self.save_timeline(timeline)

        stats["total_events"] = len(timeline["events"])
        return stats

    def _get_date_range(self, events: List[Dict]) -> Dict:
        """Get earliest and latest dates in timeline"""
        if not events:
            return {"earliest": None, "latest": None}

        dates = [e.get('date') for e in events if e.get('date')]
        if not dates:
            return {"earliest": None, "latest": None}

        return {
            "earliest": min(dates),
            "latest": max(dates)
        }

    def get_events_by_date_range(self, start_date: str = None, end_date: str = None) -> List[Dict]:
        """Get events within date range"""
        timeline = self.load_timeline()
        events = timeline.get("events", [])

        if start_date:
            events = [e for e in events if e.get('date', '') >= start_date]
        if end_date:
            events = [e for e in events if e.get('date', '') <= end_date]

        return events

    def get_events_by_entity(self, entity_name: str) -> List[Dict]:
        """Get events involving specific entity"""
        timeline = self.load_timeline()
        events = timeline.get("events", [])

        return [e for e in events if entity_name in e.get('entities_involved', [])]

    def export_timeline_markdown(self, filepath: Path = None):
        """Export timeline as readable Markdown"""

        timeline = self.load_timeline()
        output_file = filepath or (self.investigation_dir / "timeline.md")

        events = timeline.get("events", [])
        metadata = timeline.get("metadata", {})
        date_range = metadata.get("date_range", {})

        # Generate markdown
        md_content = f"# Timeline - {self.investigation}\n\n"
        md_content += f"**Total Events:** {len(events)}\n"
        md_content += f"**Date Range:** {date_range.get('earliest', 'Unknown')} to {date_range.get('latest', 'Unknown')}\n"
        md_content += f"**Last Updated:** {metadata.get('last_updated', 'Unknown')}\n\n"
        md_content += "---\n\n"

        # Group events by year
        events_by_year = {}
        for event in events:
            date = event.get('date', 'Unknown')
            year = date.split('-')[0] if date != 'Unknown' else 'Unknown'
            if year not in events_by_year:
                events_by_year[year] = []
            events_by_year[year].append(event)

        # Sort years
        sorted_years = sorted(events_by_year.keys(), reverse=True)

        for year in sorted_years:
            md_content += f"## {year}\n\n"

            for event in events_by_year[year]:
                date = event.get('date', 'Unknown')
                title = event.get('title', 'Untitled')
                description = event.get('description', '')
                entities = event.get('entities_involved', [])
                importance = event.get('importance', 'medium')

                # Format importance indicator
                importance_icon = {
                    'high': '[HIGH]',
                    'medium': '',
                    'low': '[low]'
                }.get(importance, '')

                md_content += f"### {date} {importance_icon}\n"
                md_content += f"**{title}**\n\n"

                if description:
                    md_content += f"{description}\n\n"

                if entities:
                    md_content += f"**Entities:** {', '.join(entities)}\n\n"

                md_content += "---\n\n"

        # Save markdown
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md_content)

        return output_file

    def export_timeline_html(self, filepath: Path = None):
        """Export timeline as interactive HTML visualization"""

        timeline = self.load_timeline()
        output_file = filepath or (self.investigation_dir / "timeline.html")

        events = timeline.get("events", [])
        metadata = timeline.get("metadata", {})

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Timeline - {self.investigation}</title>
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
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        header {{
            background: rgba(255, 165, 0, 0.1);
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            border-left: 4px solid #ffa500;
        }}
        h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .timeline {{
            position: relative;
            padding-left: 50px;
        }}
        .timeline::before {{
            content: '';
            position: absolute;
            left: 20px;
            top: 0;
            bottom: 0;
            width: 2px;
            background: linear-gradient(to bottom, #ffa500, transparent);
        }}
        .event {{
            position: relative;
            margin-bottom: 30px;
            background: rgba(255, 255, 255, 0.05);
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #ffa500;
        }}
        .event::before {{
            content: '';
            position: absolute;
            left: -34px;
            top: 20px;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #ffa500;
            border: 3px solid #0a0e14;
        }}
        .event-date {{
            color: #ffa500;
            font-weight: bold;
            font-size: 1.1em;
            margin-bottom: 10px;
        }}
        .event-title {{
            color: #00d9ff;
            font-size: 1.3em;
            margin-bottom: 10px;
        }}
        .event-description {{
            color: #e6edf3;
            margin-bottom: 10px;
            line-height: 1.6;
        }}
        .event-entities {{
            margin-top: 10px;
        }}
        .entity-tag {{
            display: inline-block;
            background: rgba(0, 255, 159, 0.2);
            color: #00ff9f;
            padding: 4px 10px;
            border-radius: 4px;
            margin-right: 5px;
            margin-top: 5px;
            font-size: 0.9em;
        }}
        .importance-high {{
            border-left-color: #ff6b35;
        }}
        .importance-high::before {{
            background: #ff6b35;
        }}
        .year-header {{
            color: #ffa500;
            font-size: 2em;
            margin: 40px 0 20px 0;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(255, 165, 0, 0.3);
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Timeline</h1>
            <p>{self.investigation}</p>
            <p style="margin-top: 10px; color: #8b95a1;">Total Events: {len(events)} | Last Updated: {metadata.get('last_updated', 'Unknown')}</p>
        </header>

        <div class="timeline">
"""

        # Group by year
        events_by_year = {}
        for event in events:
            date = event.get('date', 'Unknown')
            year = date.split('-')[0] if date != 'Unknown' else 'Unknown'
            if year not in events_by_year:
                events_by_year[year] = []
            events_by_year[year].append(event)

        sorted_years = sorted(events_by_year.keys(), reverse=True)

        for year in sorted_years:
            html += f'            <div class="year-header">{year}</div>\n'

            for event in events_by_year[year]:
                importance = event.get('importance', 'medium')
                importance_class = f"importance-{importance}" if importance == 'high' else ''

                html += f'            <div class="event {importance_class}">\n'
                html += f'                <div class="event-date">{event.get("date", "Unknown Date")}</div>\n'
                html += f'                <div class="event-title">{event.get("title", "Untitled Event")}</div>\n'

                if event.get('description'):
                    html += f'                <div class="event-description">{event["description"]}</div>\n'

                entities = event.get('entities_involved', [])
                if entities:
                    html += '                <div class="event-entities">\n'
                    for entity in entities:
                        html += f'                    <span class="entity-tag">{entity}</span>\n'
                    html += '                </div>\n'

                html += '            </div>\n'

        html += """
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

    parser = argparse.ArgumentParser(description='Integrate timeline events')
    parser.add_argument('--investigation', required=True, help='Investigation name')
    parser.add_argument('--events-file', help='JSON file with events to integrate')
    parser.add_argument('--export-md', action='store_true', help='Export as Markdown')
    parser.add_argument('--export-html', action='store_true', help='Export as HTML')

    args = parser.parse_args()

    integrator = TimelineIntegrator(investigation=args.investigation)

    if args.export_md:
        output = integrator.export_timeline_markdown()
        print(f"[OK] Timeline exported (Markdown): {output}")
    elif args.export_html:
        output = integrator.export_timeline_html()
        print(f"[OK] Timeline exported (HTML): {output}")
    elif args.events_file:
        with open(args.events_file, 'r') as f:
            events = json.load(f)
        stats = integrator.integrate_events(events)
        print(f"[OK] Timeline integration complete:")
        print(f"  - New events: {stats['new_events']}")
        print(f"  - Updated events: {stats['updated_events']}")
        print(f"  - Total events: {stats['total_events']}")


if __name__ == '__main__':
    main()
