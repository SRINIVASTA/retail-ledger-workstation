# app/visualizer.py
import pandas as pd
import plotly.express as px

class ExposureChartFactory:
    """Builds decoupled Plotly components from active data workspace tracking metrics."""

    @staticmethod
    def generate_exposure_chart(df: pd.DataFrame, product_selection: str):
        if product_selection == "[ SHOW ALL PRODUCTS ]":
            summary = df.groupby("LAN_PDT")["EXPOSURE_POS"].sum().reset_index()
            color_map = {
                "PERSONAL_LOAN": "#2980b9", "CREDIT_CARD": "#8e44ad", 
                "VEHICLE_LOAN": "#27ae60", "HOME_LOAN": "#d35400", 
                "GOLD_LOAN": "#f1c40f", "LAP": "#16a085"
            }
            names_col = "LAN_PDT"
            title = "Total Active Capital Exposure Share"
        else:
            summary = df.groupby("LAN_BKT")["EXPOSURE_POS"].sum().reset_index()
            summary["BKT_NAME"] = "Bucket " + summary["LAN_BKT"].astype(str)
            color_map = {
                "Bucket 0": "#27ae60", "Bucket 1": "#f1c40f", 
                "Bucket 2": "#e67e22", "Bucket 3": "#d35400", 
                "Bucket 4": "#c0392b"
            }
            names_col = "BKT_NAME"
            title = f"Capital Exposure Distribution — {product_selection}"

        fig = px.pie(summary, values="EXPOSURE_POS", names=names_col, color=names_col, color_discrete_map=color_map, hole=0.4)
        fig.update_traces(
            textinfo="percent+label", 
            textposition="outside", 
            hovertemplate="<b>%{label}</b><br>Exposure: ₹%{value:,.0f}<br>% Share: %{percent}"
        )
        fig.update_layout(
            title={"text": f"<b>{title}</b>", "y": 0.95, "x": 0.5, "xanchor": "center"}, 
            showlegend=False, 
            margin=dict(t=60, b=20, l=20, r=20), 
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)"
        )
        return fig
