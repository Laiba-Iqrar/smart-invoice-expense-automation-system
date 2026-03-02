import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# =========================
# CONFIGURATION
# =========================
SMTP_SERVER = "smtp.gmail.com"  # Change if not Gmail
SMTP_PORT = 587

SENDER_EMAIL = "zia4500438@cloud.neduet.edu.pk"
SENDER_PASSWORD = ""  #  Replace

RECIPIENTS = [
    "laibaiqrarahmedkhan@gmail.com",
    "anooshakhalid999@gmail.com"
]


def send_summary_email(invoices):

    if not invoices:
        return  # Nothing to send

    total_amount = sum(inv["total_amount"] for inv in invoices)
    total_invoices = len(invoices)

    subject = f"Invoice Summary Report ({total_invoices} invoices)"

    body = f"""
Invoice Summary Report
==============================

Total Invoices: {total_invoices}
Total Revenue: ${total_amount:,.2f}

--------------------------------
Invoice Details:
--------------------------------
"""

    for inv in invoices:
        body += f"""
Invoice No: {inv['invoice_no']}
Vendor: {inv['vendor']}
Date: {inv['date']}
Total: ${inv['total_amount']:,.2f}
--------------------------------
"""

    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = ", ".join(RECIPIENTS)
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENTS, msg.as_string())
        server.quit()

        print("Summary email sent successfully.")

    except Exception as e:
        print("Failed to send summary email:", e)