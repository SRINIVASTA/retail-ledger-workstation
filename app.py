# app.py [PART 1: Infrastructure Initialization & Global Filters]
import pandas as pd
import streamlit as st
import logging 
from io import BytesIO

# Enterprise Architecture Module Imports
from app.components import WorkstationUIComponents
from app.visualizer import ExposureChartFactory
from core.transformations import PortfolioTransformer
from business.playbooks import LoanCollectionsReportEngine
from reports.pdf_factory import DocumentAuditFactory

# Initialize Core Logging Infrastructure
logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger("CREDITPULSE_WORKSTATION") 

# Set Typed Corporate Page Configuration Limits
st.set_page_config(
    page_title="CreditPulse AI Workstation", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 1. Inject Corporate Theme Layout Controls & Performance CSS Overlays
WorkstationUIComponents.inject_corporate_branding_theme()

# 2. Render Main Screen Identity Banner Frame
WorkstationUIComponents.render_enterprise_summary_banner()

# ==============================================================================
# SIDEBAR CONTROL CENTER - STEP 1: DATA INJECTION
# ==============================================================================
st.sidebar.title("Ledger Workspace Controls")
st.sidebar.markdown("### 📂 Step 1: Data Injection")
uploaded_file = st.sidebar.file_uploader(
    "Upload Portfolio Ledger CSV File", 
    type=["csv"],
    help="Upload your credit portfolio file containing required operational ledger fields."
)

if uploaded_file is None:
    st.info("💡 **Welcome to CreditPulse AI!** To begin, please upload your portfolio ledger CSV file using the sidebar.")
    st.stop()

@st.cache_data(show_spinner="Processing systemic multi-product ledger matrices...")
def parse_uploaded_ledger(file_buffer):
    try: 
        raw_df = pd.read_csv(file_buffer)
        return PortfolioTransformer.process_raw_ledger(raw_df)
    except Exception as e:
        st.error(f"❌ Critical Structural Ingestion Exception: {e}")
        return None

portfolio_df = parse_uploaded_ledger(uploaded_file)
if portfolio_df is None or portfolio_df.empty: 
    st.stop()

# ==============================================================================
# SIDEBAR CONTROL CENTER - STEP 2: ANALYTICAL INTERACTIVE FILTER PIPELINE
# ==============================================================================
st.sidebar.markdown("### 🎯 Step 2: Workspace Filtering")
product_options = ["[ SHOW ALL PRODUCTS ]", "PERSONAL_LOAN", "CREDIT_CARD", "VEHICLE_LOAN", "HOME_LOAN", "GOLD_LOAN", "LAP"]
product_dropdown = st.sidebar.selectbox("Product Category:", product_options, index=0)
omni_search_box = st.sidebar.text_input(
    "Omni Search Filter:", 
    placeholder="Type name, UCIC ID, or loan number..."
).strip()

# Slice Core Dataframes Safely Using Vector Clones
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

# Master Compliance Output Downloader Engine Block
if not portfolio_df.empty:
    st.sidebar.markdown("##### 🗃️ Master Compliance Ledger Export")
    csv_buffer = BytesIO()
    portfolio_df.to_csv(csv_buffer, index=False, encoding='utf-8')
    st.sidebar.download_button(
        label="📥 Download Expanded 108-Header CSV",
        data=csv_buffer.getvalue(),
        file_name="Expanded_Master_Ledger_108_Headers.csv",
        mime="text/csv",
        use_container_width=True,
        help="Export the complete un-filtered 108-column schema spreadsheet containing all processed ledger records."
    )

# ==============================================================================
# SIDEBAR CONTROL CENTER - STEP 3: SYSTEMS STABILITY DIAGNOSTICS
# ==============================================================================
st.sidebar.markdown("---")
st.sidebar.markdown("### 🛠️ Step 3: System Verification")
run_diagnostics = st.sidebar.checkbox(
    "Run System Diagnostics", 
    value=False,
    help="Tick this checkbox to run automated PyTest checks directly inside this Streamlit container server."
)

if run_diagnostics:
    st.sidebar.info("⏳ Running engine validations...")
    try:
        import pytest
        # Execute unified core calculation unit validations
        exit_code = pytest.main(["-q", "--tb=short", "tests/test_calculations.py"])
        if exit_code == 0:
            st.sidebar.success("✅ ALL TESTS PASSED! Calculation engine validated.")
            st.toast("System Integrity Verified: 100% Stable", icon="✅")
        else:
            st.sidebar.error("❌ CRITICAL BUG DETECTED! A balance test calculation has failed verification rules.")
    except Exception as e:
        st.sidebar.error(f"Execution Exception: Testing libraries missing. Details: {e}")
# app.py [PART 2: Main Operational Viewport & Split Layout Panels]

# ==============================================================================
# PRIMARY KPI SCOREBOARD DISPLAY GRID
# ==============================================================================
counts = PortfolioTransformer.compute_bucket_counts(base_df)
kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6 = st.columns(6)
kpi_col1.metric("📊 TOTAL FILTERED", int(len(base_df)))
kpi_col2.metric("🟢 BUCKET 0", int(counts['b0']))
kpi_col3.metric("🟡 BUCKET 1", int(counts['b1']))
kpi_col4.metric("🟠 BUCKET 2", int(counts['b2']))
kpi_col5.metric("🔴 BUCKET 3", int(counts['b3']))
kpi_col6.metric("☠️ BUCKET 4+", int(counts['b4']))

st.info(f"**Workspace Ledger State:** Active Subsets — Filter: {product_dropdown}")

# Data Presentation Ledger Grid Assembly
cols = ["UCIC", "LAN_PDT", "MODULE", "LOAN_NO", "CUSTOMERNAME", "LOAN_EMI", "LAN_INST_OV_AMT", "LAN_DPD", "BRANCH_DESC", "SOLID"]
available_cols = [c for c in cols if c in base_df.columns]
st.subheader("📋 Workspace Active Data Ledger Rows")
st.dataframe(base_df[available_cols], use_container_width=True, hide_index=True)

# ==============================================================================
# SPLIT DUAL PANEL LAYOUT DESIGN (AUDIT INSPECTOR vs VISUALIZATIONS)
# ==============================================================================
left_panel, right_panel = st.columns(2)

with left_panel:
    st.markdown("### 🔍 108-Header Cross-Product Audit Inspector")
    
    if base_df.empty:
        st.info("📂 Workspace filter arrays resulted in zero records. Adjust side menu constraints.")
    else:
        # Dynamically load customer identifiers based on selected active filters
        available_ucics = sorted(base_df["UCIC"].dropna().unique().tolist())
        target_id = st.selectbox(
            "Select Active Customer UCIC Key to Inspect:", 
            options=available_ucics,
            help="Sourced dynamically from filtered workspace memory matrix."
        )

        if target_id:
            record = base_df[base_df["UCIC"] == target_id]
            
            if not record.empty:
                row_slice = record.iloc.to_dict()
                
                # Fetch regulatory risk assertions from backend business matrix modules
                b_code, b_class, b_playbook = LoanCollectionsReportEngine.generate_audit_bucket_metadata(row_slice)
                row_slice["RESPONSE_CODE_NEW"] = LoanCollectionsReportEngine.extract_field_action_code(row_slice)
                
                st.subheader(f"🛡️ Audit Inspector Panel: {target_id}")
                
                # Render Clean Immutable Status Markers
                col_b1, col_b2 = st.columns(2)
                col_b1.metric("Regulatory Bucket Code", b_code)
                col_b2.metric("Portfolio Risk Tier", b_class)

                st.text_area(
                    label="Official Mandated Playbook Strategy Directive:", 
                    value=b_playbook, 
                    height=80, 
                    disabled=True,
                    help="Immutable policy directives governed by core risk compliance rule sets."
                )
                st.markdown("---")

                # Modular Presentation Elements Block
                st.markdown("##### 🏷️ Sourcing & Identification Parameters")
                WorkstationUIComponents.display_isolated_audit_field_block("Customer Legal Title", row_slice.get('CUSTOMERNAME', ''))
                WorkstationUIComponents.display_isolated_audit_field_block("Loan Contract Number", row_slice.get('LOAN_NO', ''))
                WorkstationUIComponents.display_isolated_audit_field_block("Originating Branch Title", row_slice.get('BRANCH_DESC', 'NONE'))
                WorkstationUIComponents.display_isolated_audit_field_block("Core Banking SOL ID", row_slice.get('SOLID', 'NONE'))
                WorkstationUIComponents.display_isolated_audit_field_block("Asset Allocation Zone", row_slice.get('RCLG_ZONE', 'NONE'))
                WorkstationUIComponents.display_isolated_audit_field_block("Jurisdiction State", row_slice.get('STATE', 'NONE'))
                
                st.markdown("##### 💳 Financial Balances & Balances Aging Matrix")
                try:
                    disb_val = f"₹{int(float(row_slice.get('LAN_DISB_AMT', 0))):,}"
                    pos_val = f"₹{int(float(row_slice.get('LAN_POS', 0))):,}"
                    ovd_val = f"₹{int(float(row_slice.get('LAN_INST_OV_AMT', 0))):,}"
                    charge_val = f"₹{int(float(row_slice.get('OVERDUE_CHARGE', 0))):,}"
                except Exception:
                    disb_val = row_slice.get('LAN_DISB_AMT', '0')
                    pos_val = row_slice.get('LAN_POS', '0')
                    ovd_val = row_slice.get('LAN_INST_OV_AMT', '0')
                    charge_val = row_slice.get('OVERDUE_CHARGE', '0')

                WorkstationUIComponents.display_isolated_audit_field_block("Original Disbursed Principal", disb_val)
                WorkstationUIComponents.display_isolated_audit_field_block("Live Running Balance (POS)", pos_val)
                WorkstationUIComponents.display_isolated_audit_field_block("Total Overdue Principal Due", ovd_val)
                WorkstationUIComponents.display_isolated_audit_field_block("Accrued Outlier Penalty Fees", charge_val)
                
                st.markdown("##### 🚨 Delinquency Metrics & Enforcement Indicators")
                WorkstationUIComponents.display_isolated_audit_field_block("Continuous Days Past Due", f"{row_slice.get('LAN_DPD', 0)} Days", is_critical=True)
                WorkstationUIComponents.display_isolated_audit_field_block("Systemic Field Response Action Tag", row_slice.get('RESPONSE_CODE_NEW', 'PAID_VIA_CLEARING'), is_critical=True)

                st.markdown("---")
                
                # Safe Structural Report PDF Compilation Trigger Block
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
        st.info("⚠️ No active dataset variations available to output visual metrics.")
    else: 
        # Inject Decoupled Graphical Component Engine Rendering Model
        st.plotly_chart(
            ExposureChartFactory.generate_exposure_chart(base_df, product_dropdown), 
            use_container_width=True
        )

# ==============================================================================
# MASTER STRUCTURAL FOOTER COMPONENT INJECTION
# ==============================================================================
WorkstationUIComponents.render_corporate_footer()
