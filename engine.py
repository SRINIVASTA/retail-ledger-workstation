import pandas as pd
import plotly.express as px

def compute_bucket_counts(df: pd.DataFrame) -> dict:
    """Calculates row counts across all 5 delinquency stages safely."""
    if df.empty:
        return {"b0": 0, "b1": 0, "b2": 0, "b3": 0, "b4": 0}
        
    bkt_series = df["LAN_BKT"].astype(str).str.strip()
    return {
        "b0": len(df[bkt_series == "0"]),
        "b1": len(df[bkt_series == "1"]),
        "b2": len(df[bkt_series == "2"]),
        "b3": len(df[bkt_series == "3"]),
        "b4": len(df[bkt_series == "4"]),
    }

def generate_exposure_plotly(df: pd.DataFrame, product_selection: str):
    """Assembles an interactive Plotly donut chart configuration."""
    if product_selection == "[ SHOW ALL PRODUCTS ]":
        summary = df.groupby("LAN_PDT")["EXPOSURE_POS"].sum().reset_index()
        color_map = {
            "PERSONAL_LOAN": "#2980b9", "CREDIT_CARD": "#8e44ad", "VEHICLE_LOAN": "#27ae60",
            "HOME_LOAN": "#d35400", "GOLD_LOAN": "#f1c40f", "LAP": "#16a085"
        }
        names_col = "LAN_PDT"
        title = "Total Active Capital Exposure Share (Cross-Product Overview)"
    else:
        summary = df.groupby("LAN_BKT")["EXPOSURE_POS"].sum().reset_index()
        summary["BKT_NAME"] = "Bucket " + summary["LAN_BKT"].astype(str)
        color_map = {
            "Bucket 0": "#27ae60", "Bucket 1": "#f1c40f", "Bucket 2": "#e67e22",
            "Bucket 3": "#d35400", "Bucket 4": "#c0392b"
        }
        names_col = "BKT_NAME"
        title = f"Full 5-Stage Capital Exposure Distribution — {product_selection}"

    fig = px.pie(
        summary, values="EXPOSURE_POS", names=names_col,
        color=names_col, color_discrete_map=color_map, hole=0.4
    )
    fig.update_traces(
        textinfo="percent+label", textposition="outside",
        hovertemplate="<b>%{label}</b><br>Exposure: ₹%{value:,.0f}<br>% Share: %{percent}"
    )
    fig.update_layout(
        title={"text": f"<b>{title}</b>", "y": 0.95, "x": 0.5, "xanchor": "center"},
        showlegend=False, margin=dict(t=60, b=20, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig
