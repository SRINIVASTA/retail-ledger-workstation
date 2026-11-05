# app.py [PART 1 - Update only this specific block around lines 90-120]

# ==============================================================================
# SIDEBAR CONTROL CENTER - STEP 3: SYSTEMS STABILITY DIAGNOSTICS WITH DEBUGGING
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
        
        # Intercept standard output to print the exact test traceback on your dashboard screen
        capture_buffer = StringIO()
        old_stdout = sys.stdout
        sys.stdout = capture_buffer
        
        # 🟢 CHANGED: Replaced singular script call with the full "tests/" folder index block
        # This scans and runs BOTH test_calculations.py and test_mock_distribution.py in parallel
        exit_code = pytest.main(["-v", "--tb=long", "tests/"])
        
        # Restore normal output routing streams
        sys.stdout = old_stdout
        test_logs = capture_buffer.getvalue()

        if exit_code == 0:
            st.sidebar.success("✅ ALL TESTS PASSED! Backend calculation engine is 100% accurate.")
            st.toast("System Integrity Verified: 100% Stable", icon="✅")
        else:
            st.sidebar.error("❌ CRITICAL BUG DETECTED!")
            # Expose the hidden test traceback logs directly inside an expander drawer for troubleshooting
            with st.sidebar.expander("🛠️ View Internal PyTest Error Details", expanded=True):
                st.code(test_logs, language="text")
                
    except Exception as e:
        st.sidebar.error(f"Execution Exception: Testing libraries missing. Details: {e}")
# app.py [PART 2: Main Operational Viewport & Split Layout Panels]

# Render Scoreboard KPI block responsive to deep geographic filters
counts = PortfolioTransformer.compute_bucket_counts(base_df)
kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6 = st.columns(6)
kpi_col1.metric("📊 TOTAL FILTERED", int(len(base_df)))
kpi_col2.metric("🟢 BUCKET 0", int(counts['b0']))
kpi_col3.metric("🟡 BUCKET 1", int(counts['b1']))
kpi_col4.metric("🟠 BUCKET 2", int(counts['b2']))
kpi_col5.metric("🔴 BUCKET 3", int(counts['b3']))
kpi_col6.metric("☠️ BUCKET 4+", int(counts['b4']))

# Formulate location status string block
loc_status = f"Zone: {selected_zone} | State: {selected_state} | Branch: {selected_branch}"
st.info(f"**Workspace Ledger State:** Filter Mode: {product_dropdown} ({loc_status})")

# Main Data Table Display Layer
cols = ["UCIC", "LAN_PDT", "MODULE", "LOAN_NO", "CUSTOMERNAME", "LOAN_EMI", "LAN_INST_OV_AMT", "LAN_DPD", "BRANCH_DESC", "RCLG_ZONE", "STATE"]
available_cols = [c for c in cols if c in base_df.columns]
st.subheader("📋 Workspace Active Data Ledger Rows")
st.dataframe(base_df[available_cols], use_container_width=True, hide_index=True)

left_panel, right_panel = st.columns(2)

with left_panel:
    # Folded collapsible box wrapper container
    with st.expander("🔍 Open 108-Header Cross-Product Audit Inspector", expanded=False):
        if base_df.empty:
            st.info("📂 Workspace is empty. Readjust side menu sorting parameters.")
        else:
            available_ucics = sorted(base_df["UCIC"].dropna().unique().tolist())
            target_id = st.selectbox("Select Active Customer UCIC Key to Inspect:", options=available_ucics)

            if target_id:
                record = base_df[base_df["UCIC"] == target_id]
                
                if not record.empty:
                    # Run dataframe level text validation before positional dict parsing
                    row_slice = record.fillna("NONE").iloc[0].to_dict()
                    
                    # Intercept whitespace or missing string values
                    for key, val in list(row_slice.items()):
                        if str(val).strip() in ["", "nan", "NaN", "None", "NONE", "0"]:
                            row_slice[key] = "NONE"
                    
                    # Direct client field fallback verification
                    if row_slice.get("MODULE") == "NONE":
                        pdt = str(row_slice.get("LAN_PDT", "")).strip().upper()
                        if pdt in ["HOME_LOAN", "LAP"]:
                            row_slice["MODULE"] = "SECURED_MORTGAGES"
                        elif pdt == "CREDIT_CARD":
                            row_slice["MODULE"] = "UNSECURED_CARDS"
                        else:
                            row_slice["MODULE"] = "RETAIL_UNSECURED"
                    
                    b_code, b_class, b_playbook = LoanCollectionsReportEngine.generate_audit_bucket_metadata(row_slice)
                    row_slice["RESPONSE_CODE_NEW"] = LoanCollectionsReportEngine.extract_field_action_code(row_slice)
                    
                    st.subheader(f"🛡️ Audit Inspector Panel: {target_id}")
                    col_b1, col_b2 = st.columns(2)
                    col_b1.metric("Regulatory Bucket Code", b_code)
                    col_b2.metric("Portfolio Risk Tier", b_class)

                    st.text_area(label="Official Mandated Playbook Strategy Directive:", value=b_playbook, height=80, disabled=True)
                    st.markdown("---")

                    st.markdown("##### 🏷️ Sourcing & Identification Parameters")
                    WorkstationUIComponents.display_isolated_audit_field_block("Customer Legal Title", row_slice.get('CUSTOMERNAME', ''))
                    WorkstationUIComponents.display_isolated_audit_field_block("Module Category Tag", row_slice.get('MODULE', ''))
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
        st.plotly_chart(ExposureChartFactory.generate_exposure_chart(base_df, product_dropdown), use_container_width=True)

WorkstationUIComponents.render_corporate_footer()
