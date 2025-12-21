# Research Intelligence Platform - Quick Start Guide

## 🚀 The Simplest Workflow

### From Claude Desktop to Full Processing in 3 Steps:

**1. Do Research with Claude Desktop**
- Research your topic
- Get executive summary with "Next Steps" section
- Save file to: `C:\Users\jonat\Documents\Research\Research_Inbox`

**2. Run Auto-Processor**
```cmd
cd C:\Users\jonat\Documents\Research
python _Automation\auto_process.py
```
- Choose option 1 (Run all commands)
- Or use `--auto` flag for zero prompts

**3. Done!**
- Agents spawn automatically
- Research executes in background
- Findings integrate into databases
- Everything syncs to GitHub

---

## 📋 Copy-Paste Commands

### Interactive Mode (Recommended First Time)
```cmd
cd C:\Users\jonat\Documents\Research
python _Automation\auto_process.py
```
Shows you what it will do, asks for confirmation.

### Fully Automatic (No Prompts)
```cmd
cd C:\Users\jonat\Documents\Research
python _Automation\auto_process.py --auto
```
Just runs everything.

### Double-Click Option
Or just double-click: **`PROCESS_RESEARCH.bat`** in your Research folder!

---

## 🎯 What Actually Happens

```
Your Research File (with "Next Steps")
  ↓
Auto-Processor Detects Latest File
  ↓
Spawns Research Agents (one per question)
  ↓
Agents Execute Research
  ↓
FULL CIRCLE INTEGRATION:
  ├─ Entities: Added to database with fuzzy matching
  ├─ Glossary: Terms added to local + master glossaries
  ├─ Timeline: Events added chronologically
  ├─ Network: Knowledge graph updated with connections
  └─ Cross-References: Entity relationships tracked globally
  ↓
VISUALIZATIONS GENERATED:
  ├─ Interactive Document (live entity links, tooltips - Phase 3!)
  ├─ Consolidated Report (all findings combined)
  ├─ Timeline HTML (interactive chronological view)
  ├─ Network Graph (entity relationship visualization)
  ├─ Glossary Markdown (term definitions)
  └─ Cross-Reference Report (global connections)
  ↓
Git Auto-Commits Everything
  ↓
GitHub Sync (automatic backup)
  ↓
DONE - Knowledge Base Expanded!
```

---

## 📝 Research Document Format

Make sure your research files have this format:

```markdown
# Title

**Date:** 2025-12-19
**Investigation:** COVID_PCR_Truth_Investigation

## Executive Summary
Your findings here...

## Next Steps
1. First research question
2. Second research question
3. Third research question

## Sources
- [Source Title](url)
```

**IMPORTANT:**
- Use plain investigation names (not bold/italic)
- `COVID_PCR_Truth_Investigation` ✅
- `**COVID_PCR_Truth_Investigation**` ❌ (will cause errors)

---

## 🖥️ Desktop Shortcuts

**Research Intelligence Platform** → Opens agent monitor dashboard

**Process Research** → Runs auto-processor (coming soon)

---

## 🔍 View Your Results

After processing, you get **6 interactive visualizations** per investigation (Phase 3 complete!):

### 1. Interactive Research Document (NEW - Phase 3!) ✨
**Location:** `Active_Investigations\{Investigation}\{YourFile}_interactive.html`

**Features:**
- **Clickable Entities** - Click any entity name to see full details
- **Hover Tooltips** - Hover over entities to see quick info
- **Glossary Terms** - Hover over terms for instant definitions
- **Source Citations** - Click citations to see sources
- **Rich Formatting** - Beautiful, readable layout
- **Navigation Links** - Quick links to all other visualizations

**Special Syntax:**
- `[[Entity Name]]` → Interactive entity link with tooltip
- `[[term]]` → Glossary term with definition popup
- `[[src_123]]` → Clickable source citation

### 2. Consolidated Research Report (Main Overview)
**Location:** `Active_Investigations\{Investigation}\Consolidated_Research_Report.html`

Shows:
- All agent findings combined
- Entities discovered across all agents
- Timeline events preview
- Glossary terms preview
- Recommended next research steps
- All sources referenced

### 3. Timeline Visualization
**Location:** `Active_Investigations\{Investigation}\timeline.html`

Shows:
- Chronological events discovered
- Grouped by year
- Entities involved in each event
- Color-coded by importance

### 4. Knowledge Graph Network
**Location:** `Active_Investigations\{Investigation}\Knowledge_Graph\network_visualization.html`

Shows:
- Interactive network of entities
- Visual relationships between entities
- Click and drag to explore
- Connection strength visualization

### 5. Glossary Reference
**Location:** `Active_Investigations\{Investigation}\glossary.md`

Shows:
- All terms defined during research
- Alphabetically organized
- Context for each term
- Mention counts

### 6. Cross-Reference Report (Global View)
**Location:** `_Intelligence\cross_reference_report.html`

Shows:
- Entities appearing in multiple investigations
- Strongest co-occurrence patterns
- Global research connections
- Cross-investigation insights

### Monitor Agents in Real-Time
```cmd
# Open in browser:
start Tools_and_Systems\Master_Research_Hub\agent_monitor_dashboard.html
```

Or double-click the **Research Intelligence Platform** desktop shortcut!

### View Raw Data
- **Entity Database:** `Active_Investigations\{Investigation}\entity_database.csv`
- **Network Data:** `Active_Investigations\{Investigation}\Knowledge_Graph\network.json`
- **Glossary Data:** `Active_Investigations\{Investigation}\glossary.json`
- **Timeline Data:** `Active_Investigations\{Investigation}\timeline.json`
- **Master Glossary:** `_Intelligence\master_glossary.json`
- **Cross-References:** `_Intelligence\cross_references.json`

---

## 🛠️ Manual Steps (If Needed)

If you want to run steps individually:

### Step 1: Spawn Agents
```cmd
python _System\agent_manager.py process --document "Research_Inbox\FILE.md" --investigation "Investigation_Name"
```

### Step 2: Integrate Findings
```cmd
python _System\integration_controller.py run
```

### Step 3: Sync to GitHub
```cmd
python _Automation\organize_and_sync.py
```

---

## 📄 Document Analysis (NEW in Phase 2!)

Process PDFs, Excel, CSV, Word documents directly:

### Analyze a PDF
```cmd
python _System\agent_manager.py document --document "path\to\file.pdf" --investigation "Investigation_Name"
```

### Analyze Excel Spreadsheet
```cmd
python _System\agent_manager.py document --document "data.xlsx" --investigation "Investigation_Name"
```

### Analyze CSV Data
```cmd
python _System\agent_manager.py document --document "data.csv" --investigation "Investigation_Name"
```

### With Specific Research Question
```cmd
python _System\agent_manager.py document --document "file.pdf" --investigation "Investigation_Name" --question "What are the key findings about X?"
```

**Supported Formats:**
- PDF (.pdf)
- Excel (.xlsx, .xls)
- CSV (.csv)
- Word (.docx, .doc)
- Text (.txt)
- Markdown (.md)

**What Gets Extracted:**
- Full text content
- Tables and data
- Entities (companies, people, organizations)
- Timeline events (dates mentioned)
- Glossary terms (acronyms, definitions)
- Statistics (for data files)

---

## 🆘 Troubleshooting

**"No files found in Research_Inbox"**
- Add your research file to: `C:\Users\jonat\Documents\Research\Research_Inbox`

**Investigation name error**
- Don't use bold/italic in investigation name (**Investigation** ❌)
- Use plain text (Investigation ✅)

**Agents not running**
- Check agent monitor dashboard
- Look in: `Active_Investigations\{Investigation}\Agent_Findings\`

**Nothing integrated**
- Run: `python _System\integration_controller.py run`
- Check logs: `_System\logs\integration_log_YYYY-MM-DD.json`

---

## 📚 Investigation Names

Current investigations you can use:
- `COVID_PCR_Truth_Investigation`
- `Weather_Modification`
- `Fox_News_Corp_Investigation`
- `Surveillance_Infrastructure`
- `Flight_Tracking`
- `Media_Ownership`
- `General_Research` (default if none detected)

---

## 🎓 Claude Desktop Custom Instructions

See: `CLAUDE_DESKTOP_INSTRUCTIONS.md` for instructions to add to Claude Desktop.

Once added, you can just tell Claude:
- "process my research"
- "give me the commands"
- "run the platform"

And it will give you the exact commands to copy-paste!

---

**That's it! Your research workflow is now fully automated.** 🚀
