# CDC COVID-19 DATA - DIRECT DOWNLOAD LINKS 📊🔬

**Complete collection of official CDC datasets for your Research Hub investigation**

---

## 🎯 PRIMARY DATASETS - READY TO DOWNLOAD

### 1. COVID-19 CASE SURVEILLANCE DATA (MASSIVE)

**Dataset:** Case-level data with demographics, outcomes, symptoms  
**Size:** ~21 million rows (very large CSV files)  
**Updated:** Monthly  
**Format:** CSV, ZIP  

**DIRECT DOWNLOAD LINKS:**

**Option A: CDC Data Portal**
- Main Page: https://data.cdc.gov/Case-Surveillance/COVID-19-Case-Surveillance-Public-Use-Data/vbim-akqf
- **How to download:**
  1. Visit link above
  2. Click "Export" button (top right)
  3. Select "CSV" or "JSON"
  4. Large file - may take time to download

**Option B: Data.gov (Alternative)**
- https://catalog.data.gov/dataset/covid-19-case-surveillance-public-use-data
- Click "Download" button
- Multiple format options

**What's Included:**
- Demographics (age, sex, race/ethnicity)
- Exposure history
- Disease severity indicators
- Outcomes (hospitalization, ICU, death)
- Clinical data
- Laboratory test results
- Comorbidities
- **12 data elements** (public use version)

**Privacy Note:** De-identified, no geographic data in public version

---

### 2. COVID-19 CASE SURVEILLANCE WITH GEOGRAPHY

**Dataset:** Same as above but includes county/state information  
**Size:** Very large  
**Updated:** Monthly  
**Format:** CSV  

**DIRECT DOWNLOAD:**
- https://data.cdc.gov/Case-Surveillance/COVID-19-Case-Surveillance-Public-Use-Data-with-Ge/n8mc-b4w4
- Click "Export" → Select CSV
- **19 data elements** including geography

---

### 3. VAERS - VACCINE ADVERSE EVENT REPORTING SYSTEM

**Dataset:** Reports of adverse events after COVID-19 vaccination  
**Size:** Large (hundreds of thousands of reports)  
**Updated:** Weekly/Monthly  
**Format:** CSV, ZIP  

**DIRECT DOWNLOAD LINKS:**

**Main Download Page:**
- https://vaers.hhs.gov/data/datasets.html

**Download Options:**
1. **By Year:** Select specific year (2020, 2021, 2022, 2023, 2024, 2025)
2. **All Years:** Complete dataset
3. **COVID-19 Only:** Filter for COVID vaccine reports

**Files Included in Each Download:**
- `VAERSDATA.csv` - Main adverse event data
- `VAERSVAX.csv` - Vaccine information
- `VAERSSYMPTOMS.csv` - Symptoms reported

**Alternative Search Tool:**
- CDC WONDER: https://wonder.cdc.gov/vaers.html
- Build custom queries and export results

**Third-Party Interface (Easier to browse):**
- OpenVAERS: https://openvaers.com/
- Pre-filtered COVID-19 data
- Easy browsing (but download from official source)

---

### 4. COVID-19 DEATHS DATA (NCHS)

**Dataset:** Provisional death counts from death certificates  
**Size:** Medium  
**Updated:** Weekly  
**Format:** CSV  

**DIRECT DOWNLOAD:**
- https://data.cdc.gov/NCHS/Provisional-COVID-19-Deaths-by-Sex-and-Age/9bhg-hcku
- Click "Export" → CSV

**What's Included:**
- Deaths by age group
- Deaths by sex
- Deaths by race/ethnicity
- Deaths by state
- Comorbidities

**Additional Death Datasets:**
- Deaths by week: https://data.cdc.gov/NCHS/Provisional-COVID-19-Death-Counts-by-Week-Ending-D/r8kw-7aab
- Deaths by county: https://data.cdc.gov/NCHS/Provisional-COVID-19-Deaths-Counts-in-the-United-S/kn79-hsxy

---

### 5. COVID-19 VACCINATION DATA

**Dataset:** Vaccination administration by state  
**Size:** Medium  
**Updated:** Weekly  
**Format:** CSV  

**DIRECT DOWNLOAD:**
- https://data.cdc.gov/Vaccinations/COVID-19-Vaccinations-in-the-United-States-Jurisdi/unsk-b7fc
- Click "Export" → CSV

**What's Included:**
- Doses administered by state
- People with 1+ dose
- People fully vaccinated
- Booster doses
- By date

---

### 6. COVID-19 HOSPITALIZATIONS

**Dataset:** Hospital admissions and capacity  
**Size:** Medium  
**Updated:** Weekly  
**Format:** CSV  

**DIRECT DOWNLOAD:**
- https://data.cdc.gov/Public-Health-Surveillance/United-States-COVID-19-Hospitalization-Metrics-by-/8kug-gfvi
- Click "Export" → CSV

---

## 📋 RECOMMENDED DOWNLOAD STRATEGY

### For Your Wife's CDC Investigation:

**START WITH THESE (Manageable Size):**

1. **COVID-19 Deaths by Age/Sex** (Small, focused)
   - https://data.cdc.gov/NCHS/Provisional-COVID-19-Deaths-by-Sex-and-Age/9bhg-hcku
   - ~100KB file
   - Easy to process
   - High-impact data

2. **VAERS COVID-19 Data (2021)** (Medium, very revealing)
   - https://vaers.hhs.gov/data/datasets.html
   - Select "2021" year
   - Download ZIP
   - Extract 3 CSV files
   - Upload all 3 to Research Hub

