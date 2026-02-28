import streamlit as st
import time
from report_service import ReportService
import pandas as pd

st.set_page_config(
    page_title="Invoice Dashboard",
    layout="wide"
)

service = ReportService()

# -------------------------
# LOAD DATA & METRICS
# -------------------------
total_revenue = service.total_revenue()
total_invoices = service.total_invoices()
average_invoice = service.average_invoice_value()

# -------------------------
# KPI CARDS (TOP ROW)
# -------------------------
st.markdown("##  Key Metrics")
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric(" Total Revenue", f"${total_revenue:,.2f}")
kpi2.metric("Total Invoices", total_invoices)
kpi3.metric(" Average Invoice Value", f"${average_invoice:,.2f}")

st.markdown("---")

# -------------------------
# HORIZONTAL CHART ROW 1
# -------------------------
st.markdown("###  Revenue & Vendors Overview")
col1, col2, col3 = st.columns(3)

# Revenue by Category
with col1:
    st.subheader("Revenue by Category")
    category_data = service.revenue_by_category(min_revenue=50)
    category_df = pd.DataFrame(category_data.items(), columns=["Category", "Revenue"])
    category_df = category_df.sort_values("Revenue", ascending=True)
    st.bar_chart(category_df.set_index("Category"))

# Top Vendors by Revenue
with col2:
    st.subheader("Top Vendors")
    vendor_data = service.revenue_by_vendor(top_n=5)
    vendor_df = pd.DataFrame(vendor_data.items(), columns=["Vendor", "Revenue"])
    vendor_df = vendor_df.sort_values("Revenue", ascending=True)
    st.bar_chart(vendor_df.set_index("Vendor"))

# Yearly Invoices
with col3:
    st.subheader("Invoices by Year")
    year_data = service.invoices_by_year()
    year_df = pd.DataFrame(year_data.items(), columns=["Year", "Invoice Count"])
    year_df = year_df.sort_values("Year")
    st.line_chart(year_df.set_index("Year"))

# -------------------------
# HORIZONTAL CHART ROW 2
# -------------------------
st.markdown("###  Trends & Top Invoices")
col4, col5 = st.columns([2, 1])  # wider left for trends

# Monthly Revenue Trends
with col4:
    st.subheader("Monthly Revenue Trends")
    years_available = sorted([int(y) for y in year_data.keys()])
    selected_year = st.selectbox("Select Year", options=years_available, index=len(years_available)-1, key="monthly_year")
    monthly_data = service.monthly_revenue(year=selected_year)
    monthly_df = pd.DataFrame(monthly_data.items(), columns=["Month", "Revenue"])
    monthly_df = monthly_df.sort_values("Month")
    st.line_chart(monthly_df.set_index("Month"))

# Top 5 Expensive Invoices
with col5:
    st.subheader("Top 5 Expensive Invoices")
    top_invoices = service.top_expensive_invoices(top_n=5)
    for inv in top_invoices:
        st.info(f"Invoice: **{inv['invoice_no']}**\nVendor: **{inv['vendor']}**\nAmount: **${inv['total_amount']:,.2f}**")

# -------------------------
# AUTO REFRESH EVERY 5 SECONDS
# -------------------------
time.sleep(5)
st.rerun()