# RESEARCH INFRASTRUCTURE - PHASE 1 CORE SYSTEMS

**Built:** December 10, 2025  
**Status:** ✅ OPERATIONAL

---

## 🎯 WHAT YOU HAVE

**4 Core Python Systems** that power your entire research infrastructure:

1. **File Intelligence** - Smart file processing and analysis
2. **Database Manager** - Unified access to all your data
3. **Source Tracker** - Evidence provenance and citations
4. **Enhanced Auto-Index** - Automatic INDEX.html maintenance

---

## 📦 INSTALLATION COMPLETE

### Python Packages Installed:
- PyPDF2 (PDF text extraction)
- Pillow (Image processing)
- pytesseract (OCR - text from images)
- pandas (CSV/data analysis)
- beautifulsoup4 (HTML processing)
- markdown (Markdown generation)
- requests (Web requests)
- lxml (XML/HTML parsing)
- openpyxl (Excel files)
- python-dateutil (Date parsing)

### External Dependencies:
- Tesseract OCR (for image text extraction)

---

## 🚀 HOW TO USE

### 1. FILE INTELLIGENCE

**Analyze any file:**
```bash
cd C:\Users\jonat\Documents\Research\_System
python file_intelligence.py "path\to\file.pdf"
```

**Features:**
- Detects file type automatically
- Extracts text from PDFs
- OCR for scanned documents/images
- Extracts dates, entities, URLs
- Auto-categorizes into investigations
- Provides full metadata

### 2. DATABASE MANAGER

**View all databases:**
```bash
python database_manager.py
```

**Search across everything:**
```bash
python database_manager.py search Raytheon
```

**Find entity mentions:**
```bash
python database_manager.py entity "Operation Popeye"
```

**Find entity connections:**
```bash
python database_manager.py connections Raytheon
```

**Features:**
- Auto-discovers all CSV databases
- Unified search across all data
- Entity tracking
- Cross-referencing
- Connection mapping

### 3. SOURCE TRACKER

**View statistics:**
```bash
python source_tracker.py
```

**Register a source:**
```bash
python source_tracker.py register "path\to\document.pdf"
```

**Generate citation:**
```bash
python source_tracker.py cite <source_id> apa
```

**Verify all sources:**
```bash
python source_tracker.py verify
```

**Export bibliography:**
```bash
python source_tracker.py export bibliography.md apa
```

**Features:**
- Registers all source documents
- Links claims to sources
- Generates citations (APA, MLA, Chicago)
- Builds evidence chains
- Tracks provenance

### 4. ENHANCED AUTO-INDEX

**Scan for new files:**
```bash
python auto_index.py scan
```

**View statistics:**
```bash
python auto_index.py stats
```

**Process specific file:**
```bash
python auto_index.py process "path\to\file.pdf"
```

**Features:**
- Auto-scans research directory
- Processes new files intelligently
- Updates INDEX.html automatically
- Categorizes files
- Registers sources
- Never lose a file

---

## 📊 WHAT EACH SYSTEM DOES

### FILE INTELLIGENCE
**Input:** Any file  
**Output:** Complete analysis with metadata, entities, categorization

**Use when:** 
- Dropping new research documents
- Need to extract information from PDFs
- Want to OCR scanned documents
- Need automatic categorization

### DATABASE MANAGER
**Input:** Search query or entity name  
**Output:** Matching records across all databases

**Use when:**
- Searching for entities (Raytheon, HAARP, etc.)
- Finding cross-references
- Tracking entity connections
- Need unified data access

### SOURCE TRACKER
**Input:** Document filepath or claim text  
**Output:** Source registration, citations, evidence chains

**Use when:**
- Need to cite sources
- Building evidence chains
- Tracking document provenance
- Verifying sources
- Preparing bibliographies

### AUTO-INDEX
**Input:** Research directory  
**Output:** Updated INDEX.html with all files tracked

**Use when:**
- Adding new files to research
- Want automatic organization
- Need INDEX.html updated
- Running scheduled maintenance

---

## 🔄 TYPICAL WORKFLOW

**1. Drop new PDF into research folder:**
```
You save: report.pdf → Active_Investigations\Weather_Modification\
```

**2. Run auto-index scan:**
```bash
python auto_index.py scan
```

**3. System automatically:**
- Extracts text from PDF
- Identifies key entities (Raytheon, HAARP, dates)
- Categorizes as "weather_modification"
- Registers as source document
- Updates INDEX.html
- Adds to searchable databases

**4. Search for information:**
```bash
python database_manager.py search "cloud seeding"
```

**5. Build evidence chain:**
```python
# In Python script or interactive mode
from source_tracker import SourceTracker
st = SourceTracker()

# Chain showing military weather control
st.build_evidence_chain(
    "Military Weather Control",
    ["Owning Weather 2025 doctrine", 
     "Raytheon NOAA contract",
     "Tennessee weather modification ban"]
)
```

---

## 🎯 INTEGRATION WITH INDEX.HTML

All systems work together with your INDEX.html:

1. **File Intelligence** → Categorizes files
2. **Database Manager** → Powers search
3. **Source Tracker** → Provides citations
4. **Auto-Index** → Updates INDEX.html

**Result:** Click-run-done workflow

---

## 📁 FILE LOCATIONS

```
C:\Users\jonat\Documents\Research\
├── _System\              ← Core systems (YOU ARE HERE)
│   ├── file_intelligence.py
│   ├── database_manager.py
│   ├── source_tracker.py
│   ├── auto_index.py
│   ├── config.json
│   ├── source_registry.json  (auto-created)
│   └── index_state.json     (auto-created)
│
├── Active_Investigations\   ← Your research
├── Output\                  ← Generated files
├── Tools_and_Systems\       ← Research hub tools
└── INDEX.html               ← Main interface
```

---

## 🔧 CONFIGURATION

Edit `config.json` to customize:
- Research directory path
- Auto-scan interval
- Default citation style
- Investigation keywords
- Output directories

---

## 🐛 TROUBLESHOOTING

**"Module not found"**
→ Run: `pip install <module_name>`

**"Tesseract not found"**
→ Check PATH environment variable includes Tesseract directory

**"No databases found"**
→ Make sure CSV files exist in research directory

**"Can't update INDEX.html"**
→ Check INDEX.html exists at: `C:\Users\jonat\Documents\Research\INDEX.html`

---

## 📈 NEXT STEPS

**Phase 2 - Investigation Automation** (Build Tomorrow):
- Investigation Starter (one-command setup)
- Smart File Categorizer (auto-place files)
- Duplicate Detector (find redundant work)
- Version Control (track all changes)

**Phase 3 - Content Generation** (Build Day 3):
- Timeline Auto-Builder
- Entity Network Mapper
- Investigation Report Generator
- Evidence Chain Builder

**Phases 4 & 5** (Build Days 4-5):
- Research intelligence features
- Presentation and export systems

---

## 🎉 YOU'RE READY

**Test the system:**
1. Drop a PDF into research folder
2. Run: `python auto_index.py scan`
3. Watch it process automatically
4. Search: `python database_manager.py search Raytheon`
5. See results!

**Your research infrastructure is now SMART and AUTOMATED.**

---

Last Updated: December 10, 2025
