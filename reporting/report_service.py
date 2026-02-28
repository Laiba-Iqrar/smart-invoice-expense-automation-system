import json
import os
from collections import defaultdict
from utils import DB_PATH
from datetime import datetime

class ReportService:

    def __init__(self):
        self.db_path = DB_PATH

    def load_data(self):
        if not os.path.exists(self.db_path):
            return []
        with open(self.db_path, "r") as f:
            data = json.load(f)
        return data.get("invoices", [])

    # -------------------------
    # CORE METRICS
    # -------------------------
    def total_revenue(self):
        invoices = self.load_data()
        return sum(inv["total_amount"] for inv in invoices)

    def total_invoices(self):
        return len(self.load_data())

    def revenue_by_vendor(self, top_n=None):
        invoices = self.load_data()
        vendor_totals = defaultdict(float)
        for inv in invoices:
            vendor_totals[inv["vendor"]] += inv["total_amount"]

        # Sort descending by revenue
        sorted_vendors = dict(sorted(vendor_totals.items(), key=lambda x: x[1], reverse=True))
        if top_n:
            sorted_vendors = dict(list(sorted_vendors.items())[:top_n])
        return sorted_vendors

    def revenue_by_category(self, min_revenue=None):
        invoices = self.load_data()
        category_totals = defaultdict(float)
        for inv in invoices:
            for item in inv["items"]:
                category_totals[item["category"]] += item["price"]

        # Filter categories by min revenue if specified
        if min_revenue:
            category_totals = {k: v for k, v in category_totals.items() if v >= min_revenue}

        return dict(sorted(category_totals.items(), key=lambda x: x[1], reverse=True))

    def invoices_by_year(self):
        invoices = self.load_data()
        year_count = defaultdict(int)
        for inv in invoices:
            year = inv["date"].split("/")[-1]
            year_count[year] += 1
        return dict(sorted(year_count.items()))

    # -------------------------
    # NEW FINANCE REPORTS
    # -------------------------
    def average_invoice_value(self):
        invoices = self.load_data()
        if not invoices:
            return 0
        return sum(inv["total_amount"] for inv in invoices) / len(invoices)

    def top_expensive_invoices(self, top_n=5):
        invoices = self.load_data()
        sorted_invoices = sorted(invoices, key=lambda x: x["total_amount"], reverse=True)
        return sorted_invoices[:top_n]

    def monthly_revenue(self, year=None):
        invoices = self.load_data()
        monthly_totals = defaultdict(float)
        for inv in invoices:
            dt = datetime.strptime(inv["date"], "%m/%d/%Y")
            if year and dt.year != year:
                continue
            month_str = dt.strftime("%Y-%m")
            monthly_totals[month_str] += inv["total_amount"]

        return dict(sorted(monthly_totals.items()))

    def vendor_invoice_counts(self, min_invoices=1):
        invoices = self.load_data()
        vendor_counts = defaultdict(int)
        for inv in invoices:
            vendor_counts[inv["vendor"]] += 1

        # Filter by minimum invoice count
        vendor_counts = {v: c for v, c in vendor_counts.items() if c >= min_invoices}
        return dict(sorted(vendor_counts.items(), key=lambda x: x[1], reverse=True))

    def category_contribution_percentage(self):
        invoices = self.load_data()
        category_totals = defaultdict(float)
        total = 0
        for inv in invoices:
            for item in inv["items"]:
                category_totals[item["category"]] += item["price"]
                total += item["price"]
        percentages = {k: (v / total * 100) for k, v in category_totals.items()}
        return dict(sorted(percentages.items(), key=lambda x: x[1], reverse=True))