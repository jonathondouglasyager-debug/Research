# Claude Desktop Custom Instructions for Research Intelligence Platform

## Copy This Into Your Claude Desktop Custom Instructions

```
RESEARCH WORKFLOW CONTEXT:

I have a Research Intelligence Platform that automatically processes research findings. Here's how it works:

WORKFLOW:
1. I do research with you in Claude Desktop
2. You create executive summaries with "Next Steps" sections
3. I save the file to: C:\Users\jonat\Documents\Research\Research_Inbox
4. I run the auto-processor to spawn research agents
5. Agents execute research and findings integrate automatically

IMPORTANT COMMANDS:
When I'm ready to process research, generate these exact commands for me:

```cmd
cd C:\Users\jonat\Documents\Research
python _Automation\auto_process.py
```

Or for fully automatic mode:
```cmd
cd C:\Users\jonat\Documents\Research
python _Automation\auto_process.py --auto
```

FORMATTING REQUIREMENTS:
When creating research documents, always include:
- **Investigation:** field at the top (e.g., COVID_PCR_Truth_Investigation)
- **Next Steps** section with numbered research questions
- Clear entity mentions in the content
- Sources with links

EXAMPLE FORMAT:
```markdown
# Research Title

**Date:** YYYY-MM-DD
**Investigation:** Investigation_Name

## Executive Summary
[Your findings]

## Next Steps
1. Research question one
2. Research question two
3. Research question three

## Sources
- [Source 1](url)
```

When I say "process my research" or "run the platform", immediately provide the commands above formatted ready to copy-paste into a terminal.
```

---

## Quick Reference Commands

### Process Latest Research (Interactive)
```cmd
cd C:\Users\jonat\Documents\Research
python _Automation\auto_process.py
```
- Finds newest file in Research_Inbox
- Shows you what it will do
- Asks for confirmation

### Process Automatically (No Prompts)
```cmd
cd C:\Users\jonat\Documents\Research
python _Automation\auto_process.py --auto
```
- Fully automatic
- Spawns agents → Integrates → Syncs to GitHub

### Process Specific File
```cmd
cd C:\Users\jonat\Documents\Research
python _Automation\auto_process.py --file "Research_Inbox\YOUR_FILE.md" --investigation "Investigation_Name"
```

### Monitor Agents
```cmd
cd C:\Users\jonat\Documents\Research
start Tools_and_Systems\Master_Research_Hub\agent_monitor_dashboard.html
```

### Manual Steps (If Needed)

**Step 1: Spawn Agents**
```cmd
python _System\agent_manager.py process --document "Research_Inbox\FILE.md" --investigation "Investigation_Name"
```

**Step 2: Integrate Findings**
```cmd
python _System\integration_controller.py run
```

**Step 3: Sync to GitHub**
```cmd
python _Automation\organize_and_sync.py
```

---

## How to Add to Claude Desktop

1. Open Claude Desktop
2. Click Settings (gear icon)
3. Find "Custom Instructions" or "Memory"
4. Copy the text from the box at the top of this file
5. Paste it into custom instructions
6. Save

Now when you chat with Claude Desktop, just say:
- "process my research"
- "give me the commands"
- "run the platform"

And Claude will give you the exact commands to run!
