# 🚀 PROJECT EXECUTION GUIDE - PyCharm Setup & Running

## Quick Setup (5 minutes)

### Step 1: Open Project in PyCharm

1. File → Open → Select project folder
2. PyCharm will detect Python and offer to create virtual environment
3. Click "Create" to setup venv automatically

### Step 2: Install Dependencies

**Method 1 (Recommended - Automatic)**
- PyCharm will detect `requirements.txt`
- Click notification "Install requirements"
- Wait for installation to complete

**Method 2 (Manual)**
```bash
# In PyCharm Terminal:
pip install -r requirements.txt
```

### Step 3: Configure Data File

1. Ensure `data/Airbnb_data.csv` exists (6.8 MB)
2. Update `config.py` if needed:
   ```python
   RAW_DATA_PATH = DATA_DIR / "Airbnb_data.csv"  # Line 19
   ```

### Step 4: Run Pipeline

**Option A: Click Green Run Button**
- Open `main.py`
- Click green ▶ button (top right)
- Pipeline executes with output in console

**Option B: Run → Run 'main.py'**
- From menu bar
- Or press Shift+F10

**Option C: Terminal**
```bash
cd /path/to/project
python main.py
```

---

## 📊 Expected Execution Flow

```
┌─────────────────────────────────────────────────┐
│        STARTING ANALYSIS PIPELINE               │
├─────────────────────────────────────────────────┤
│ ✓ Step 1: Loading raw data (48,895 rows)       │ ~1 sec
├─────────────────────────────────────────────────┤
│ ✓ Step 2: Cleaning data (39,729 final rows)    │ ~1 sec
├─────────────────────────────────────────────────┤
│ ✓ Step 3: Exploratory analysis                 │ ~1 sec
├─────────────────────────────────────────────────┤
│ ✓ Step 4: Creating 17 visualizations           │ ~10 sec
├─────────────────────────────────────────────────┤
│ ✓ Step 5: Generating reports                   │ ~1 sec
├─────────────────────────────────────────────────┤
│ COMPLETED SUCCESSFULLY in ~15 seconds          │
└─────────────────────────────────────────────────┘
```

**Console Output Summary:**
```
================================================================================
ANALYSIS SUMMARY
================================================================================

📊 DATASET OVERVIEW
  Total Listings: 39,729
  Unique Hosts: 32,365
  Neighbourhoods: 219

💰 PRICING INSIGHTS
  Average Price: $119.03
  Median Price: $100.00

📅 AVAILABILITY & OCCUPANCY
  Average Available Days: 97
  Estimated Occupancy Rate: 73.4%

⭐ REVIEW METRICS
  Total Reviews: 1,047,821
  Listings with Reviews: 83.1%

📁 OUTPUT FILES
  Cleaned Data: data/airbnb_cleaned.csv
  Visualizations: output/plots/ (17 files)
  Reports: output/reports/ (2 files)
```

---

## 📁 Directory Structure

```
📦 airbnb-analysis/
│
├── 📄 main.py                       ← RUN THIS FILE
├── 📄 config.py                     ← Configuration (modify if needed)
├── 📄 requirements.txt              ← Dependencies
├── 📄 README.md                     ← Full documentation
│
├── 📂 data/
│   ├── Airbnb_data.csv             ← INPUT (6.8 MB)
│   └── airbnb_cleaned.csv          ← OUTPUT (generated)
│
├── 📂 output/
│   ├── 📂 plots/
│   │   ├── 01_price_distribution.png
│   │   ├── 02_price_by_room_type.png
│   │   ├── 03_price_by_neighbourhood_group.png
│   │   ├── ... (17 total PNG files)
│   │   └── 17_occupancy_by_price.png
│   │
│   └── 📂 reports/
│       ├── airbnb_analysis_report.md     ← KEY REPORT
│       └── airbnb_analysis_data.json
│
├── 📂 logs/
│   └── analysis.log
│
└── 📂 [Module Files]
    ├── data_loader.py
    ├── data_cleaner.py
    ├── exploratory_analyzer.py
    ├── visualizer.py
    ├── report_generator.py
    └── logger_config.py
```

---

## 🔍 Key Output Files Explained

### 1. **airbnb_analysis_report.md** (View in any editor)
- Executive summary with all key metrics
- Detailed analysis of prices, locations, reviews
- Business insights and recommendations
- **👉 Start here after execution**

