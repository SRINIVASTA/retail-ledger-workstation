import os
import pandas as pd
import streamlit as st

# Import the detached functional logic modules
import engine

st.set_page_config(
    page_title="CreditPulse AI Workstation",
    layout="wide",
    initial_sidebar_state="expanded",
)

FILE_PATH = "data/loan_master_portfolio_5_buckets.csv"


@st.cache_data
def load_portfolio_data(path):
    if os.path.exists(path):
        return pd.read_csv(path)
    return None


portfolio_df = load_portfolio_data(FILE_PATH)

if portfolio_df is None:
    st.error(
        f"❌ Injection Error: Master file '{FILE_PATH}' not found. Verify your layout."
    )
    st.stop()

# Sidebar Controls
st.sidebar.title("Ledger Workspace Controls")
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

# Apply Filters
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

# Call Engine Logic to render layout components
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

# Split Layout Panel
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
                    target_id, record.iloc[0].to_dict()
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
