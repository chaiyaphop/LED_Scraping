# LED_Scraping: Scraping Legal Execution Department's Website Using Python

**LED_Scraping** is a Python script for extracting property data from the Legal Execution Department (LED) of Thailand’s website using Selenium.

## Features

* Supports scraping for condos and land/building assets
* Covers multiple provinces, including Bangkok, Samut Prakan, and Pathum Thani
* Saves results to Excel, grouped by civil code
* Headless Chrome browser support

---

## ✅ Prerequisites

* Google Chrome **v120.0.6099.130** (or compatible)
* Python **v3.11.3**
* ChromeDriver that matches your Chrome version (must be in PATH)

---

## ⚙️ Setup Instructions

<details>
<summary><strong>Option 1: Local Python (Manual)</strong></summary>

Install dependencies using:

```bash
source setup.sh
```

Or manually:

```bash
pip install -r requirements.txt
```

Make sure you have:

* Python **3.11**
* Google Chrome and matching **ChromeDriver** in your PATH

</details>

<details>
<summary><strong>Option 2: Docker (Recommended)</strong></summary>

Make sure Docker is installed on your system.

### 1. Build and run the Docker container manually:

```bash
docker buildx build --platform=linux/amd64 -t led_scraper .
docker run -it --rm -v "$(pwd)/output":/app/output --env-file .env --name running-led-scraper-app led_scraper
```

### 2. Or use `docker-compose`:

```bash
docker-compose up --build
```

</details>

---

## 📄 Using Environment Variables

You can skip manual input by creating a `.env` file in the project root:

```env
ASSET_TYPE_ID=002       # 002 = condo, 003 = land/house
PROVINCE=bkk            # bkk, spk, or pte
CIVILS=1,2,...      # Only required if province = bkk
```

---

## ▶️ How to Run

<details>
<summary><strong>Run via Python</strong></summary>

```bash
python led_scraping.py
```

Follow the prompts for asset type, province, and civil code.

</details>

<details>
<summary><strong>Run via Docker (automated input)</strong></summary>

Make sure `.env` file is prepared, then:

```bash
docker-compose up --build
```

</details>

---

## 📁 Output Example

```plaintext
output/
└── LED_SCRAPING_BKK_CONDO_20250719.xlsx
    ├── Sheet: CIVIL_1
    ├── Sheet: CIVIL_2
```

---

## 📦 Project Structure

```plaintext
├── .env
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── led_scraping.py
├── output/
├── README.md
├── requirements.txt
└── setup.sh
```

---

## 🧑‍💻 Author

Chaiyaphop Jamjumrat

*Last updated: July 19, 2025*