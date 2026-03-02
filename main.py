import os
import time
import shutil
from datetime import datetime, timedelta
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from ocr_extraction import process_invoice
from pdf_extraction import process_pdf_invoice
from utils import save_db, load_db
from email_service import send_summary_email


# DIRECTORY CONFIG
INCOMING_DIR = "invoices/incoming"
PROCESSED_DIR = "invoices/processed"
FAILED_DIR = "invoices/failed"

os.makedirs(INCOMING_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(FAILED_DIR, exist_ok=True)


# EMAIL BATCH CONFIG
EMAIL_INTERVAL = timedelta(minutes=15)
pending_invoices = []
last_email_time = datetime.now()


# FILE HANDLER
class InvoiceHandler(FileSystemEventHandler):

    def handle_file(self, path):
        global pending_invoices

        try:
            print(f"Processing: {os.path.basename(path)}")

            if path.lower().endswith(".pdf"):
                invoice = process_pdf_invoice(path)
            else:
                invoice = process_invoice(path)

            if invoice:
                db = load_db()
                db["invoices"].append(invoice)
                save_db(db)

                # Add to email batch
                pending_invoices.append(invoice)

                print(f"Invoice {invoice['invoice_no']} added to batch.")

            shutil.move(path, os.path.join(PROCESSED_DIR, os.path.basename(path)))
            print("Moved to processed folder.\n")

        except Exception as e:
            print("Processing Failed:", e)
            shutil.move(path, os.path.join(FAILED_DIR, os.path.basename(path)))


    def on_created(self, event):
        if not event.is_directory:
            time.sleep(1)  
            self.handle_file(event.src_path)


# PROCESS EXISTING FILES
def process_existing_files(handler):
    for file in os.listdir(INCOMING_DIR):
        path = os.path.join(INCOMING_DIR, file)
        if os.path.isfile(path):
            handler.handle_file(path)


# MAIN
if __name__ == "__main__":

    handler = InvoiceHandler()

    # Process already existing files
    process_existing_files(handler)

    # Start observer
    observer = Observer()
    observer.schedule(handler, INCOMING_DIR, recursive=False)
    observer.start()

    print(" Invoice automation running...")
    print(" Summary emails will be sent every 15 minutes.\n")

    try:

        while True:
            time.sleep(5)

            current_time = datetime.now()

            if current_time - last_email_time >= EMAIL_INTERVAL:

                if pending_invoices:
                    print("Sending summary email...")
                    send_summary_email(pending_invoices)
                    pending_invoices.clear()
                else:
                    print("No new invoices in this period.")

                last_email_time = current_time

    except KeyboardInterrupt:
        print("\nStopping automation...")
        observer.stop()

    observer.join()