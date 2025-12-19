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
Integration Controller Runs
  ├─ Entities added to database
  ├─ Fuzzy matching (merges duplicates)
  ├─ Timeline events extracted
  └─ Glossary terms identified
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

## 🔍 Monitor Your Agents

```cmd
# Open in browser:
start Tools_and_Systems\Master_Research_Hub\agent_monitor_dashboard.html
```

Or double-click the **Research Intelligence Platform** desktop shortcut!

Shows:
- Active agents and their status
- Completed agents
- Pending integrations
- Real-time updates every 5 seconds

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
