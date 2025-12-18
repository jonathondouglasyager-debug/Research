# Download Queue Manager

**Last Updated:** [Date]

---

## How This Works

This file tracks ALL documents found during research that need downloading. Each research session adds to this queue. You batch download when convenient.

**Workflow:**
1. During research → Claude adds documents here automatically
2. You copy URLs and batch download (browser extensions, wget, manual)
3. Mark as "Downloaded" with local file path
4. Archive to separate "Downloaded_Archive.md" monthly

---

## Active Download Queue

### High Priority - Download First
*Critical primary sources, government documents, technical reports*

| Session ID | Document Title | URL | File Type | Size (est.) | Status | Local Path |
|------------|----------------|-----|-----------|-------------|--------|------------|
| RS-20241202-001 | Example Report | https://example.com/doc.pdf | PDF | 2.5 MB | Pending | - |
|  |  |  |  |  |  |  |

### Medium Priority - Download Soon
*Supporting documents, secondary sources, verification materials*

| Session ID | Document Title | URL | File Type | Size (est.) | Status | Local Path |
|------------|----------------|-----|-----------|-------------|--------|------------|
|  |  |  |  |  |  |  |

### Low Priority - Reference/Archive
*Background reading, context documents, tertiary sources*

| Session ID | Document Title | URL | File Type | Size (est.) | Status | Local Path |
|------------|----------------|-----|-----------|-------------|--------|------------|
|  |  |  |  |  |  |  |

---

## Download Instructions

### Option 1: Manual Download (Simple)
```
1. Copy URL from table
2. Paste in browser
3. Save to: /Research_Documents/[Year]/[Topic]/
4. Update "Status" to "Downloaded"
5. Add local file path
```

### Option 2: Batch Download with wget (Advanced)
```bash
# Copy all High Priority URLs to a file called urls.txt (one per line)
# Then run:
wget -i urls.txt -P /Research_Documents/[Year]/[Topic]/

# Or for individual file:
wget [URL] -O /Research_Documents/[filename].pdf
```

### Option 3: Browser Extension (Recommended)
- DownThemAll (Firefox/Chrome)
- Bulk Download (Chrome)
- Copy all URLs, paste into extension, download to organized folder

---

## Status Definitions

- **Pending:** Not yet downloaded
- **Downloaded:** Saved locally, path recorded
- **Failed:** Download attempt failed - needs investigation
- **Archived:** Moved to Downloaded_Archive.md
- **Unavailable:** Source no longer accessible - note in research session

---

## Monthly Archive Process

At month end:
1. Copy all "Downloaded" entries to `Downloaded_Archive_[YYYY-MM].md`
2. Remove from this file
3. Keep only "Pending" and "Failed" items here

---

## Failed Downloads - Needs Attention

| Session ID | Document Title | URL | Issue | Alternative Source |
|------------|----------------|-----|-------|-------------------|
|  |  |  |  |  |

---

## Statistics
- **Total Pending:** [Count]
- **Total Downloaded This Month:** [Count]
- **Total Failed:** [Count]
- **Average Download Time:** [Manual tracking]

---

## Notes
- Check download queue before starting new research (avoid duplicates)
- Some PDFs may require VPN or institutional access
- Archive.org links may be slow but reliable for older documents
- Keep original URLs even after download (verification/citation purposes)
