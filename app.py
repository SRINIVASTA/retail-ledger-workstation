import pandas as pd
import streamlit as st
import engine
import logging 


# --- 3. FORCE STREAMLIT CHROMIUM HIDING LAYERS & GAP FIX ---
st.markdown(""" 
 <style> 
 header[data-testid="stHeader"] { visibility: hidden !important; display: none !important; } 
 div[data-testid="stToolbar"] { visibility: hidden !important; display: none !important; } 
 footer { visibility: hidden !important; } 
 
 [data-testid="stMainBlockContainer"] {
     padding-top: 1rem !important;
 }
 .main .block-container {
     padding-top: 1rem !important;
 }
 </style> 
 """, unsafe_allow_html=True) 

logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger("FIREWALL") 

st.set_page_config(
    page_title="CreditPulse AI Workstation",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📈 CREDITPULSE AI — MULTI-PRODUCT RETAIL LEDGER WORKSTATION")
st.divider()

# ==============================================================================
# STREAMLIT NATIVE FILE UPLOADER CONTROL PANEL
# ==============================================================================
st.sidebar.title("Ledger Workspace Controls")
st.sidebar.markdown("### 📂 Step 1: Data Injection")
uploaded_file = st.sidebar.file_uploader(
    "Upload Portfolio Ledger CSV File", type=["csv"],
    help="Upload your credit portfolio file containing required operational ledger fields."
)

if uploaded_file is None:
    st.info("💡 **Welcome to CreditPulse AI!** To begin, please upload your portfolio ledger CSV file using the sidebar.")
    st.warning("⚠️ Workspace Ledger is currently empty. Use the upload tool on the left side menu to inject records.")
    st.stop()

@st.cache_data
def parse_uploaded_ledger(file_buffer):
    try: 
        raw_df = pd.read_csv(file_buffer)
        # Dynamic expansion step: Pass the raw 25 headers to compile the 108 master grid
        from engine import transform_25_to_108_ledger
        return transform_25_to_108_ledger(raw_df)
    except Exception as e:
        st.error(f"❌ Structural Read/Transformation Error: {e}")
        return None

portfolio_df = parse_uploaded_ledger(uploaded_file)
if portfolio_df is None: 
    st.stop()

# ==============================================================================
# INTERACTIVE CORES & FILTERS PIPELINE
# ==============================================================================
st.sidebar.markdown("### 🎯 Step 2: Workspace Filtering")
product_options = ["[ SHOW ALL PRODUCTS ]", "PERSONAL_LOAN", "CREDIT_CARD", "VEHICLE_LOAN", "HOME_LOAN", "GOLD_LOAN", "LAP"]
product_dropdown = st.sidebar.selectbox("Product Category:", product_options, index=0)
omni_search_box = st.sidebar.text_input("Omni Search Filter:", placeholder="Type name, UCIC ID, or loan file number...").strip()

# 1. Isolate target product selection frame 
if product_dropdown == "[ SHOW ALL PRODUCTS ]":
    base_df = portfolio_df.copy()
else:
    # Explicit type casting string matching to secure absolute matrix separation
    base_df = portfolio_df[portfolio_df["LAN_PDT"].astype(str) == str(product_dropdown)]

# 2. Layer global character search boundaries across active slices
if omni_search_box:
    q = omni_search_box.upper()
    base_df = base_df[
        base_df["UCIC"].astype(str).str.upper().str.contains(q, na=False) |
        base_df["LOAN_NO"].astype(str).str.upper().str.contains(q, na=False) |
        base_df["CUSTOMERNAME"].astype(str).str.upper().str.contains(q, na=False)
    ]

# 3. GLOBAL BINDING EXPORT: Reassign your active workspace tracking variable
# Ensure that your downstream variable (e.g., filtered_df) evaluates ONLY this subset
filtered_df = base_df

# ==============================================================================
# SIDEBAR DIAGNOSTICS CONTROL PANEL 
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
        exit_code = pytest.main(["-q", "--tb=short", "test_engine.py"])
        
        if exit_code == 0:
            st.sidebar.success("✅ ALL TESTS PASSED! Backend logic calculation engine is 100% accurate.")
            st.toast("System Integrity Verified: 100% Stable", icon="✅")
        else:
            st.sidebar.error("❌ CRITICAL BUG DETECTED! A calculation filter logic has failed validation rules.")
            st.sidebar.warning("Please review your engine.py variables or spreadsheet column structures.")
    except Exception as e:
        st.sidebar.error(f"Execution Error: Missing testing dependencies in requirements.txt. Details: {e}")
else:
    st.sidebar.caption("💤 Diagnostics system idle. Check the box above to verify asset logic pools.")

# ==============================================================================
# MAIN DASHBOARD METRICS DISPLAY
# ==============================================================================
counts = engine.compute_bucket_counts(base_df)
kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6 = st.columns(6)
kpi_col1.metric("📊 TOTAL FILTERED", int(len(base_df)))
kpi_col2.metric("🟢 BUCKET 0", int(counts['b0']))
kpi_col3.metric("🟡 BUCKET 1", int(counts['b1']))
kpi_col4.metric("🟠 BUCKET 2", int(counts['b2']))
kpi_col5.metric("🔴 BUCKET 3", int(counts['b3']))
kpi_col6.metric("☠️ BUCKET 4", int(counts['b4']))

st.info(f"**Workspace Ledger State:** Active Portfolio Profile Subsets — Filter: {product_dropdown}")

# Datagrid Panel
cols = ["UCIC", "LAN_PDT", "MODULE", "LOAN_NO", "CUSTOMERNAME", "LOAN_EMI", "LAN_INST_OV_AMT", "LAN_DPD", "NPA_TYPE", "WRITEOFF_TAG"]
available_cols = [c for c in cols if c in base_df.columns]
st.subheader("📋 Workspace Active Data Ledger Rows")
st.dataframe(base_df[available_cols], use_container_width=True, hide_index=True)

# ==============================================================================
# SPLIT LAYOUT PANEL (AUDIT INSPECTOR & PLOTLY VISUALIZATIONS)
# ==============================================================================
import collections_engine  # Ensure collections_engine.py is in your root folder!
# Add this import at the top of your existing app.py file

# ==============================================================================
# SPLIT LAYOUT PANEL (AUDIT INSPECTOR & PLOTLY VISUALIZATIONS)
# ==============================================================================

left_panel, right_panel = st.columns(2)

with left_panel:
    st.markdown("### 🔍 108-Header Cross-Product Audit Inspector")
    
    # 1. Filter out data based on selected category (e.g., PERSONAL_LOAN)
    filtered_df = portfolio_df[portfolio_df["PRODUCT_CATEGORY"] == "PERSONAL_LOAN"] if "PRODUCT_CATEGORY" in portfolio_df.columns else portfolio_df
    
    # 2. Prevent breaks if file isn't parsed yet
    if filtered_df.empty:
        st.info("📂 Please complete Step 1: Upload Portfolio Ledger CSV file above.")
    else:
        # 3. Pull actual UCIC keys from data matrix for easy collection selection
        available_ucics = sorted(filtered_df["UCIC"].dropna().unique().tolist())
        
        # 4. Interactive selection
        target_id = st.selectbox(
            "Select Active Customer UCIC Key to Inspect:", 
            options=available_ucics,
            help="Dynamically loaded from loan_master_portfolio_5_buckets.csv"
        )

        if target_id:
            record = filtered_df[filtered_df["UCIC"] == target_id]
            
            if not record.empty:
                # SAFE EXTRACTION: Added explicit row location index before parsing to dictionary
                row_slice = record.iloc[0].to_dict()
                
                st.subheader(f"🛡️ Audit Inspector Panel: {target_id}")
                
# ==============================================================================
# EXECUTIVE REPORT INSPECTION & RENDER PIPELINE (SYNCHRONIZED)
# ==============================================================================
# Pulls parameters safely out from the external module dependency
b_code, b_class, b_playbook = collections_engine.LoanCollectionsReportEngine.generate_audit_bucket_metadata(row_slice)

st.markdown("##### 🏛️ Risk Regulatory Status Report")

# Clean, non-interactive audit counters
col_b1, col_b2 = st.columns(2)
col_b1.metric("Regulatory Bucket Code", b_code)
col_b2.metric("Portfolio Risk Tier", b_class)

# Immutable operational directive field block
st.text_area(
    label="Official Mandated Playbook Strategy Directive:",
    value=b_playbook,
    height=100,
    disabled=True,
    help="Immutable policy directives governed by core risk compliance rule sets."
)
st.markdown("---")

st.markdown("##### 🏷️ Sourcing & Identification Parameters")
st.write(f"**Product Group (LAN_PDT):** {row_slice.get('LAN_PDT', '')}")
st.write(f"**Module Category:** {row_slice.get('MODULE', '')}")
st.write(f"**Customer Name:** {row_slice.get('CUSTOMERNAME', '')}")
st.write(f"**Loan Account No:** {row_slice.get('LOAN_NO', '')}")
st.write(f"**Original Disbursal Date:** {row_slice.get('DISB_DATE', '')}")

try:
    disb_amt = int(float(row_slice.get('LAN_DISB_AMT', 0)))
    st.write(f"**Disbursed Principal:** ₹{disb_amt:,}")
except:
    st.write(f"**Disbursed Principal:** ₹{row_slice.get('LAN_DISB_AMT', 0)}")
    
# FIXED: Shifted source references from selected_row over to row_slice to eliminate NameError crashes
st.markdown("### 🏠 Collateral Asset Verification Parameters")
st.write(f"**Make / Restructuring:** {row_slice.get('MAKE', 'NONE')}")
st.write(f"**Asset Model / Segment:** {row_slice.get('MODEL', 'NONE')}")
st.write(f"**Registration Refs (REGDNUM):** {row_slice.get('REGDNUM', 'NONE')}")
st.write(f"**HL / LAP Flags:** {row_slice.get('HL_NONHL', 'NON_HL')} | {row_slice.get('LAP_NONLAP', 'NON_LAP')}")

st.markdown("##### 💳 Monthly Billing & Active Balances")
st.write(f"**Gateway Presentation Mode:** {row_slice.get('REPAY_MODE', '')}")

try:
    st.write(f"**Loan Scheduled EMI:** ₹{int(float(row_slice.get('LOAN_EMI', 0))):,}")
    st.write(f"**Principal Bal (LAN_POS):** ₹{int(float(row_slice.get('LAN_POS', 0))):,}")
    st.write(f"**Total Exposure POS Risk:** ₹{int(float(row_slice.get('EXPOSURE_POS', 0))):,}")
except:
    st.write(f"**Loan Scheduled EMI:** ₹{row_slice.get('LOAN_EMI', 0)}")
    st.write(f"**Principal Bal (LAN_POS):** ₹{row_slice.get('LAN_POS', 0)}")
    st.write(f"**Total Exposure POS Risk:** ₹{row_slice.get('EXPOSURE_POS', 0)}")

st.markdown("##### 🚨 Delinquency Buckets & Field Allocations")
st.error(f"**Days Past Due (LAN_DPD):** {row_slice.get('LAN_DPD', 0)} Days")
st.write(f"**Risk Bucket:** Bucket {row_slice.get('LAN_BKT', 0)}")

try:
    st.write(f"**Total Overdue Principal:** ₹{int(float(row_slice.get('LAN_INST_OV_AMT', 0))):,}")
    st.write(f"**Late Presentation Fees:** ₹{int(float(row_slice.get('OVERDUE_CHARGE', 0))):,}")
except:
    st.write(f"**Total Overdue Principal:** ₹{row_slice.get('LAN_INST_OV_AMT', 0)}")
    st.write(f"**Late Presentation Fees:** ₹{row_slice.get('OVERDUE_CHARGE', 0)}")
    
st.write(f"**Assigned Agency ID Desk:** {row_slice.get('FINAL_ALLO_ID', '')}")
st.write(f"**Field Action Response Code:** {row_slice.get('RESPONSE_CODE_NEW', '')}")
st.write(f"**NPA Status Code:** {row_slice.get('NPA_TYPE', '')}")
st.write(f"**Account Writeoff Status:** {row_slice.get('WRITEOFF_TAG', '')}")

st.markdown("---")
st.markdown("##### 📥 Export Official Records")

pdf_payload = engine.generate_audit_pdf(target_id, row_slice)

st.download_button(
    label="Download Executive PDF Audit Report",
    data=pdf_payload,
    file_name=f"Audit_Report_{target_id}.pdf",
    mime="application/pdf",
    type="primary",
    use_container_width=True # FIXED: Replaced invalid ReportLab 'width' parameter with st.download_button container alignment flag
)

with right_panel:
    st.markdown("### 📊 Reconciled Capital Exposure Share Frame")
    if base_df.empty: 
        st.info("⚠️ No data available to plot chart analysis.")
    else: 
        # FIXED: Replaced invalid width argument with standard responsive container property
        st.plotly_chart(
            engine.generate_exposure_plotly(base_df, product_dropdown), 
            use_container_width=True
        )

# =============================================================================
# --- 7. ABSOLUTE LAST LINE OF APP.PY (GUARANTEED EXECUTING IN BOTH STATES) ---
# =============================================================================
st.markdown( 
 """ 
 <style> 
 .footer { 
     position: fixed; 
     left: 0; 
     bottom: 0; 
     width: 100%; 
     background-color: #262730; 
     color: #FAFAFA; 
     text-align: center; 
     font-size: 13px; 
     padding: 12px 0; 
     z-index: 9999999 !important; 
     border-top: 1px solid #FF4B4B; 
 } 
 .footer a { 
     color: #FF4B4B; 
     text-decoration: none; 
     margin: 0 10px; 
     font-weight: bold; 
 } 
 .footer a:hover { 
     text-decoration: underline; 
     color: #FAFAFA; 
 } 
 .footer-separator { 
     color: #666; 
     margin: 0 5px; 
 } 
 [data-testid="stMainBlockContainer"] { 
     padding-bottom: 120px !important; 
 } 
 .main .block-container {
     padding-bottom: 120px !important;
 }
 </style> 
 <div class="footer"> 
     <span><strong>© 2026 T A Srinivas.</strong> All Rights Reserved. Prototype for portfolio display. For commercial licensing requests, please use the contact channels.</span> 
     <span class="footer-separator">|</span> 
     <a href="https://www.linkedin.com/in/srinivas-t-a-557637119/" target="_blank">LinkedIn Profile</a> 
     <span class="footer-separator">|</span> 
     <a href="mailto:tasrinivass@gmail.com">Contact Me</a> 
 </div> 
 """, 
 unsafe_allow_html=True 
)
