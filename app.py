import pandas as pd
import streamlit as st
import engine

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
        return pd.read_csv(file_buffer)
    except Exception as e:
        st.error(f"❌ Structural Read Error: {e}")
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

base_df = portfolio_df if product_dropdown == "[ SHOW ALL PRODUCTS ]" else portfolio_df[portfolio_df["LAN_PDT"] == product_dropdown]
if omni_search_box:
    q = omni_search_box.upper()
    base_df = base_df[
        base_df["UCIC"].str.upper().str.contains(q, na=False) |
        base_df["LOAN_NO"].str.upper().str.contains(q, na=False) |
        base_df["CUSTOMERNAME"].str.upper().str.contains(q, na=False)
    ]

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
        
        # 4. Use standard interactive selectbox instead of restrictive text input form
        target_id = st.selectbox(
            "Select Active Customer UCIC Key to Inspect:", 
            options=available_ucics,
            help="Dynamically loaded from loan_master_portfolio_5_buckets.csv"
        )

        if target_id:
            record = filtered_df[filtered_df["UCIC"] == target_id]
            row_slice = record.iloc[0].to_dict()
            
            st.subheader(f"🛡️ Audit Inspector Panel: {target_id}")
            
            # --------------------------------------------------------------
            # FAIL-SAFE TYPE CONVERSION FOR BUCKETS 0 TO 4
            # --------------------------------------------------------------
            try:
                # Capture possible float values (e.g., 3.0) or string representations (e.g., "3")
                raw_bkt = row_slice.get('LAN_BKT', 0)
                row_slice['LAN_BKT'] = int(float(raw_bkt)) if raw_bkt not in [None, ''] else 0
            except (ValueError, TypeError):
                row_slice['LAN_BKT'] = 0
            
            # Fetch behavioral strategies based on calculated index row
            playbook = collections_engine.LoanCollectionsEngine.get_playbook(row_slice)
            
            # Render strategic banner update inside workstation
            st.markdown(
                f"""
                <div style="background-color: {playbook.ui_color}12; 
                            padding: 15px; 
                            border-left: 6px solid {playbook.ui_color}; 
                            border-radius: 4px; 
                            margin-top: 5px;
                            margin-bottom: 20px;">
                    <h4 style="margin: 0; color: {playbook.ui_color}; font-size: 15px; font-weight: 700;">
                        [{playbook.tag_name}] — {playbook.stage_name}
                    </h4>
                    <p style="margin: 4px 0 0 0; font-size: 13px; color: #111111;">
                        {playbook.message}
                    </p>
                    <p style="margin: 6px 0 0 0; font-size: 12.5px; font-weight: 600; color: #222222;">
                        👉 <strong>Playbook Strategy Action:</strong> {playbook.strategy_action}
                    </p>
                </div>
                """, 
                unsafe_html=True
            )
            # --------------------------------------------------------------
            
            st.markdown("##### 🏷️ Sourcing & Identification Parameters")
            st.write(f"**Product Group (LAN_PDT):** {row_slice.get('LAN_PDT', '')}")
            st.write(f"**Module Category:** {row_slice.get('MODULE', '')}")
            st.write(f"**Customer Name:** {row_slice.get('CUSTOMERNAME', '')}")
            st.write(f"**Loan Account No:** {row_slice.get('LOAN_NO', '')}")
            st.write(f"**Original Disbursal Date:** {row_slice.get('DISB_DATE', '')}")
            st.write(f"**Disbursed Principal:** ₹{int(float(row_slice.get('LAN_DISB_AMT', 0))):,}")
            
            st.markdown("##### 🏠 Collateral Asset Verification Parameters")
            st.write(f"**Make / Restructuring:** {row_slice.get('MAKE', '')}")
            st.write(f"**Asset Model / Segment:** {row_slice.get('MODEL', '')}")
            st.write(f"**Registration Refs (REGDNUM):** {row_slice.get('REGDNUM', '')}")
            st.write(f"**HL / LAP Flags:** {row_slice.get('HL_NONHL', '')} | {row_slice.get('LAP_NONLAP', '')}")
            
            st.markdown("##### 💳 Monthly Billing & Active Balances")
            st.write(f"**Gateway Presentation Mode:** {row_slice.get('REPAY_MODE', '')}")
            st.write(f"**Loan Scheduled EMI:** ₹{int(float(row_slice.get('LOAN_EMI', 0))):,}")
            st.write(f"**Principal Bal (LAN_POS):** ₹{int(float(row_slice.get('LAN_POS', 0))):,}")
            st.write(f"**Total Exposure POS Risk:** ₹{int(float(row_slice.get('EXPOSURE_POS', 0))):,}")
            
            st.markdown("##### 🚨 Delinquency Buckets & Field Allocations")
            st.error(f"**Days Past Due (LAN_DPD):** {row_slice.get('LAN_DPD', 0)} Days")
            st.write(f"**Risk Bucket:** Bucket {row_slice.get('LAN_BKT', 0)}")
            st.write(f"**Total Overdue Principal:** ₹{int(float(row_slice.get('LAN_INST_OV_AMT', 0))):,}")
            st.write(f"**Late Presentation Fees:** ₹{int(float(row_slice.get('OVERDUE_CHARGE', 0))):,}")
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
                use_container_width=True
            )

with right_panel:
    st.markdown("### 📊 Reconciled Capital Exposure Share Frame")
    if base_df.empty: 
        st.info("⚠️ No data available to plot chart analysis.")
    else: 
        st.plotly_chart(engine.generate_exposure_plotly(base_df, product_dropdown), use_container_width=True)
