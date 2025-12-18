# PHASE 2: INVESTIGATION AUTOMATION

Automate research workflow and organization tasks.

## 🎯 Systems

### 1. Investigation Starter
Create complete investigation structures instantly.

**What it does:**
- Creates full folder structure
- Generates starter files (overview, timeline, database)
- Auto-adds to INDEX.html
- Sets up research log

**Usage:**
```bash
# Create new investigation
python investigation_starter.py create "Bill Gates Funding Networks"
python investigation_starter.py create "Pfizer Patents" "Investigation into pharmaceutical weather patents"

# List all investigations
python investigation_starter.py list

# Get statistics
python investigation_starter.py stats "Bill Gates Funding Networks"
```

**Time saved:** 10 minutes → 5 seconds per investigation

---

### 2. Smart File Categorizer
Automatically sort files into correct investigation folders.

**What it does:**
- Analyzes file content
- Identifies relevant investigations
- Suggests categorization
- Handles cross-investigation files
- Auto-updates databases

**Usage:**
```bash
# Analyze file (see suggestions)
python smart_categorizer.py analyze "document.pdf"

# Manually categorize
python smart_categorizer.py categorize "document.pdf" "Weather_Modification"

# Auto-categorize (interactive)
python smart_categorizer.py auto "document.pdf"

# Auto-categorize with options
python smart_categorizer.py auto "document.pdf" --move --threshold 5

# Batch process directory
python smart_categorizer.py batch "C:\Downloads" --move
```

**Options:**
- `--move`: Move instead of copy (default is copy)
- `--threshold N`: Minimum confidence score (default 3)

**Time saved:** Manual sorting → Automatic

---

### 3. Duplicate Detector
Find and remove duplicate files and data.

**What it does:**
- Scans for duplicate files (by content hash)
- Finds duplicate entities across databases
- Identifies similar entity names (typos)
- Suggests cleanup actions
- Calculates space savings

**Usage:**
```bash
# Scan for duplicate files
python duplicate_detector.py files
python duplicate_detector.py files "C:\Research\Active_Investigations"

# Find duplicate entities
python duplicate_detector.py entities

# Interactive cleanup
python duplicate_detector.py cleanup

# Auto cleanup
python duplicate_detector.py cleanup --auto
```

**Time saved:** Prevents duplicate work, frees disk space

---

### 4. Version Control
Track changes to research over time.

**What it does:**
- Creates snapshots of research state
- Compares snapshots
- Shows changes since last snapshot
- Tracks file additions/deletions/modifications
- Provides change history

**Usage:**
```bash
# Create snapshot
python version_control.py snapshot "Before major investigation"
python version_control.py snapshot

# List all snapshots
python version_control.py list

# Compare two snapshots
python version_control.py compare 20251210_140000 20251210_150000

# See changes since snapshot
python version_control.py changes 20251210_140000

# Get snapshot details
python version_control.py info 20251210_140000
```

**Recommended:** Create daily/weekly snapshots

**Time saved:** Never lose work, track progress

---

## 🚀 Typical Workflow

### Starting New Investigation
```bash
# 1. Create investigation
python investigation_starter.py create "New Investigation"

# 2. Add files to Downloads folder

# 3. Auto-categorize them
python smart_categorizer.py batch "C:\Downloads"

# 4. Create snapshot
python version_control.py snapshot "Started new investigation"
```

### Weekly Maintenance
```bash
# 1. Check for duplicates
python duplicate_detector.py files
python duplicate_detector.py entities

# 2. Clean up if needed
python duplicate_detector.py cleanup

# 3. See what changed this week
python version_control.py changes [last_week_snapshot_id]

# 4. Create new snapshot
python version_control.py snapshot "Weekly backup"
```

---

## 📂 File Locations

All automation tools are in:
```
C:\Users\jonat\Documents\Research\_Automation\
```

Files:
- `investigation_starter.py` - Investigation creation
- `smart_categorizer.py` - File categorization
- `duplicate_detector.py` - Duplicate detection
- `version_control.py` - Change tracking

---

## 🔧 Integration with Phase 1

Phase 2 builds on Phase 1 systems:
- Uses **File Intelligence** for content analysis
- Uses **Database Manager** for entity detection
- Uses **Source Tracker** for file tracking
- Updates **Auto-Index** automatically

---

## ⚡ Quick Reference

**New investigation:**
```bash
python investigation_starter.py create "Name"
```

**Sort file:**
```bash
python smart_categorizer.py auto "file.pdf"
```

**Find duplicates:**
```bash
python duplicate_detector.py files
```

**Take snapshot:**
```bash
python version_control.py snapshot
```

---

## 🎯 Benefits

**Before Phase 2:**
- ✋ Manual folder creation (10 minutes)
- ✋ Manual file sorting (error-prone)
- ✋ Duplicate work (no detection)
- ✋ No change tracking (lost work)

**After Phase 2:**
- ✅ Instant investigation setup (5 seconds)
- ✅ Automatic file organization
- ✅ Duplicate prevention
- ✅ Complete change history

---

## 📊 Next: Phase 3

Phase 3 will add:
- Timeline Auto-Builder
- Entity Network Mapper
- Investigation Report Generator
- Evidence Chain Builder

These will use the automation from Phase 2 to generate content automatically.