### 2. **output/plots/** (17 Professional Charts)

| # | Chart | What It Shows | Business Insight |
|---|-------|--------------|-----------------|
| 1 | Price Distribution | Spread of pricing | Most listings $80-150 |
| 2 | Price by Room Type | Comparison across room types | Entire homes 2.7x more expensive |
| 3 | Price by Borough | Manhattan vs Brooklyn vs others | Location is #1 price driver |
| 4 | Expensive Neighborhoods | Top 15 premium areas | East Harlem, West Village lead |
| 5 | Room Type Pie Charts | Market composition | 50% private, 47.5% entire, 2.5% shared |
| 6 | Top Neighborhoods | Most popular areas | East Harlem, Williamsburg, Park Slope |
| 7 | Geographic Heatmap | Location visualization | Clear clustering in Manhattan |
| 8 | Availability Distribution | 365-day availability pattern | 73.4% avg occupancy rate |
| 9 | Occupancy by Room Type | Which types rent more | Entire homes highest occupancy |
| 10 | Review Distribution | Number of reviews per listing | 83% have reviews (healthy market) |
| 11 | Reviews per Month | Activity frequency | 1.48 avg reviews/month |
| 12 | Top Hosts | Most prolific hosts | 32K hosts, avg 3.1 listings |
| 13 | Host Experience | Host segmentation | 78% single-host, 22% operators |
| 14 | Correlation Heatmap | Feature relationships | 5 strong correlations found |
| 15 | Price vs Reviews | Relationship analysis | Premium listings get more reviews |
| 16 | Min Nights Distribution | Stay length requirements | 71% require 1-5 night minimum |
| 17 | Occupancy vs Price | Revenue optimization | $100-150 sweet spot |

### 3. **airbnb_cleaned.csv** (Analysis-ready data)
- 39,729 rows (cleaned from 48,895)
- 20 columns including engineered features
- Ready for further analysis or modeling
- Open with Excel, pandas, or any CSV reader

### 4. **analysis.log** (Execution tracking)
- Timestamp for each operation
- Data at each step
- Errors (if any) with traceback
- Useful for debugging

---

## 💻 PyCharm Pro Tips

### View Execution Output

**Run → View → Show Execution Point** (or Alt+F10)

### Debug Mode

```python
# In main.py, add breakpoint:
pipeline = AnalysisPipeline()
breakpoint()  # ← Click here to pause
success = pipeline.run()
```

### View Generated Plots

```python
# Right-click on plots/ folder in Project Explorer
# Select "Show in Explorer"
# Opens file browser to view PNG files
```

### Modify Parameters

Edit `config.py` to customize:

```python
# Line 43: Price outlier threshold
PRICE_OUTLIER_IQR_MULTIPLIER = 1.5  # Change to 2.0 for stricter

# Line 51: Top N items to display
TOP_N = 10  # Change to 20 for more

# Line 67: Figure dimensions
FIGURE_WIDTH = 14  # Change for smaller/larger charts

# Line 108: Significance level
SIGNIFICANCE_LEVEL = 0.05  # Change for different threshold
```

### Run Individual Modules

```python
# Test just the loader
from data_loader import DataLoader
loader = DataLoader()
data = loader.load()
print(loader.get_data_info())

# Test just the cleaner
from data_cleaner import DataCleaner
cleaner = DataCleaner(data)
cleaned = cleaner.clean()

# Test just analysis
from exploratory_analyzer import ExploratoryAnalyzer
analyzer = ExploratoryAnalyzer(cleaned)
results = analyzer.analyze()
```

---

## 🐛 Debugging Tips

### If data doesn't load:
```python
# In main.py, add after line 25:
import os
print("Current working directory:", os.getcwd())
print("Data file exists:", os.path.exists("data/Airbnb_data.csv"))
print("Files in data/:", os.listdir("data/"))
```

### If visualizations fail:
```python
# Check matplotlib backend
import matplotlib
print("Matplotlib backend:", matplotlib.get_backend())

# If needed, use non-interactive backend
import matplotlib
matplotlib.use('Agg')
```

### If memory issues:
```python
# Monitor memory usage
import psutil
import os
process = psutil.Process(os.getpid())
print("Memory usage:", process.memory_info().rss / 1024 ** 2, "MB")
```

---

## 📈 Sample Analysis Workflow

### After first run:

1. **Review Console Output**
   - Check dataset summary
   - Verify counts match expectations

