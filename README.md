# 📊 Smart Data Cleaner & Analyzer

A powerful, modular **data preprocessing engine** with a Streamlit UI that can clean, analyze, and transform messy datasets from multiple formats.

---

## 🚀 Features

### 📥 Multi-Format Data Ingestion

* Supports:

  * CSV
  * Excel (`.xlsx`, `.xls`)
  * JSON
  * TXT
  * DOCX (table extraction)

---

### 🧠 Smart Data Cleaning

* Automatic column type detection:

  * Numerical
  * Categorical
  * Boolean
* Intelligent type conversion
* Handles messy real-world data formats

---

### 🧹 Missing Value Handling

* Auto strategy:

  * Mean (normal data)
  * Median (skewed data)
  * Mode (categorical)
* Manual options:

  * Mean
  * Median

---

### 🔍 Pattern Detection & Transformation

Automatically detects and converts:

* 💰 Currency values

  ```
  $5K → 5000
  ```
* ⏱ Duration

  ```
  1h 30min → 90
  ```
* 📅 Year / Range

  ```
  (2010–2022) → start/end columns
  ```

---

### 🧼 Duplicate Handling

* Remove exact duplicates
* Remove duplicates based on selected columns
* Normalizes text before comparison

---

### 📊 Data Quality Analysis

* Dataset shape, duplicates, missing values
* Data Quality Score
* Column intelligence:

  * dtype
  * missing %
  * skew
  * uniqueness

---

### 🤖 Smart Suggestions Engine

* Detects:

  * High missing columns
  * ID-like columns
  * Low-value columns

---

### 📈 Visualization

* Histograms (numerical)
* Bar charts (categorical)

---

### ⚡ Outlier Handling

* Cap using IQR
* Remove using IQR

---

### 💾 Pipeline System

* Save cleaning configuration
* Reload and reuse later

---

### 🧱 Modular Architecture

* Clean separation:

  ```
  app/        → Streamlit UI
  pipeline/   → core logic
  ```

---

## 📂 Project Structure

```
data_cleaner/
│
├── app/
│   └── app.py
│
├── pipeline/
│   ├── loader.py
│   ├── preprocess.py
│   ├── transformers.py
│   ├── cleaner.py
│   ├── outliers.py
│   ├── utils.py
│
├── configs/
│   └── saved_pipeline.json
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

# 🛠️ Local Setup

## 1️⃣ Clone Repository

```
git clone https://github.com/HafsaAli2526/smart-data-cleaner.git
cd smart-data-cleaner
```

---

## 2️⃣ Create Virtual Environment

```
python -m venv .venv
```

Activate:

**Windows**

```
.venv\Scripts\activate
```

**Mac/Linux**

```
source .venv/bin/activate
```

---

## 3️⃣ Install Dependencies

```
pip install -r requirements.txt
```

---

## 4️⃣ Run Application

```
streamlit run app/app.py
```

Open in browser:

```
http://localhost:8501
```

---

# 🐳 Run with Docker

## 1️⃣ Build & Run

```
docker compose up --build
```

---

## 2️⃣ Open App

```
http://localhost:8501
```

---

## 🛑 Stop Container

```
docker compose down
```

---

# ⚙️ Docker Notes

* Uses `python:3.11-slim`
* Exposes port `8501`
* Mounts project directory for live updates

---

# 📦 Requirements

```
streamlit
pandas
numpy
matplotlib
seaborn
python-docx
openpyxl
```

---

# 💡 Use Cases

* Data preprocessing for ML
* Cleaning messy datasets
* Exploratory data analysis
* Data quality auditing

---

# 🚀 Future Improvements

* Fuzzy duplicate detection
* Feature engineering module
* ML model training integration
* API (FastAPI backend)
* SaaS deployment

---

# 👨‍💻 Author

Developed as a modular **data engineering project** focusing on real-world messy data handling.

---

# ⭐ Contribute

Feel free to fork, improve, and submit PRs!

---