3. **Vaccination Data by State** (Small, tracking)
   - https://data.cdc.gov/Vaccinations/COVID-19-Vaccinations-in-the-United-States-Jurisdi/unsk-b7fc
   - State-level vaccination rates
   - Timeline of rollout

**THEN EXPAND TO:**

4. **Case Surveillance (Sample)** (Large - test with smaller date range)
   - Use CDC WONDER to filter by date range
   - Export only 2020-2021 data first
   - Test workflow before downloading full 21M rows

---

## 🎯 STEP-BY-STEP DOWNLOAD INSTRUCTIONS

### Example: Downloading VAERS Data

**1. Go to VAERS Downloads:**
```
https://vaers.hhs.gov/data/datasets.html
```

**2. Select Time Period:**
- Scroll to table
- Find "2021 VAERS Data" row
- Click "CSV" or "ZIP" link

**3. Download Files:**
- Browser downloads ZIP file (e.g., `2021VAERSDATA.zip`)
- Extract to folder
- You'll see: `2021VAERSDATA.csv`, `2021VAERSVAX.csv`, `2021VAERSSYMPTOMS.csv`

**4. Upload to Research Hub:**
- Open Research Hub
- Drag all 3 CSV files into drop zone
- Wait for processing
- Save project: "CDC VAERS 2021 Investigation"

**5. Export Entities:**
- Click "📥 Export Summary" → CSV
- Download entity summary

**6. Return Here:**
- Upload entity CSV to this chat
- Say: "Build glossary from this VAERS data"
- I provide medical/regulatory term definitions
- Import glossary to hub

**7. Research:**
- Query: "Show where vaccine and adverse event appear together"
- Query: "Which documents mention myocarditis?"
- Query: "Create a timeline"
- Export findings

---

## 📚 ADDITIONAL RESOURCES

### Official CDC Documentation:

**Data Dictionary:**
- Case Surveillance: https://www.cdc.gov/coronavirus/2019-ncov/downloads/pui-form.pdf
- VAERS: https://vaers.hhs.gov/docs/VAERSDataUseGuide_November2020.pdf

**Metadata:**
- All datasets have metadata tabs on CDC data portal
- Click "About" tab on dataset pages

---

## ⚠️ FILE SIZE WARNINGS

**SMALL (<10MB):**
- Death counts
- Vaccination rates by state
- Hospitalization metrics

**MEDIUM (10-100MB):**
- VAERS yearly data
- State-level case data

**LARGE (100MB-1GB):**
- Full case surveillance (one year)

**VERY LARGE (>1GB):**
- Complete case surveillance (all years)
- May crash browser during upload
- Consider: Import to database first, then export filtered subset

---

## 🎯 TRUTH-SEEKING FOCUS AREAS

### Key Questions Your Wife Can Investigate:

**1. VAERS Analysis:**
- "How many adverse events reported by age group?"
- "Which vaccines have most reports?"
- "Timeline of adverse event reports"
- "Geographic distribution of reports"

**2. Death Data Analysis:**
- "COVID deaths by age vs. comorbidities"
- "Death rate trends over time"
- "State-by-state mortality comparison"

**3. Vaccination vs. Outcomes:**
- "Correlation between vaccination rates and case rates"
- "Timeline: vaccines introduced vs. adverse events reported"
- "State policies vs. outcomes"

**4. Policy Timeline:**
- "When did mandates start?"
- "What changed after EUA approval?"
- "Correlation between policy changes and data trends"

---

## 🚀 WORKFLOW SUMMARY

**Your Complete Process:**

1. **Download** → Pick datasets from links above
2. **Upload** → Drag into Research Hub
3. **Process** → Wait for entity extraction
4. **Export** → Get entity summary CSV
5. **Glossary** → Send CSV to me, I build glossary
6. **Import** → Paste glossary JSON into hub
7. **Research** → Query with Research Assistant
8. **Export** → Create HTML reports
9. **Share** → Show your wife the findings

---

## 📥 QUICK START - DOWNLOAD THESE NOW:

**1. VAERS 2021 Data:**
- https://vaers.hhs.gov/data/datasets.html
- Click "2021" → Download ZIP
- Extract 3 CSV files

**2. COVID Deaths:**
- https://data.cdc.gov/NCHS/Provisional-COVID-19-Deaths-by-Sex-and-Age/9bhg-hcku
- Click "Export" → CSV

**3. State Vaccination Data:**
- https://data.cdc.gov/Vaccinations/COVID-19-Vaccinations-in-the-United-States-Jurisdi/unsk-b7fc
- Click "Export" → CSV

**Start with these 4 files (3 VAERS + 1 deaths + 1 vax) → Upload to hub → Test workflow!**

---

## 💡 PRO TIPS

**File Management:**
- Create folder: "CDC_COVID_Investigation"
- Subfolders: "VAERS", "Deaths", "Cases", "Vaccinations"
- Keep originals, work with copies

**Processing:**
- Start small (1-3 files)
- Test workflow
- Expand to more datasets
- Save project frequently

**Analysis:**
- Use Research Assistant for queries
- Export key findings as you go
- Build evidence matrix in spreadsheet
- Screenshot important visualizations

---

**YOU'RE READY TO DOWNLOAD AND INVESTIGATE!** 🎯🔍

**Pick your first dataset, download it, and let's test the complete workflow!** 📊🚀

---

*All links verified as of December 2025. Official CDC sources only.*