2. **Open Report**
   - Double-click `output/reports/airbnb_analysis_report.md`
   - Read executive summary first
   - Then detailed sections

3. **View Charts**
   - Open `output/plots/` folder
   - Start with #1 (price distribution)
   - Progress through to #17

4. **Examine Data**
   - Open `data/airbnb_cleaned.csv` in Excel
   - Verify data quality
   - Check new engineered features

5. **Deep Dive (Optional)**
   - Modify `config.py` parameters
   - Re-run `python main.py`
   - Compare outputs

---

## 🔄 Rerunning Analysis

### Simple Re-run
```bash
python main.py
# Overwrites all output files with new results
```

### Compare Different Parameters

1. Edit `config.py`:
   ```python
   # Before: PRICE_OUTLIER_IQR_MULTIPLIER = 1.5
   # After: PRICE_OUTLIER_IQR_MULTIPLIER = 2.0
   ```

2. Run pipeline:
   ```bash
   python main.py
   ```

3. Compare `data/airbnb_cleaned.csv` (different row count if outlier threshold changed)

4. Review `logs/analysis.log` to see impact:
   ```
   "Removed 2972 price outliers"  # vs different count with new setting
   ```

---

## ✅ Verification Checklist

After successful execution, verify:

- [ ] Console shows "PIPELINE EXECUTION COMPLETED SUCCESSFULLY"
- [ ] `data/airbnb_cleaned.csv` exists (should be ~5 MB)
- [ ] `output/plots/` contains 17 PNG files
- [ ] `output/reports/` contains:
  - [ ] `airbnb_analysis_report.md` (~5 KB)
  - [ ] `airbnb_analysis_data.json` (~23 KB)
- [ ] `logs/analysis.log` has entries for each step
- [ ] Can open and view at least 3 PNG files
- [ ] Markdown report readable in browser or editor

---

## 🚨 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "ModuleNotFoundError: No module named 'pandas'" | `pip install -r requirements.txt` |
| "FileNotFoundError: data/Airbnb_data.csv" | Verify CSV file location and path in config.py |
| "PermissionError: output/plots/" | `chmod 755 output/plots` (Linux/Mac) or check folder permissions (Windows) |
| "Memory error" | Close other applications, ensure 2GB+ free RAM |
| "Plots not displaying" | Normal for server/CLI environment. Check PNG files exist. |
| "Report has no content" | Verify exploratory_analyzer.py completed successfully |

---

## 📞 Getting Help

### Check Logs First
```bash
# View last 50 lines of log
tail -50 logs/analysis.log

# Find errors
grep "ERROR" logs/analysis.log
grep "WARNING" logs/analysis.log
```

### Review Code Comments
All modules have:
- Module docstrings explaining purpose
- Class docstrings explaining responsibility  
- Method docstrings with parameters & returns
- Inline comments for complex logic

### Validate Your Environment
```python
# Run this in Python console to verify setup:
import pandas as pd
import numpy as np
import scipy
import matplotlib
import seaborn

versions = {
    'pandas': pd.__version__,
    'numpy': np.__version__,
    'scipy': scipy.__version__,
    'matplotlib': matplotlib.__version__,
    'seaborn': seaborn.__version__,
}

print("Installed Versions:")
for lib, version in versions.items():
    print(f"  {lib}: {version}")
```

---

## 🎓 Learning Resources

### Understanding the Code

1. **Start with `main.py`** - Shows overall flow
2. **Read `config.py`** - Understand all parameters
3. **Study individual modules** - Each has clear responsibility
4. **Review `data_cleaner.py`** - Most complex, best learning
5. **Examine visualizations** - See practical matplotlib usage

### Data Science Concepts

The project demonstrates:
- **Exploratory Data Analysis** (EDA)
- **Statistical analysis** (mean, median, correlation)
- **Data cleaning** (imputation, outlier detection)
- **Feature engineering** (creating new columns)
- **Data visualization** (multiple chart types)

### Python Concepts

The project uses:
- **Object-Oriented Programming** (classes, inheritance)
- **Functional Programming** (lambda functions, comprehensions)
- **Error Handling** (try-except, logging)
- **Configuration Management** (config files)
- **Module Organization** (clean imports, dependencies)

---

**Ready to run? Press Shift+F10 in PyCharm or `python main.py` in terminal!**

Generated: May 25, 2026 | Status: ✅ Production Ready
