# 📊 Kaggle Automated Analytics Pipeline

> **Production-grade, end-to-end Python data analytics pipeline that accepts any Kaggle dataset URL and automatically downloads, validates, preprocesses, visualises, and generates business insights + a full HTML report.**

---

## 🗂️ Project Structure

```
kaggle_analytics_pipeline/
│
├── data/                          # Downloaded & cleaned datasets
├── reports/                       # HTML, TXT, JSON analytical reports
├── visualizations/
│   ├── before/                    # Pre-processing charts
│   └── after/                     # Post-processing charts
├── logs/                          # Pipeline run logs
│
├── config/
│   ├── __init__.py
│   └── settings.py                # All configuration constants
│
├── src/
│   ├── __init__.py
│   ├── main.py                    # ← Pipeline entry point (run this)
│   │
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── kaggle_downloader.py   # Kaggle API download + extraction
│   │   ├── data_loader.py         # Multi-format loader (CSV/XLSX/JSON/Parquet)
│   │   └── domain_classifier.py   # Auto domain detection
│   │
│   ├── validation/
│   │   ├── __init__.py
│   │   ├── file_validator.py      # File integrity checks
│   │   └── data_quality.py        # Full DQ assessment (nulls, dups, outliers …)
│   │
│   ├── preprocessing/
│   │   ├── __init__.py
│   │   └── data_processor.py      # Imputation, encoding, scaling, feature eng.
│   │
│   ├── visualization/
│   │   ├── __init__.py
│   │   └── plot_engine.py         # 9+ chart types, before & after processing
│   │
│   ├── insights/
│   │   ├── __init__.py
│   │   ├── insight_generator.py   # Trends, risks, correlations, recommendations
│   │   └── report_generator.py    # HTML + TXT + JSON report writer
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logger.py              # Colored console + file logger
│       └── console.py             # Rich terminal formatting helpers
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## ⚙️ Setup Instructions

### 1. Clone / Download the Project

```bash
git clone <your-repo-url>
cd kaggle_analytics_pipeline
```

### 2. Create a Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Kaggle API Credentials

You need a free Kaggle account and an API key:

1. Log in at [kaggle.com](https://www.kaggle.com) → **Account** → **Create New API Token**
2. A `kaggle.json` file will be downloaded containing:
   ```json
   {"username": "your_username", "key": "your_api_key"}
   ```
3. Place it at:
   - **Windows**: `C:\Users\<YourName>\.kaggle\kaggle.json`
   - **macOS/Linux**: `~/.kaggle/kaggle.json`
   - Or set environment variables: `KAGGLE_USERNAME` and `KAGGLE_KEY`

---

## 🚀 Running the Pipeline

### Option A — CLI with URL argument (recommended)

```bash
python -m src.main --url "https://www.kaggle.com/datasets/uciml/iris"
```

### Option B — Interactive prompt

```bash
python -m src.main
# You will be prompted to enter the Kaggle URL
```

### Option C — Run directly in PyCharm

1. Open `src/main.py`
2. Right-click → **Run 'main'**
3. Enter the Kaggle URL when prompted (or edit `main()` to hardcode it for testing)

---

## 📋 Example Datasets to Try

| Domain       | Kaggle URL |
|--------------|------------|
| Healthcare   | `https://www.kaggle.com/datasets/uciml/pima-indians-diabetes-database` |
| Finance      | `https://www.kaggle.com/datasets/anandaramg/global-stock-market-indices-data` |
| E-commerce   | `https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce` |
| Education    | `https://www.kaggle.com/datasets/whenamancodes/students-performance-in-exams` |
| Entertainment| `https://www.kaggle.com/datasets/shivamb/netflix-shows` |
| General      | `https://www.kaggle.com/datasets/uciml/iris` |

---

## 📦 Pipeline Stages

| Step | Stage | Description |
|------|-------|-------------|
| 1 | **Download** | Kaggle API → zip extraction |
| 2 | **File Validation** | Existence, format, encoding, headers |
| 3 | **Data Loading** | CSV / XLSX / JSON / Parquet with chunking |
| 4 | **Domain Classification** | Keyword-frequency scoring across 10 domains |
| 5 | **Quality Assessment** | Nulls, duplicates, outliers, correlations |
| 6 | **Visualisations (Before)** | 8+ chart types on raw data |
| 7 | **Preprocessing** | Impute → encode → scale → feature engineering |
| 8 | **Visualisations (After)** | Charts on cleaned dataset |
| 9 | **Insight Generation** | Trends, risks, patterns, recommendations |
| 10 | **Report** | HTML + TXT + JSON saved to `reports/` |

---

## 📤 Outputs

After a successful run you will find:

```
data/
└── cleaned_dataset.csv           ← Preprocessed data

visualizations/
├── before/                        ← Raw data charts
│   ├── missing_heatmap_before.png
│   ├── correlation_matrix_before.png
│   ├── histograms_before.png
│   ├── boxplots_before.png
│   ├── countplots_before.png
│   ├── scatter_plots_before.png
│   ├── distribution_overview_before.png
│   └── class_imbalance_before.png
└── after/                         ← Cleaned data charts
    ├── histograms_after.png
    ├── boxplots_after.png
    ├── scatter_plots_after.png
    └── feature_importance_proxy_after.png

reports/
├── analytics_report_<timestamp>.html   ← Full interactive report
├── analytics_report_<timestamp>.txt    ← Plain text summary
└── analytics_report_<timestamp>.json   ← Machine-readable output

logs/
└── pipeline_<timestamp>.log
```

---

## 🧰 Supported File Formats

| Format   | Extension(s)          |
|----------|-----------------------|
| CSV      | `.csv`                |
| Excel    | `.xlsx`, `.xls`       |
| JSON     | `.json`               |
| Parquet  | `.parquet`            |

---

## 🏗️ Architecture Highlights

- **Modular design** — each stage is an independent class, easily extended
- **No hardcoded column names** — fully dynamic inference
- **Memory-efficient** — chunked loading, early GC, configurable row caps
- **Domain-aware insights** — 10 business domains with tailored risk flags
- **Scalable** — plug-in ML stage after preprocessing with no structural changes
- **PEP8 compliant** — type hints throughout, full docstrings

---

## 🛠️ Configuration

All tunable parameters live in `config/settings.py`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `MISSING_VALUE_THRESHOLD` | `0.40` | Drop columns with >40% nulls |
| `OUTLIER_IQR_FACTOR` | `1.5` | IQR multiplier for outlier detection |
| `CORRELATION_THRESHOLD` | `0.85` | Flag pairs above this Pearson r |
| `CHUNK_SIZE` | `100,000` | Rows per chunk for large CSV files |
| `MAX_ROWS_IN_MEMORY` | `1,000,000` | Truncation limit |
| `MAX_CATEGORIES_PLOT` | `15` | Max bars in count plots |
| `FIG_DPI` | `150` | Chart export resolution |

---

## 📄 License

MIT — free for personal and commercial use.
