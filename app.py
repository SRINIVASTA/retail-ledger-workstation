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

# KPI Display Row
counts = engine.compute_bucket_counts(base_df)
kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6 = st.columns(6)
kpi_col1.metric("📊 TOTAL FILTERED", int(len(base_df)))
kpi_col2.metric("🟢 BUCKET 0", int(counts['b0']))
kpi_col3.metric("🟡 BUCKET 1", int(counts['b1']))
kpi_col4.metric("🟠 BUCKET 2", int(counts['b2']))
kpi_col5.metric("🔴 BUCKET 3", int(counts['b3']))
kpi_col6.metric("☠️ BUCKET 4", int(counts['b4']))

# LINE 60 FIX: Pure native component presentation bypasses the Python 3.14 tracking bug entirely
st.info(f"**Workspace Ledger State:** Active Portfolio Profile Subsets — Filter: {product_dropdown}")

# Datagrid Panel
cols = ["UCIC", "LAN_PDT", "MODULE", "LOAN_NO", "CUSTOMERNAME", "LOAN_EMI", "LAN_INST_OV_AMT", "LAN_DPD", "NPA_TYPE", "WRITEOFF_TAG"]
available_cols = [c for c in cols if c in base_df.columns]
st.subheader("📋 Workspace Active Data Ledger Rows")
st.dataframe(base_df[available_cols], use_container_width=True, hide_index=True)

# Split Layout Panel
left_panel, right_panel = st.columns(2)

with left_panel:
    st.markdown("### 🔍 108-Header Cross-Product Audit Inspector")
    with st.form("audit_form"):
        audit_input_box = st.text_input("Audit Variable (Input UCIC Key):", placeholder="Type or copy a UCIC key...").strip()
        submit_audit = st.form_submit_button("Inspect Complete 108 Headers Map", type="primary")

    if submit_audit:
        if not audit_input_box: 
            st.warning("⚠️ Error: Please type an active Customer UCIC code first.")
        else:
            target_id = audit_input_box.upper()
            record = portfolio_df[portfolio_df["UCIC"].str.upper() == target_id]
            if record.empty: 
                st.error(f"❌ Error: Account key '{target_id}' does not exist.")
            else:
                row_slice = record.iloc[0].to_dict()
                
                # Pure Native clean audit field list rendering layout
                st.subheader(f"🛡️ Audit Inspector Panel: {target_id}")
                
                st.markdown("##### 🏷️ Sourcing & Identification Parameters")
                st.write(f"**Product Group (LAN_PDT):** {row_slice.get('LAN_PDT', '')}")
                st.write(f"**Module Category:** {row_slice.get('MODULE', '')}")
                st.write(f"**Customer Name:** {row_slice.get('CUSTOMERNAME', '')}")
                st.write(f"**Loan Account No:** {row_slice.get('LOAN_NO', '')}")
                st.write(f"**Original Disbursal Date:** {row_slice.get('DISB_DATE', '')}")
                st.write(f"**Disbursed Principal:** ₹{int(row_slice.get('LAN_DISB_AMT', 0)):,}")
                
                st.markdown("##### 🏠 Collateral Asset Verification Parameters")
                st.write(f"**Make / Restructuring:** {row_slice.get('MAKE', '')}")
                st.write(f"**Asset Model / Segment:** {row_slice.get('MODEL', '')}")
                st.write(f"**Registration Refs (REGDNUM):** {row_slice.get('REGDNUM', '')}")
                st.write(f"**HL / LAP Flags:** {row_slice.get('HL_NONHL', '')} | {row_slice.get('LAP_NONLAP', '')}")
                
                st.markdown("##### 💳 Monthly Billing & Active Balances")
                st.write(f"**Gateway Presentation Mode:** {row_slice.get('REPAY_MODE', '')}")
                st.write(f"**Loan Scheduled EMI:** ₹{int(row_slice.get('LOAN_EMI', 0)):,}")
                st.write(f"**Principal Bal (LAN_POS):** ₹{int(row_slice.get('LAN_POS', 0)):,}")
                st.write(f"**Total Exposure POS Risk:** ₹{int(row_slice.get('EXPOSURE_POS', 0)):,}")
                
                st.markdown("##### 🚨 Delinquency Buckets & Field Allocations")
                st.error(f"**Days Past Due (LAN_DPD):** {row_slice.get('LAN_DPD', 0)} Days")
                st.write(f"**Risk Bucket:** Bucket {row_slice.get('LAN_BKT', 0)}")
                st.write(f"**Total Overdue Principal:** ₹{int(row_slice.get('LAN_INST_OV_AMT', 0)):,}")
                st.write(f"**Late Presentation Fees:** ₹{int(row_slice.get('OVERDUE_CHARGE', 0)):,}")
                st.write(f"**Assigned Agency ID Desk:** {row_slice.get('FINAL_ALLO_ID', '')}")
                st.write(f"**Field Action Response Code:** {row_slice.get('RESPONSE_CODE_NEW', '')}")
                st.write(f"**NPA Status Code:** {row_slice.get('NPA_TYPE', '')}")
                st.write(f"**Account Writeoff Status:** {row_slice.get('WRITEOFF_TAG', '')}")

with right_panel:
    st.markdown("### 📊 Reconciled Capital Exposure Share Frame")
    if base_df.empty: 
        st.info("⚠️ No data available to plot chart analysis.")
    else: 
        st.plotly_chart(engine.generate_exposure_plotly(base_df, product_dropdown), use_container_width=True)
