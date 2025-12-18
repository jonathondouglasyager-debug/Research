# Phase 3: Content Generation Systems

**Status:** ✅ **COMPLETE**

Automatically generate timelines, network maps, reports, and evidence chains from your investigation data.

---

## 🎯 **WHAT PHASE 3 DOES**

Phase 3 transforms your raw investigation data into professional outputs:

1. **Timeline Auto-Builder** - Chronological timelines from database dates
2. **Entity Network Mapper** - Visual connection graphs
3. **Investigation Report Generator** - Professional HTML/MD reports
4. **Evidence Chain Builder** - Document relationship analysis

---

## 📦 **SYSTEMS OVERVIEW**

### 1. Timeline Auto-Builder (`timeline_builder.py`)

**Purpose:** Generate chronological timelines from your databases

**Features:**
- Scans databases for dates and events
- Groups events by year
- Multiple export formats (markdown, JSON, HTML)
- Interactive HTML timeline with vis.js

**Usage:**
```bash
# Build timeline for specific investigation
python timeline_builder.py build "Fox_News_Corp"

# Build timeline for all investigations
python timeline_builder.py build

# Export as HTML
python timeline_builder.py export "Fox_News" html timeline.html

# Export as markdown
python timeline_builder.py export "Fox_News" markdown timeline.md
```

**Output Formats:**
- **Markdown:** Clean text timeline
- **JSON:** Structured data
- **HTML:** Interactive visualization with scroll and zoom

---

### 2. Entity Network Mapper (`entity_network_mapper.py`)

**Purpose:** Create visual maps showing connections between entities

**Features:**
- Extracts entities from databases
- Finds relationships and connections
- Interactive network visualization
- Graphviz export for advanced layouts

**Usage:**
```bash
# Build network for specific investigation
python entity_network_mapper.py build "Fox_News_Corp"

# Export as interactive HTML
python entity_network_mapper.py export "Fox_News" html network.html

# Export as Graphviz DOT format
python entity_network_mapper.py export "Fox_News" graphviz network.dot

# Export as JSON
python entity_network_mapper.py export "Fox_News" json network.json
```

**Output Formats:**
- **HTML:** Interactive network with vis.js (drag, zoom, click)
- **Graphviz:** Professional graph layouts
- **JSON:** Structured network data

**Network Features:**
- Color-coded by entity type
- Connection strength visualization
- Hover for details
- Click for full information

---

### 3. Investigation Report Generator (`report_generator.py`)

**Purpose:** Create professional reports from investigation folders

**Features:**
- Gathers all investigation data
- Professional formatting
- Print-ready HTML
- Comprehensive markdown

**Usage:**
```bash
# Export investigation as HTML report
python report_generator.py export "C:\Research\Active_Investigations\Fox_News_Corp_Investigation" html report.html

# Export as markdown
python report_generator.py export "C:\Research\Active_Investigations\Fox_News_Corp_Investigation" markdown report.md
```

**Report Includes:**
- Executive summary with statistics
- Investigation overview
- Complete timeline
- Entity database
- Evidence inventory
- All analysis reports

**Output Formats:**
- **HTML:** Print-ready with styling
- **Markdown:** Clean text format

---

### 4. Evidence Chain Builder (`evidence_chain_builder.py`)

**Purpose:** Link documents together to show proof chains

**Features:**
- Analyzes document content
- Finds shared entities, dates, terms
- Calculates connection strength
- Visual network of evidence

**Usage:**
```bash
# Build evidence chain
python evidence_chain_builder.py build "C:\Research\Evidence" 0.2

# Export as interactive HTML
python evidence_chain_builder.py export "C:\Research\Evidence" html chain.html 0.3

# Export as markdown
python evidence_chain_builder.py export "C:\Research\Evidence" markdown chain.md
```

**Connection Strength:**
- **≥50%:** Strong connection (green)
- **30-50%:** Medium connection (yellow)
- **<30%:** Weak connection (red)

**Analyzes:**
- Shared entities
- Shared dates
- Shared key terms
- Temporal proximity
- Document type relationships

---

## 🎨 **OUTPUT EXAMPLES**

### Timeline HTML
- Vertical timeline with dates
- Color-coded by year
- Expandable events
- Source attribution

### Network Map HTML
- Interactive drag-and-drop
- Zoom and pan
- Color-coded entity types
- Click for details

### Investigation Report HTML
- Professional header
- Statistics dashboard
- Print-ready formatting
- Table of contents

### Evidence Chain HTML
- Document inventory
- Connection strength visualization
- Interactive network
- Shared entity highlighting

---

## 🔧 **HOW TO USE**

### Basic Workflow

**1. Build Timeline:**
```bash
python timeline_builder.py build "My_Investigation"
python timeline_builder.py export "My_Investigation" html timeline.html
```

