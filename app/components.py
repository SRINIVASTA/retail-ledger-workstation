# app/components.py
import streamlit as st
from typing import Any

class WorkstationUIComponents:
    """Manages application presentation and custom corporate styling elements."""

    @staticmethod
    def inject_corporate_branding_theme() -> None:
        st.markdown(""" 
            <style> 
            header[data-testid="stHeader"] { visibility: hidden !important; display: none !important; } 
            div[data-testid="stToolbar"] { visibility: hidden !important; display: none !important; } 
            footer { visibility: hidden !important; } 
            [data-testid="stMainBlockContainer"], .main .block-container {
                padding-top: 1.5rem !important;
                padding-bottom: 8rem !important;
            }
            </style> 
            """, unsafe_allow_html=True)

    @staticmethod
    def render_enterprise_summary_banner() -> None:
        st.markdown("""
            <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 1.5rem; border-radius: 8px; color: white; margin-bottom: 1.5rem;">
                <h2 style="margin: 0; font-size: 1.8rem; font-weight: 700; letter-spacing: -0.5px;">📈 CREDITPULSE AI — MULTI-PRODUCT RETAIL LEDGER WORKSTATION</h2>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.85; font-size: 0.95rem;">Bureau-Grade Ledger Asset Processing Engine & Analytical Risk Risk-Regulatory Delinquency Workspace</p>
            </div>
            """, unsafe_allow_html=True)

    @staticmethod
    def render_corporate_footer() -> None:
        st.markdown( 
            """ 
            <style> 
            .enterprise-footer { 
                position: fixed; left: 0; bottom: 0; width: 100%; background-color: #1e293b; 
                color: #f8fafc; text-align: center; font-size: 12px; padding: 10px 0; 
                z-index: 9999999 !important; border-top: 2px solid #3b82f6; 
            } 
            .enterprise-footer a { color: #3b82f6; text-decoration: none; margin: 0 8px; font-weight: 600; } 
            .enterprise-footer a:hover { text-decoration: underline; color: #f1f5f9; } 
            </style> 
            <div class="enterprise-footer"> 
                <span><strong>© 2026 T A Srinivas.</strong> All Rights Reserved. Bank Portfolio Execution Workstation Engine Prototype.</span> 
                <a href="https://linkedin.com" target="_blank">LinkedIn Profile</a> |
                <a href="mailto:tasrinivass@gmail.com">Contact Systems Desk</a> 
            </div> 
            """, 
            unsafe_allow_html=True 
        )

    @staticmethod
    def display_isolated_audit_field_block(label: str, value: Any, is_critical: bool = False) -> None:
        color = "#c0392b" if is_critical else "#1a202c"
        weight = "bold" if is_critical else "normal"
        st.markdown(
            f"<div style='padding: 4px 0; border-bottom: 1px solid #f1f5f9; font-size: 0.9rem;'>"
            f"<span style='color: #64748b; font-weight: 600;'>{label}:</span> "
            f"<span style='color: {color}; font-weight: {weight};'>{value}</span>"
            f"</div>", 
            unsafe_allow_html=True
        )
