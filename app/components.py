# app/components.py
import streamlit as st
from typing import Any

class WorkstationUIComponents:
    """Enterprise UI presentation factory injecting corporate styling & layout containers."""

    @staticmethod
    def inject_corporate_branding_theme() -> None:
        """Injects clean corporate styling arrays, hides Chromium artifacts, and stabilizes footers."""
        st.markdown(""" 
            <style> 
            /* Hide Streamlit Native Branding Bloat */
            header[data-testid="stHeader"] { visibility: hidden !important; display: none !important; } 
            div[data-testid="stToolbar"] { visibility: hidden !important; display: none !important; } 
            footer { visibility: hidden !important; } 
            
            /* Structural Optimization Framework */
            [data-testid="stMainBlockContainer"] {
                padding-top: 1.5rem !important;
                padding-bottom: 8rem !important;
            }
            .main .block-container {
                padding-top: 1.5rem !important;
                padding-bottom: 8rem !important;
            }
            .stExpander {
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                background-color: transparent !important;
            }
            </style> 
            """, unsafe_allow_html=True)

    @staticmethod
    def render_enterprise_summary_banner() -> None:
        """Renders an executive high-level workspace description panel."""
        st.markdown("""
            <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 1.5rem; border-radius: 8px; color: white; margin-bottom: 1.5rem;">
                <h2 style="margin: 0; font-size: 1.8rem; font-weight: 700; letter-spacing: -0.5px;">📈 CREDITPULSE AI — MULTI-PRODUCT RETAIL LEDGER WORKSTATION</h2>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.85; font-size: 0.95rem;">Bureau-Grade Ledger Asset Processing Engine & Analytical Risk Risk-Regulatory Delinquency Workspace</p>
            </div>
            """, unsafe_allow_html=True)

    @staticmethod
    def render_corporate_footer() -> None:
        """Injects a high-visibility, clean, compliant corporate disclaimer string block."""
        st.markdown( 
            """ 
            <style> 
            .enterprise-footer { 
                position: fixed; 
                left: 0; 
                bottom: 0; 
                width: 100%; 
                background-color: #1e293b; 
                color: #f8fafc; 
                text-align: center; 
                font-size: 12px; 
                padding: 12px 0; 
                z-index: 9999999 !important; 
                border-top: 2px solid #3b82f6; 
            } 
            .enterprise-footer a { 
                color: #3b82f6; 
                text-decoration: none; 
                margin: 0 8px; 
                font-weight: 600; 
            } 
            .enterprise-footer a:hover { 
                text-decoration: underline; 
                color: #f1f5f9; 
            } 
            .footer-divider { 
                color: #475569; 
                margin: 0 4px; 
            } 
            </style> 
            <div class="enterprise-footer"> 
                <span><strong>© 2026 T A Srinivas.</strong> All Rights Reserved. Bank Portfolio Execution Workstation Engine Prototype.</span> 
                <span class="footer-divider">|</span> 
                <a href="https://linkedin.com" target="_blank">LinkedIn Profile</a> 
                <span class="footer-divider">|</span> 
                <a href="mailto:tasrinivass@gmail.com">Contact Systems Desk</a> 
            </div> 
            """, 
            unsafe_allow_html=True 
        )

    @staticmethod
    def display_isolated_audit_field_block(label: str, value: Any, is_critical: bool = False) -> None:
        """Displays data attributes using flexible properties to guarantee theme cross-visibility."""
        # 🟢 MODIFIED: Critical metrics render red, standard parameters inherit config.toml colors automatically
        color = "#ef4444" if is_critical else "inherit"
        weight = "700" if is_critical else "500"
        
        # 🟢 MODIFIED: display: flex centers labels to the left and pushes values perfectly readable to the right
        st.markdown(
            f"<div style='padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.08); font-size: 0.95rem; display: flex; justify-content: space-between; align-items: center;'>"
            f"<span style='color: #94a3b8; font-weight: 600;'>{label}:</span>"
            f"<span style='color: {color}; font-weight: {weight}; text-align: right;'>{value}</span>"
            f"</div>", 
            unsafe_allow_html=True
        )
