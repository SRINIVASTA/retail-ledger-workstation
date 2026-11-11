# 📈 CreditPulse AI — Multi-Product Retail Ledger Workstation

An enterprise-ready financial workstation built with Streamlit for processing multi-product retail banking portfolios, risk-regulatory delinquency arrays, and parallel mock analytics across a 108-column bureau compliance ledger schema.

<img src="desktop.png" width="100%">

## 🏛️ System Architecture

The workstation decouples transactional computation routines (Zero I/O Core) from presentation layers to maintain a predictable analytical interface.

```mermaid
flowchart TD
    %% Architecture Pipeline Nodes
    A[Spreadsheet Ingestion Node] e1@-->|Raw Minimal CSV Matrix| B(core/transformations.py)
    B e2@-->|1. Geotechnical Resolution Maps| C{PortfolioTransformer}
    B e3@-->|2. Amortization Vectors| C
    B e4@-->|3. Bureau History Mock Chains| C
    C e5@-->|Unified 108-Column Ledger| D[In-Memory Session Context]
    D e6@-->|Presentation Layer Interceptor| E(app/components.py)
    D e7@-->|Plotly Matrix Rendering| F(app/visualizer.py)
    D e8@-->|Compliance Audit Rules| G(business/playbooks.py)
    D e9@-->|ReportLab Template Compiler| H(reports/pdf_factory.py)

    %% Running Flow Animation Definitions
    e1@{ animate: true }
    e2@{ animate: true }
    e3@{ animate: true }
    e4@{ animate: true }
    e5@{ animate: true }
    e6@{ animate: true }
    e7@{ animate: true }
    e8@{ animate: true }
    e9@{ animate: true }

    %% Clean Visual Styling
    style A fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
    style C fill:#fff8e1,stroke:#f9a825,stroke-width:2px;
    style D fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;
```

### Ingestion & Extrapolation Lifecycle Pipeline

```mermaid
flowchart TD
    %% Actors & System Modules
    Auditor([👤 Compliance Auditor])
    UI[app.py: Streamlit Layer]
    Core(core/transformations.py: Math Core)
    Rules(business/playbooks.py: Rules Engine)

    %% Numbered Lifecycle Flow
    Auditor e1@-->|1. Upload Minimal 14-Column Ledger CSV| UI
    UI e2@-->|2. Ingest Raw Data Matrix| Core
    Core e3@-.->|3. Deduce Modules/Zones & M1-M5 Chains:<br/>Return 108-Column DataFrame| UI
    UI e4@-->|4. Render KPI Scoreboard & Active Grids| Auditor
    Auditor e5@-->|5. Select Customer Identity Key UCIC| UI
    UI e6@-->|6. Pass Context Row Dictionary Slice| Rules
    Rules e7@-.->|7. Output Policy Directives & Legal Codes| UI
    Auditor e8@-->|8. Trigger Executive Audit Export Action| UI
    UI e9@-.->|9. Compile & Serve ReportLab PDF Stream| Auditor

    %% Running Flow Animation Definitions
    e1@{ animate: true }
    e2@{ animate: true }
    e3@{ animate: true }
    e4@{ animate: true }
    e5@{ animate: true }
    e6@{ animate: true }
    e7@{ animate: true }
    e8@{ animate: true }
    e9@{ animate: true }

    %% Clean Role Styling
    style Auditor fill:#fff3e0,stroke:#ef6c00,stroke-width:2px;
    style UI fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
    style Core fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;
    style Rules fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px;
```
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
│   ├── test_calculations.py         # Math Engine & Fallback Invariant Tests
│   └── test_mock_distribution.py         
├── app.py                           # Modular Application Entrypoint
├── loan_master_portfolio_5_buckets.csv # Geographic Mock Data Matrix File
├── requirements.txt                 # Dependency Framework Metrics
└── setup.py                         # Local Editable Packager Configurations
```

---

## 📊 Financial Interest Profiles (`config/constants.py`)

The engine dynamically cross-references the following product interest profile registry inside `core/transformations.py` to drive the monthly reducing-balance backtrace calculations:

| Product Group (`LAN_PDT`) | Annual Interest Rate | Security Status | Default System Behaviour & Invariants |
| :--- | :---: | :--- | :--- |
| **`GOLD_LOAN`** | **7.50%** | Secured (Asset) | Lowest risk tier. Escalates immediately to public jewelry asset auction past 90 DPD. |
| **`HOME_LOAN`** | **8.67%** | Secured (Mortgage) | Standard residential mortgage interest structure. Verified on Yash Mishr's account. |
| **`VEHICLE_LOAN`** | **10.25%** | Secured (Asset) | Vehicle asset financing rules. Automatically generates matching model tracking chains. |
| **`PERSONAL_LOAN`** | **11.00%** | Unsecured Retail | **System Core Fallback Rate** applied automatically if product tags are missing or blank. |
| **`LAP`** *(Loan Against Property)* | **13.50%** | Secured (Mortgage) | Commercial mortgage risk tier. Verified on Rahul Dravid's account. |
| **`CREDIT_CARD`** | **36.00%** | Unsecured Credit | Highest yield premium line. Revokes interest-free grace periods instantly upon payment defaults. |

---
## 💸 Penalty & Late Fee Tranches (`OVERDUE_CHARGE`)

Mandated late presentation penalties are calculated and applied to the transaction vectors dynamically on the cycle processing date based on the following **Days Past Due (DPD)** milestone limits:

```text
┌───────────────────┬───────────────────┐
│ DPD Threshold Log │ Penalty Charge    │
├───────────────────┼───────────────────┤
│ 0 Days (Current)  │ ₹0                │
│ 1 to 30 Days      │ ₹300              │
│ 31 to 60 Days     │ ₹800              │
│ 61 to 90 Days     │ ₹1,200            │
│ Over 90 Days (NPA)│ ₹2,500            │
└───────────────────┴───────────────────┘
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
