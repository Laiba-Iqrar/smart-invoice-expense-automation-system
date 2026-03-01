import re
import uuid
import pdfplumber
from datetime import datetime
from utils import get_file_hash, already_processed, categorize

# TEXT EXTRACTION
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


# DATE FORMATTER
def format_date(date_str):
    for fmt in ("%b %d %Y", "%d %B %Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt).strftime("%m/%d/%Y")
        except:
            continue
    return "Unknown"


# FORMAT 1 PARSER
def parse_format_1(text):

    # Invoice Number (# 17042)
    invoice_no_match = re.search(r"#\s*(\d+)", text)

    # Vendor Extraction
    vendor = "Unknown"
    lines = text.split("\n")

    for i, line in enumerate(lines):
        if "Bill To:" in line:
            for j in range(i + 1, min(i + 6, len(lines))):
                candidate = lines[j].strip()

                if candidate and not any(
                    keyword in candidate for keyword in
                    ["Ship", "Date", "Mode", "Balance", "$"]
                ):
                    name_parts = candidate.split()
                    if len(name_parts) >= 2:
                        vendor = f"{name_parts[0]} {name_parts[1]}"
                    else:
                        vendor = name_parts[0]
                    break
            break

    # Date
    date_match = re.search(
        r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}\s+\d{4}",
        text
    )

    # Total
    total_match = re.search(
        r"Total:\s*\$?([\d,]+\.\d+)",
        text
    )

    # Items
    items = []

    item_block = re.search(
        r"Item Quantity Rate Amount\n(.*?)Subtotal:",
        text,
        re.DOTALL
    )

    if item_block:
        block_lines = item_block.group(1).strip().split("\n")

        for line in block_lines:
            match = re.search(
                r"(.+?)\s+\d+\s+\$([\d,]+\.\d+)",
                line
            )
            if match:
                name = match.group(1).strip()
                price = float(match.group(2).replace(",", ""))

                items.append({
                    "name": name,
                    "price": price,
                    "category": categorize(name)
                })

    return {
        "invoice_no": invoice_no_match.group(1) if invoice_no_match else "Unknown",
        "vendor": vendor,
        "date": format_date(date_match.group()) if date_match else "Unknown",
        "total_amount": float(total_match.group(1).replace(",", "")) if total_match else 0.0,
        "items": items
    }


# FORMAT 2 PARSER
def parse_format_2(text):

    # Extract Invoice No + Vendor (merged block case)
    merged_match = re.search(
        r"Invoice No:\s*Verndor:\s*\n\s*(\d+)\s+([A-Za-z ]+)",
        text,
        re.IGNORECASE
    )

    if merged_match:
        invoice_no = merged_match.group(1)
        vendor = merged_match.group(2).strip()
    else:
        # fallback patterns
        invoice_no_match = re.search(
            r"Invoice No:\s*\n?\s*(\d+)",
            text,
            re.IGNORECASE
        )
        vendor_match = re.search(
            r"Verndor:\s*\n?\s*([A-Za-z ]+)",
            text,
            re.IGNORECASE
        )

        invoice_no = invoice_no_match.group(1) if invoice_no_match else "Unknown"
        vendor = vendor_match.group(1).strip() if vendor_match else "Unknown"

    # Date
    date_match = re.search(
        r"\d{2}\s+[A-Za-z]+\s+\d{4}",
        text
    )

    # Total
    total_match = re.search(
        r"GRAND TOTAL\s*\$?\s*([\d,]+)",
        text,
        re.IGNORECASE
    )

    # Items
    items = []

    item_pattern = re.findall(
        r"\d+\s+([A-Za-z ]+?)\s+\d+\s+\$\s*([\d,]+)",
        text
    )

    for name, price in item_pattern:
        items.append({
            "name": name.strip(),
            "price": float(price.replace(",", "")),
            "category": categorize(name)
        })

    return {
        "invoice_no": invoice_no,
        "vendor": vendor,
        "date": format_date(date_match.group()) if date_match else "Unknown",
        "total_amount": float(total_match.group(1).replace(",", "")) if total_match else 0.0,
        "items": items
    }

# MAIN PROCESS FUNCTION
def process_pdf_invoice(file_path):

    text = extract_text_from_pdf(file_path)

    print("\n" + "="*60)
    print("Extracted PDF Text from:", file_path)
    print("="*60)
    print(text)
    print("="*60 + "\n")

    file_hash = get_file_hash(file_path)
    if already_processed(file_hash):
        print("Duplicate invoice detected. Skipping.")
        return None

    # Stronger format detection
    if "Invoice No:" in text and "Verndor:" in text:
        data = parse_format_2(text)
    elif "Bill To:" in text:
        data = parse_format_1(text)
    else:
        raise Exception("Unknown PDF format")

    invoice = {
        "invoice_id": str(uuid.uuid4()),
        "invoice_no": data["invoice_no"],
        "vendor": data["vendor"],
        "date": data["date"],
        "total_amount": data["total_amount"],
        "items": data["items"],
        "_hash": file_hash
    }

    return invoice