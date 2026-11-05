# app.py
import pandas as pd
import streamlit as st
import logging 
from io import BytesIO

from core.transformations import PortfolioTransformer
from business.playbooks import LoanCollectionsReportEngine
from app.visualizer import ExposureChartFactory
from reports.pdf_factory import DocumentAuditFactory

# --- Clean Presentation Layer Structural Framework CSS ---
st.markdown(""" 
 <style> 
 header[data-testid="stHeader"] { visibility: hidden !important; display: none !important; } 
 div[data-testid="stToolbar"] { visibility: hidden !important; display: none !important; } 
 footer { visibility: hidden !important; } 
 [data-testid="stMainBlockContainer"] { padding-top: 1rem !important; }
 .main .block-container { padding-top: 1rem !important; }
 </style> 
 """, unsafe_allow_html=True) 

logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger("CREDITPULSE") 

st.set_page_config(page_title="CreditPulse AI Workstation", layout="wide", initial_sidebar_state="expanded")
st.title("📈 CREDITPULSE AI — MULTI-PRODUCT RETAIL LEDGER WORKSTATION")
st.divider()

# ==============================================================================
# DATA INJECTION PANEL
# ==============================================================================
st.sidebar.title("Ledger Workspace Controls")
st.sidebar.markdown("### 📂 Step 1: Data Injection")
uploaded_file = st.sidebar.file_uploader("Upload Portfolio Ledger CSV File", type=["csv"])

if uploaded_file is None:
    st.info("💡 **Welcome to CreditPulse AI!** To begin, please upload your portfolio ledger CSV file using the sidebar.")
    st.stop()

@st.cache_data
def parse_uploaded_ledger(file_buffer):
    try: 
        raw_df = pd.read_csv(file_buffer)
        return PortfolioTransformer.process_raw_ledger(raw_df)
    except Exception as e:
        st.error(f"❌ Structural Read/Transformation Error: {e}")
        return None

portfolio_df = parse_uploaded_ledger(uploaded_file)
if portfolio_df is None or portfolio_df.empty: 
    st.stop()

# ==============================================================================
# FILTER PIPELINE
# ==============================================================================
st.sidebar.markdown("### 🎯 Step 2: Workspace Filtering")
product_options = ["[ SHOW ALL PRODUCTS ]", "PERSONAL_LOAN", "CREDIT_CARD", "VEHICLE_LOAN", "HOME_LOAN", "GOLD_LOAN", "LAP"]
product_dropdown = st.sidebar.selectbox("Product Category:", product_options, index=0)
omni_search_box = st.sidebar.text_input("Omni Search Filter:", placeholder="Type name, UCIC ID...").strip()

if product_dropdown == "[ SHOW ALL PRODUCTS ]":
    base_df = portfolio_df.copy()
else:
    base_df = portfolio_df[portfolio_df["LAN_PDT"].astype(str) == str(product_dropdown)]

if omni_search_box:
    q = omni_search_box.upper()
    base_df = base_df[
        base_df["UCIC"].astype(str).str.upper().str.contains(q, na=False) |
        base_df["LOAN_NO"].astype(str).str.upper().str.contains(q, na=False) |
        base_df["CUSTOMERNAME"].astype(str).str.upper().str.contains(q, na=False)
    ]

# Master Data Export Downloader
if not portfolio_df.empty:
    st.sidebar.markdown("##### 🗃️ Master Compliance Ledger Export")
    csv_buffer = BytesIO()
    portfolio_df.to_csv(csv_buffer, index=False, encoding='utf-8')
    st.sidebar.download_button(
        label="📥 Download Expanded 108-Header CSV",
        data=csv_buffer.getvalue(),
        file_name="Expanded_Master_Ledger_108_Headers.csv",
        mime="text/csv",
        use_container_width=True
    )

# ==============================================================================
# DIAGNOSTICS CONTROL PANEL
# ==============================================================================
st.sidebar.markdown("---")
st.sidebar.markdown("### 🛠️ Step 3: System Verification")
run_diagnostics = st.sidebar.checkbox("Run System Diagnostics", value=False)

if run_diagnostics:
    st.sidebar.info("⏳ Running engine validations...")
    try:
        import pytest
        exit_code = pytest.main(["-q", "--tb=short", "tests/test_calculations.py"])
        if exit_code == 0:
            st.sidebar.success("✅ ALL TESTS PASSED!")
            st.toast("System Integrity Verified: 100% Stable", icon="✅")
        else:
            st.sidebar.error("❌ CRITICAL BUG DETECTED!")
    except Exception as e:
        st.sidebar.error(f"Execution Error: {e}")

