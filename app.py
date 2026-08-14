import pandas as pd
import streamlit as st

# Import the detached functional logic modules
import engine

st.set_page_config(
    page_title="CreditPulse AI Workstation",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Render Title Header Banner
st.markdown(
    """
    <div style='background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 18px; text-align: center; border-radius: 6px; margin-bottom: 20px;'>
        <h2 style='color: white; margin: 0; font-family: -apple-system,BlinkMacSystemFont,"Segoe UI"; font-weight: 600; letter-spacing: 0.5px;'>
            📈 CREDITPULSE AI — MULTI-PRODUCT RETAIL LEDGER WORKSTATION
        </h2>
    </div>
""",
    unsafe_html=True,
)

# ==============================================================================
# STREAMLIT NATIVE FILE UPLOADER CONTROL PANEL
# ==============================================================================
st.sidebar.title("Ledger Workspace Controls")

st.sidebar.markdown("### 📂 Step 1: Data Injection")
# File uploader box explicitly locking down format verification parameters
uploaded_file = st.sidebar.file_uploader(
    "Upload Portfolio Ledger CSV File", 
    type=["csv"],
    help="Upload your credit portfolio file containing required operational ledger fields."
)

# Block dashboard presentation until user successfully drops a CSV dataset stream
if uploaded_file is None:
    st.info("👋 **Welcome to CreditPulse AI!** To begin managing cross-product risk, please upload your portfolio ledger CSV file using the container panel in the sidebar.")
    
    # GitHub styled placeholder helper box layout
    st.markdown(
        """
        <div style='border: 1px dashed #d0d7de; padding: 40px; text-align: center; border-radius: 6px; background-color: #f6f8fa; margin-top: 20px;'>
            <h3 style='color: #57606a; margin: 0 0 8px 0;'>Workspace Ledger is currently empty</h3>
            <p style='color: #57606a; margin: 0; font-size: 14px;'>Use the <b>"Upload Portfolio Ledger CSV File"</b> browser tool on the left to inject active customer records.</p>
        </div>
        """,
        unsafe_html=True
    )
    st.stop()

# Cache parsed user uploaded byte buffers safely in system memory indices
@st.cache_data
def parse_uploaded_ledger(file_buffer):
    try:
        return pd.read_csv(file_buffer)
    except Exception as e:
        st.error(f"❌ Structural Read Error: Verify file formatting properties. Details: {e}")
        return None

portfolio_df = parse_uploaded_ledger(uploaded_file)

if portfolio_df is None:
    st.stop()

# ==============================================================================
# INTERACTIVE CORES & FILTERS PIPELINE
# ==============================================================================
st.sidebar.markdown("### 🎯 Step 2: Workspace Filtering")
product_options = [
    "[ SHOW ALL PRODUCTS ]",
    "PERSONAL_LOAN",
    "CREDIT_CARD",
    "VEHICLE_LOAN",
    "HOME_LOAN",
    "GOLD_LOAN",
    "LAP",
]
product_dropdown = st.sidebar.selectbox(
    "Product Category:", product_options, index=0
)
omni_search_box = st.sidebar.text_input(
    "Omni Search Filter:",
    placeholder="Type profile name, UCIC ID, or loan registry file number...",
).strip()

# Apply Dynamic Filters
base_df = (
    portfolio_df
    if product_dropdown == "[ SHOW ALL PRODUCTS ]"
    else portfolio_df[portfolio_df["LAN_PDT"] == product_dropdown]
)
if omni_search_box:
    q = omni_search_box.upper()
    base_df = base_df[
        base_df["UCIC"].str.upper().str.contains(q, na=False)
        | base_df["LOAN_NO"].str.upper().str.contains(q, na=False)
        | base_df["CUSTOMERNAME"].str.upper().str.contains(q, na=False)
    ]

# ==============================================================================
# DASHBOARD OUTPUT DISPLAY
# ==============================================================================
# Call Engine Logic to render template KPI headers layout components
metrics_html = engine.render_metrics_board_html(base_df, product_dropdown)
st.markdown(metrics_html, unsafe_html=True)

# Datagrid Panel
cols = [
    "UCIC",
    "LAN_PDT",
    "MODULE",
    "LOAN_NO",
    "CUSTOMERNAME",
    "LOAN_EMI",
    "LAN_INST_OV_AMT",
    "LAN_DPD",
    "NPA_TYPE",
    "WRITEOFF_TAG",
]
available_cols = [c for c in cols if c in base_df.columns]
st.subheader("📋 Workspace Active Data Ledger Rows")
st.dataframe(base_df[available_cols], use_container_width=True, hide_index=True)

# Split Layout Panel (Audits and Visual Plots Side-by-Side)
left_panel, right_panel = st.columns()

with left_panel:
    st.markdown("### 🔍 108-Header Cross-Product Audit Inspector")
    with st.form("audit_form"):
        audit_input_box = st.text_input(
            "Audit Variable (Input UCIC Key):",
            placeholder="Type or copy an active customer UCIC key...",
        ).strip()
        submit_audit = st.form_submit_button(
            "Inspect Complete 108 Headers Map", type="primary"
        )

    if submit_audit:
        if not audit_input_box:
            st.warning("⚠️ Error: Please type an active Customer UCIC code first.")
        else:
            target_id = audit_input_box.upper()
            record = portfolio_df[
                portfolio_df["UCIC"].str.upper() == target_id
            ]

            if record.empty:
                st.error(
                    f"❌ Error: Account key '{target_id}' does not exist inside system memory indices."
                )
            else:
                inspector_html = engine.render_audit_inspector_html(
                    target_id, record.iloc.to_dict()
                )
                st.markdown(inspector_html, unsafe_html=True)

with right_panel:
    st.markdown("### 📊 Reconciled Capital Exposure Share Frame")
    if base_df.empty:
        st.info("⚠️ No data available for selected filters to plot chart analysis.")
    else:
        # Render clean native Plotly chart tracking calculations
        chart_figure = engine.generate_exposure_plotly(base_df, product_dropdown)
        st.plotly_chart(chart_figure, use_container_width=True)
