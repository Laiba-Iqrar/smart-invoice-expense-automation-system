#  Smart Invoice & Expense Automation System

An end-to-end automated invoice processing and expense reporting system that extracts invoice data (PDF & Image), categorizes expenses, stores structured records, sends email notifications, and generates real-time financial analytics via an interactive dashboard.

---

##  One-Line Pitch

An intelligent automation workflow that extracts invoice data, categorizes expenses, stores them in a structured database, sends email alerts, and provides real-time financial insights.

---

##  Project Overview

The Smart Invoice & Expense Automation System is built for:

- Small businesses  
- Startups  
- Freelancers  
- Finance teams  
- Accounting departments  

It eliminates manual invoice processing by automating:

- Invoice data extraction
- Expense categorization
- Data storage
- Report generation
- Email notifications
- Real-time dashboard analytics

---

##  Key Features

###  Invoice Upload (PDF & Image Support)

- Monitors `invoices/incoming/` directory
- Automatically detects file type:
  - Image → OCR Extraction
  - PDF → Text Extraction
- Processes invoices in real time

---

###  Intelligent Field Extraction

Automatically extracts:

- Invoice Number
- Vendor Name
- Invoice Date
- Total Amount
- Item Names
- Item Prices

Uses:

- Regex-based pattern matching
- Multi-format PDF detection
- Tesseract OCR for image invoices

---

### Rule-Based Expense Categorization

Each invoice item is categorized using keyword rules.

Categories include:

- Technology
- Fashion
- Home Essentials
- Books
- Uncategorized

Implemented inside `utils.py`.

---

### Duplicate Invoice Detection

- Generates MD5 hash for each file
- Prevents duplicate entries
- Ensures database integrity

---

###  Structured JSON Database

All invoices are stored in:
output/invoices_db.json

## Automatic Email Notifications

Sends  batch invoice summary in time intervals (per day or every 15 mins) :

-  Email summary is automatically sent  
- Contains invoice details and item breakdown  
- Supports multiple recipients  
- Uses secure SMTP authentication  

---

## Real-Time Analytics Dashboard (Streamlit)

Interactive dashboard includes:

-  Total Revenue  
-  Total Invoices  
-  Top Vendors  
-  Revenue by Category  
-  Revenue by Vendor  
-  Yearly Invoice Trends  
-  Monthly Revenue Trends  
-  Top 5 Expensive Invoices  

---

## How It Works

### Step 1: Drop Invoice

Upload invoice that goes in invoices/incoming/


---

### Step 2: Automatic Processing

`main.py` detects new file using Watchdog.

---

### Step 3: Extraction

- Images → OCR via Tesseract  
- PDFs → Parsed via pdfplumber  

---

### Step 4: Data Structuring

Invoice converted to standardized JSON format.

---

### Step 5: Save to Database

Appends invoice to `invoices_db.json`.
```    {
      "invoice_id": "2ea02feb-e674-410b-a409-25f6692af48b",
      "invoice_no": "53695084",
      "vendor": "Diaz, Warren and Carter Black, Smith and Bass",
      "date": "10/25/2015",
      "total_amount": 2012.51,
      "items": [
        {
          "name": "Dell Optiplex Desktop Computer each with Dual 19\" LCD Monitors Windows 10 Pro",
          "price": 824.73,
          "category": "technology"
        },
        {
          "name": "HP Windows 10 Pro Desktop each Computer Intel QUAD CORE i5 Wifi, Keyboard & Mouse",
          "price": 747.78,
          "category": "technology"
        },
        {
          "name": "3: STUDENT/WORK COMPUTER each WORKSTATION WINDOWS 10 PRO",
          "price": 440.0,
          "category": "technology"
        }
      ],
      "_hash": "42e90c539e423f348324bd8c13ef221d"
    }
```

---

### Step 6: Email Notification

Sends invoice summary email in batch  once in a day (can be changed as per users preference)
<img width="642" height="559" alt="image" src="https://github.com/user-attachments/assets/cf3e99a3-f3ee-48f0-9dbb-4d9ca031f922" />


---

### Step 7: Dashboard Update

Dashboard auto-refreshes and reflects updated data.

<img width="1918" height="729" alt="image" src="https://github.com/user-attachments/assets/9cb7df9a-faff-4f33-8a08-5d77544c1ab3" />
<img width="1918" height="596" alt="image" src="https://github.com/user-attachments/assets/5cc6095a-3020-4472-8861-99cad738d96c" />



---

##  Challenges Faced

During the development of this Smart Invoice & Expense Automation System, several real-world technical challenges were encountered and resolved:

---

###  Inconsistent PDF Text Extraction

- PDF layouts vary significantly across vendors.
- `pdfplumber` sometimes merges columns or rearranges text.
- Fields like **Invoice No** and **Vendor** appeared on the same line unexpectedly.
- Required robust regex patterns and multi-format parsing logic.
- Date format was different among different formats.
- invoice with multiple items needed quantity based pattern matching
- 

✅ Solution:  
Implemented format detection logic and adaptive regex-based extraction.

---

### 2️⃣ Multi-Format Invoice Handling

- Different invoice templates had completely different structures.
- Some PDFs placed labels and values on separate lines.
- OCR-based images had noisy or inconsistent text.

 Solution:  
Created separate parsers (`parse_format_1`, `parse_format_2`) with intelligent format detection.

---

### OCR Noise & Text Imperfections

- Image invoices extracted via Tesseract sometimes contained:
  - Extra spaces
  - Broken words
  - Misaligned fields

 Solution:  
Applied pattern matching with fallback logic and keyword-based detection to improve reliability.

---

###  Email Authentication Issues

- Gmail blocks normal password authentication.
- Encountered SMTP authentication errors (Error 535).

 Solution:  
Configured Gmail App Passwords and implemented secure environment-variable-based credential handling.

---

###  Import Path & Package Structure Issues

- Streamlit execution caused module import errors.
- Running dashboard from subdirectories broke relative imports.

 Solution:  
Restructured project into a proper package layout and corrected module import paths.

---

###  File Overwrite & Duplicate Handling

- Moving processed invoices caused overwrite errors.
- Same invoice uploaded multiple times created duplicate records.

 Solution:  
Implemented:
- Safe file renaming during move operations
- MD5 hash-based deduplication system

---

## ⚙ Installation & Setup

###  Clone Repository
```bash
git clone <your-repo-url>
cd smart-invoice-expense-automation-system

### Create Virtual Environment
python3 -m venv venv
source venv/bin/activate

### Install Dependencies
pip install -r requirements.txt

### Install Tesseract (For OCR Support)
sudo apt install tesseract-ocr

▶ Running the System
Terminal 1 — Start Automation Engine
python main.py
Terminal 2 — Start Dashboard
streamlit run reporting/dashboard.py

Open browser:
http://localhost:8501
