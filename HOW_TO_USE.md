# Research Workflow - Quick Start Guide

## Your New System

I've built you an automated research workflow system. Here's how it works:

### The Simple Daily Workflow

1. **Do your research** with Claude.ai Desktop
2. **Save/export files** to: `C:\Users\jonat\Documents\Research\Research_Inbox`
3. **Double-click**: `ORGANIZE_AND_SYNC.bat` (in your Research folder)
4. **Done!** Files are automatically:
   - Organized into the right investigation folder
   - Committed to Git
   - Pushed to GitHub

### What Happens Automatically

The system:
- Reads your research files
- Figures out which investigation they belong to (Weather, COVID, Surveillance, etc.)
- Files them in the correct folder
- Syncs everything to GitHub: https://github.com/jonathondouglasyager-debug/Research

### If a File Can't Be Auto-Categorized

Files that can't be automatically categorized go to:
`C:\Users\jonat\Documents\Research\Manual_Review`

You can then manually move them to the right investigation folder.

---

## Command Line Options (Advanced)

If you want more control, open a terminal in the Research folder and run:

### Quick Commands

```bash
# Normal mode - Auto-organize and sync everything
python _Automation/organize_and_sync.py

# See what would happen without actually doing it
python _Automation/organize_and_sync.py --dry-run

# Ask before organizing each file
python _Automation/organize_and_sync.py --interactive

# Use a custom commit message
python _Automation/organize_and_sync.py --message "Added new COVID research"
```

### Individual Commands

```bash
# Only organize files (don't sync to GitHub)
python _Automation/auto_organizer.py

# Only sync to GitHub (don't organize)
python _Automation/github_sync.py

# Check what would be synced
python _Automation/github_sync.py --dry-run
```

---

## File Structure

```
Research/
├── Research_Inbox/          ← DROP FILES HERE
├── Active_Investigations/   ← Auto-organized by topic
│   ├── Weather_Modification/
│   ├── COVID_PCR_Truth_Investigation/
│   ├── Surveillance_Infrastructure/
│   └── ...
├── Manual_Review/          ← Files needing manual sorting
├── _Automation/            ← Scripts that do the work
└── ORGANIZE_AND_SYNC.bat  ← DOUBLE-CLICK THIS
```

---

## Tips

- The auto-organizer is smart but not perfect. Check `Manual_Review` folder occasionally.
- Every sync creates a Git commit with a timestamp and list of changes
- Your GitHub repo is automatically backed up: https://github.com/jonathondouglasyager-debug/Research
- You can run the workflow as many times as you want - it won't create empty commits

---

## Troubleshooting

**"No files to process"** - The Research_Inbox is empty. Add files there first.

**File went to wrong folder** - Move it manually, or update the investigation keywords in the folder's metadata.

**Sync failed** - Check your internet connection and GitHub access.

---

That's it! You now have a fully automated research organization and backup system.
