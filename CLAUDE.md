# Research Infrastructure Project

Personal research management and automation system for organizing investigations, generating reports, and maintaining evidence chains.

## Project Structure

```
Research/
├── Active_Investigations/     # Research investigation folders
│   ├── COVID_PCR_Truth_Investigation/
│   ├── Flight_Tracking/
│   ├── Fox_News_Corp_Investigation/
│   ├── Surveillance_Infrastructure/
│   └── Weather_Modification/
├── _System/                   # Phase 1: Core infrastructure
│   ├── file_intelligence.py   # PDF/OCR extraction, entity detection
│   ├── database_manager.py    # Unified data access and search
│   ├── source_tracker.py      # Citation and provenance tracking
│   └── auto_index.py          # INDEX.html maintenance
├── _Automation/               # Phase 2: Workflow automation
│   ├── organize_and_sync.py   # Main automation entry point
│   ├── auto_organizer.py      # File organization
│   ├── smart_categorizer.py   # AI-based file categorization
│   ├── investigation_starter.py # Create new investigations
│   ├── duplicate_detector.py  # Find duplicate files/entities
│   ├── version_control.py     # Research snapshots
│   └── github_sync.py         # Git sync operations
├── _Generation/               # Phase 3: Content generation
│   ├── timeline_builder.py    # Chronological timelines
│   ├── entity_network_mapper.py # Visual connection graphs
│   ├── report_generator.py    # HTML/Markdown reports
│   └── evidence_chain_builder.py # Document relationship analysis
├── _Intelligence/             # Phase 4: Research intelligence
├── Research_Inbox/            # Drop zone for new files
├── Output/                    # Generated outputs
├── Tools_and_Systems/         # Additional utilities
├── Archive/                   # Archived materials
└── Documents and Research/    # Reference documents
```

## Key Commands

### Daily Workflow
```bash
# Auto-organize new files and sync to GitHub
python _Automation/organize_and_sync.py

# Dry run (see what would happen)
python _Automation/organize_and_sync.py --dry-run

# Interactive mode
python _Automation/organize_and_sync.py --interactive
```

### File Operations
```bash
# Analyze any file
python _System/file_intelligence.py "path/to/file.pdf"

# Search across all databases
python _System/database_manager.py search "search term"

# Find entity connections
python _System/database_manager.py connections "Entity Name"

# Auto-categorize a file
python _Automation/smart_categorizer.py auto "document.pdf"
```

### Investigation Management
```bash
# Create new investigation
python _Automation/investigation_starter.py create "Investigation Name"

# List investigations
python _Automation/investigation_starter.py list

# Find duplicate files
python _Automation/duplicate_detector.py files

# Create snapshot
python _Automation/version_control.py snapshot "Description"
```

### Content Generation
```bash
# Build timeline
python _Generation/timeline_builder.py build "Investigation_Name"
python _Generation/timeline_builder.py export "Investigation_Name" html timeline.html

# Generate entity network
python _Generation/entity_network_mapper.py build "Investigation_Name"
python _Generation/entity_network_mapper.py export "Investigation_Name" html network.html

# Generate investigation report
python _Generation/report_generator.py export "path/to/investigation" html report.html

# Build evidence chain
python _Generation/evidence_chain_builder.py export "path/to/evidence" html chain.html
```

## Development Notes

### Python Dependencies
Core packages: PyPDF2, Pillow, pytesseract, pandas, beautifulsoup4, markdown, requests, lxml, openpyxl, python-dateutil

External: Tesseract OCR (for image text extraction)

### File Conventions
- Investigation folders go in `Active_Investigations/`
- New/unsorted files go in `Research_Inbox/`
- Files that can't be auto-categorized go to `Manual_Review/`
- Generated outputs go in `Output/`

### Database Format
- CSV files with entity tracking
- Key columns: entity name, type, connections, dates, sources
- Supported entity types: persons, organizations, events, locations, documents

### Investigation Folder Structure
```
Investigation_Name/
├── Overview.md          # Investigation summary
├── Timeline/            # Chronological data
├── Evidence/            # Source documents
├── Analysis/            # Analysis reports
├── entities.csv         # Entity database
└── README.md            # Investigation guide
```

## Web Interface

- `INDEX.html` - Main research dashboard (latest: `INDEX_v5.html`)
- `research_dashboard.html` - Research overview dashboard
- `RESEARCH_INDEX.html` - Searchable index

## Important Files

- `00_MASTER_INDEX_AND_SUBMISSION_GUIDE.md` - FOIA request tracking
- `HOW_TO_USE.md` - Quick start guide
- `QUICK_START_GUIDE.md` - Detailed getting started guide
- `COMMAND_CENTER_GUIDE.md` - Full command reference

## Batch Files (Windows)

- `ORGANIZE_AND_SYNC.bat` - Main automation (double-click to run)
- `LAUNCH_RESEARCH_PLATFORM.bat` - Open research dashboard
- `PROCESS_RESEARCH.bat` - Process new research files
