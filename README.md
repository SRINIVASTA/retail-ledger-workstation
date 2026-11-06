# 📈 CreditPulse AI — Multi-Product Retail Ledger Workstation

An enterprise-ready financial workstation built with Streamlit for processing multi-product retail banking portfolios, risk-regulatory delinquency arrays, and parallel mock analytics across a 108-column bureau compliance ledger schema.

<img src="desktop.png" width="100%">

## 🏛️ System Architecture

The workstation decouples transactional computation routines (Zero I/O Core) from presentation layers to maintain a predictable analytical interface.

```mermaid
graph TD
    A[Spreadsheet Ingestion Node] -->|Raw Minimal CSV Matrix| B(core/transformations.py)
    B -->|1. Geotechnical Resolution Maps| C{PortfolioTransformer}
    B -->|2. Amortization Vectors| C
    B -->|3. Bureau History Mock Chains| C
    C -->|Unified 108-Column Ledger| D[In-Memory Session Context]
    D -->|Presentation Layer Interceptor| E(app/components.py)
    D -->|Plotly Matrix Rendering| F(app/visualizer.py)
    D -->|Compliance Audit Rules| G(business/playbooks.py)
    D -->|ReportLab Template Compiler| H(reports/pdf_factory.py)
```

### Ingestion & Extrapolation Lifecycle Pipeline

```mermaid
sequenceDiagram
    autonumber
    actor Auditor as Compliance Auditor
    participant UI as app.py (Streamlit Layer)
    participant Core as core/transformations.py (Math Core)
    participant Rules as business/playbooks.py (Rules Engine)
    
    Auditor->>UI: Upload Minimal 14-Column Ledger CSV
    UI->>Core: Ingest Raw Data Matrix
    Note over Core: Process Incomplete Keys,<br/>Deduce Missing Modules/Zones,<br/>Generate M1-M5 Bureau Chains.
    Core-->>UI: Return Fully Populated 108-Column DataFrame
    UI->>UI: Render KPI Scoreboard & Active Presentation Grids
    Auditor->>UI: Select Customer Identity Key (UCIC)
    UI->>Rules: Pass Context Row Dictionary Slice
    Rules-->>UI: Output Policy Directives & Legal Action Codes
    Auditor->>UI: Trigger Executive Audit Export Action
    UI-->>Auditor: Compile & Serve Clean ReportLab PDF Stream
```

---

## 📁 Repository Directory Tree

```text
📁 creditpulse-ai-workstation/
├── 📁 .streamlit/
│   └── config.toml                  # Global Dark-Theme Layout Server Configs
├── 📁 app/
│   ├── __init__.py
│   ├── components.py                # UI Layout Elements & Styles
│   └── visualizer.py                # Plotly Visual Charts Factory
├── 📁 business/
│   ├── __init__.py
│   └── playbooks.py                 # Bureau-Grade Delinquency & Playbook Rules
├── 📁 config/
│   ├── __init__.py
│   └── constants.py                 # Frozen 108-Header Definitions & Interest Maps
├── 📁 core/
│   ├── __init__.py
│   └── transformations.py           # Vectorised Balance Amortization Core
├── 📁 reports/
│   ├── __init__.py
│   └── pdf_factory.py               # ReportLab Compliance Document Compiler
├── 📁 tests/
│   ├── __init__.py
│   └── test_calculations.py         # Math Engine & Fallback Invariant Tests
|   └── test_mock_distribution.py         
├── app.py                           # Modular Application Entrypoint
├── loan_master_portfolio_5_buckets.csv # Geographic Mock Data Matrix File
├── requirements.txt                 # Dependency Framework Metrics
└── setup.py                         # Local Editable Packager Configurations
```

---

## 🚀 Local Host Installation & Boot Instructions

To run the workstation engine locally on your machine, follow these steps:

### 1. Configure the Local Environment & Install Dependencies
```bash
# 1. Access project workspace path
cd creditpulse-ai-workstation

# 2. Spawn targeted Python virtual node
python3 -m venv venv

# 3. Initialize terminal activation link context
# On macOS/Linux:
source venv/bin/activate
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1

# 4. Ingest and compile required packages
pip install -r requirements.txt
```

### 2. Link Local Path Architecture Dependencies
Register the editable setup script mapping to expose internal application directories (`app`, `core`, `config`):
```bash
pip install -e .
```

### 3. Launch the Workstation Server on LocalHost
Boot the UI layer using Streamlit on `port 8501`:
```bash
streamlit run app.py
```
Access the application directly in your browser at:
👉 **`http://localhost:8501`**

### 4. Run Automated Mathematics Diagnostic Suites
Verify math invariants and fallback deduction structures via PyTest:
```bash
pytest -v tests/test_calculations.py
```

---

## 🛡️ License, Copyright & Compliance Notices

**All Rights Reserved © 2026 T A Srinivas.**

Developed exclusively for portfolio demonstration profiles. **DO NOT DISTRIBUTE, CLONE, OR DUPLICATE.** Corporate licensing inquiries can be routed to `tasrinivass@gmail.com`.