# ==============================================================================
# PRESENTATION PANEL GRID
# ==============================================================================
counts = PortfolioTransformer.compute_bucket_counts(base_df)
kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6 = st.columns(6)
kpi_col1.metric("📊 TOTAL FILTERED", int(len(base_df)))
kpi_col2.metric("🟢 BUCKET 0", int(counts['b0']))
kpi_col3.metric("🟡 BUCKET 1", int(counts['b1']))
kpi_col4.metric("🟠 BUCKET 2", int(counts['b2']))
kpi_col5.metric("🔴 BUCKET 3", int(counts['b3']))
kpi_col6.metric("☠️ BUCKET 4", int(counts['b4']))

st.info(f"**Workspace Ledger State:** Filter Mode: {product_dropdown}")

cols = ["UCIC", "LAN_PDT", "MODULE", "LOAN_NO", "CUSTOMERNAME", "LOAN_EMI", "LAN_INST_OV_AMT", "LAN_DPD", "BRANCH_DESC", "SOLID"]
available_cols = [c for c in cols if c in base_df.columns]
st.subheader("📋 Workspace Active Data Ledger Rows")
st.dataframe(base_df[available_cols], use_container_width=True, hide_index=True)

# ==============================================================================
# SPLIT DUAL SCREEN PRESENTATION CORE
# ==============================================================================
left_panel, right_panel = st.columns(2)

with left_panel:
    st.markdown("### 🔍 108-Header Cross-Product Audit Inspector")
    
    if base_df.empty:
        st.info("📂 Workspace is empty.")
    else:
        available_ucics = sorted(base_df["UCIC"].dropna().unique().tolist())
        target_id = st.selectbox("Select Active Customer UCIC Key to Inspect:", options=available_ucics)

        if target_id:
            record = base_df[base_df["UCIC"] == target_id]
            
            if not record.empty:
                row_slice = record.iloc[0].to_dict()
                
                # Dynamic calculated fields generation
                b_code, b_class, b_playbook = LoanCollectionsReportEngine.generate_audit_bucket_metadata(row_slice)
                row_slice["RESPONSE_CODE_NEW"] = LoanCollectionsReportEngine.extract_field_action_code(row_slice)
                
                st.subheader(f"🛡️ Audit Inspector Panel: {target_id}")
                col_b1, col_b2 = st.columns(2)
                col_b1.metric("Regulatory Bucket Code", b_code)
                col_b2.metric("Portfolio Risk Tier", b_class)

                st.text_area(label="Official Mandated Strategy Directive:", value=b_playbook, height=80, disabled=True)
                st.markdown("---")

                st.markdown("##### 🏷️ Sourcing & Parameters")
                st.write(f"**Customer Name:** {row_slice.get('CUSTOMERNAME', '')} | **Loan No:** {row_slice.get('LOAN_NO', '')}")
                st.write(f"**Branch Name:** {row_slice.get('BRANCH_DESC', 'NONE')} | **Sol ID Code:** {row_slice.get('SOLID', 'NONE')}")
                st.error(f"**Days Past Due (LAN_DPD):** {row_slice.get('LAN_DPD', 0)} Days")
                
                try:
                    st.write(f"**Principal Balance (LAN_POS):** ₹{int(float(row_slice.get('LAN_POS', 0))):,}")
                    st.write(f"**Total Overdue Balance:** ₹{int(float(row_slice.get('LAN_INST_OV_AMT', 0))):,}")
                except Exception:
                    st.write(f"**Principal Balance:** ₹{row_slice.get('LAN_POS', 0)}")

                st.markdown("---")
                pdf_payload = DocumentAuditFactory.generate_audit_pdf(target_id, row_slice, b_playbook)
                st.download_button(
                    label="Download Executive PDF Audit Report",
                    data=pdf_payload,
                    file_name=f"Audit_Report_{target_id}.pdf",
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )

with right_panel:
    st.markdown("### 📊 Reconciled Capital Exposure Share Frame")
    if base_df.empty: 
        st.info("⚠️ No data available to plot chart analysis.")
    else: 
        st.plotly_chart(ExposureChartFactory.generate_exposure_chart(base_df, product_dropdown), use_container_width=True)

# Footer Copyright injection
st.markdown("""<br><hr><center><small>© 2026 T A Srinivas. All Rights Reserved. Prototype for Portfolio Display.</small></center>""", unsafe_allow_html=True)
