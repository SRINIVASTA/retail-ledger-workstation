# 📊 CreditPulse AI — Multi-Product Retail Ledger Workstation

An interactive financial analytics dashboard designed to process retail portfolio ledger profiles, track risk regulatory buckets, run backend calculation diagnostic tests, and audit specific customer accounts.

🔗 **Live App:** [retail-ledger-workstation.streamlit.app](https://retail-ledger-workstation-5peipbcvl6qgjdtmksklyn.streamlit.app/)

---

## 📂 Project Structure

* `.github/workflows/` — Automated CI/CD pipelines
* `app.py` — Streamlit interactive frontend dashboard & components
* `engine.py` — Core ledger processing & cross-product balance calculations
* `collections_engine.py` — Delinquency risk bucketing & playbook strategy logic
* `test_engine.py` — PyTest suite verifying backend calculation precision
* `requirements.txt` — Project dependencies
* `LICENSE` — Open-source MIT License

---

## ⚙️ Core Workflow & Learning Map

The project dashboard breaks down the retail accounting pipeline into three functional phases to help learners understand ledger state operations:

### 1. Data Injection
* Uploads the raw portfolio portfolio ledger dataset (e.g., `loan_buckets.csv`).
* Automatically maps active accounts into standardized risk allocations (**Bucket 0** through **Bucket 4**).

### 2. Workspace Filtering & Analytics
* Filters active records by **Product Category** (e.g., `PERSONAL_LOAN`, `CREDIT_CARD`, `VEHICLE_LOAN`, `HOME_LOAN`, `GOLD_LOAN`, `LAP`).
* Dynamic search by customer name, unique ID (`UCIC`), or loan file number.
* Interactive cross-product visual aids (e.g., *Reconciled Capital Exposure Share* pie chart breakdowns).

### 3. System Verification
* Built-in diagnostic validations checking mathematical consistency across headers.
* Ensures the internal math rules powering the engine are 100% accurate.

---

## 🚀 Setup & Installation

### 1. Install Dependencies
Clone the repository, navigate into your project folder, and install requirements:
```bash
pip install -r requirements.txt
```

### 2. Run the Dashboard
Launch the interface locally to test workflows:
```bash
streamlit run app.py
```

### 3. Run Calculations Diagnostics
Execute the underlying automated unit tests to confirm the backend math performs as expected:
```bash
pytest test_engine.py
```