**2. Map Entity Network:**
```bash
python entity_network_mapper.py build "My_Investigation"
python entity_network_mapper.py export "My_Investigation" html network.html
```

**3. Generate Report:**
```bash
python report_generator.py export "C:\path\to\investigation" html report.html
```

**4. Build Evidence Chain:**
```bash
python evidence_chain_builder.py export "C:\path\to\evidence" html chain.html
```

### Advanced Options

**Timeline with date range:**
```python
from timeline_builder import TimelineBuilder
builder = TimelineBuilder()
timeline = builder.build_timeline(
    "Fox_News",
    start_date=datetime(2023, 1, 1),
    end_date=datetime(2023, 12, 31)
)
```

**Network with custom filtering:**
```python
from entity_network_mapper import EntityNetworkMapper
mapper = EntityNetworkMapper()
network = mapper.build_network("Fox_News")
```

**Evidence chain with custom strength:**
```bash
# Only show strong connections (≥40%)
python evidence_chain_builder.py export "Evidence" html chain.html 0.4
```

---

## 📊 **FILE OUTPUTS**

All systems create files in standard formats:

**Timeline Formats:**
- `timeline.html` - Interactive visualization
- `timeline.md` - Markdown document
- `timeline.json` - Structured data

**Network Formats:**
- `network.html` - Interactive graph
- `network.dot` - Graphviz format
- `network.json` - Network data

**Report Formats:**
- `report.html` - Professional document
- `report.md` - Markdown document

**Evidence Chain Formats:**
- `chain.html` - Interactive analysis
- `chain.md` - Markdown report
- `chain.json` - Structured data

---

## 🔗 **SYSTEM INTEGRATION**

### With Phase 1 (Foundation)
- Uses `FileIntelligence` for document analysis
- Uses `DatabaseManager` for data access
- Reads from indexed files

### With Phase 2 (Automation)
- Works with investigation structures
- Processes auto-categorized files
- Integrates with version control

### Standalone Use
- Can be run independently
- Works with any folder structure
- No dependencies on other phases

---

## ⚡ **PERFORMANCE NOTES**

**Timeline Builder:**
- Fast: Processes 1000+ events in seconds
- Efficient: Uses pandas for data operations

**Network Mapper:**
- Moderate: Network analysis can take time with 100+ entities
- Optimized: Uses efficient graph algorithms

**Report Generator:**
- Fast: Gathers data in single pass
- Efficient: Minimal file I/O

**Evidence Chain:**
- Slow: Full content analysis of documents
- Resource-intensive: Extracts text from PDFs
- Optimization: Use smaller evidence sets for testing

---

## 🎯 **BEST PRACTICES**

**For Timelines:**
- Include dates in database fields
- Use consistent date formats
- Group related events

**For Networks:**
- Use entity databases with types
- Include connection fields
- Cross-reference entities

**For Reports:**
- Keep investigation folders organized
- Write analysis in markdown
- Update entity databases regularly

**For Evidence Chains:**
- Use consistent naming
- Include metadata in filenames
- Group related documents

---

## 🐛 **TROUBLESHOOTING**

**Timeline shows no events:**
- Check database date formats
- Ensure date columns exist
- Verify investigation name filter

**Network has no connections:**
- Increase minimum strength
- Check entity naming consistency
- Verify connection fields exist

**Report is incomplete:**
- Check investigation folder structure
- Ensure files exist in subfolders
- Verify CSV file formats

**Evidence chain finds no connections:**
- Lower minimum strength threshold
- Check document file formats
- Ensure OCR text is readable

---

## 📝 **SYSTEM FILES**

```
_Generation/
├── timeline_builder.py          (509 lines)
├── entity_network_mapper.py     (557 lines)
├── report_generator.py          (645 lines)
├── evidence_chain_builder.py    (668 lines)
├── README.md                     (this file)
└── test_generation.py           (testing script)
```

**Total:** 4 systems, 2,379 lines of code

---

## 🚀 **NEXT PHASE**

**Phase 4: Research Intelligence** (Coming next)
- AI-powered analysis
- Pattern detection
- Anomaly identification
- Automated insights

---

## 💡 **TIPS**

**Export everything:**
```bash
# Full investigation output
python timeline_builder.py export "Investigation" html timeline.html
python entity_network_mapper.py export "Investigation" html network.html
python report_generator.py export "path/to/investigation" html report.html
```

**Quick visualization:**
```bash
# Fastest way to visualize
python entity_network_mapper.py build "Investigation"
```

**Evidence analysis:**
```bash
# Start with low threshold
python evidence_chain_builder.py build "Evidence" 0.1
```

---

**Phase 3 Complete! Ready for content generation.** 🎉
