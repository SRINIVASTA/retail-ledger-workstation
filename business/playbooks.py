# business/playbooks.py
from dataclasses import dataclass
from config.constants import RISK_TIER_MAPPINGS

@dataclass(frozen=True)
class RegulationAuditPayload:
    bucket_code: str
    risk_classification: str
    playbook_strategy: str

class LoanCollectionsReportEngine:
    """Processes credit parameters to issue actionable default management playbooks."""

    @staticmethod
    def generate_audit_bucket_metadata(row_slice: dict) -> tuple:
        try:
            bucket_val = int(float(row_slice.get('LAN_BKT', 0)))
        except (ValueError, TypeError):
            bucket_val = 0

        if bucket_val == 0:
            return ("BUCKET_0", "STANDARD / PERFORMING ASSET", 
                    "NURTURE / INTERNAL ACCELERATION: Asset portfolio is current. Maintain standard servicing billing operations.")
        elif bucket_val == 1:
            return ("BUCKET_1", "EARLY DELINQUENCY (SMA-0)", 
                    "DIGITAL REMINDER INTERVENTION: Missed current cycle payment date (1-30 DPD). Deploy automated outreach via SMS.")
        elif bucket_val == 2:
            return ("BUCKET_2", "MID DELINQUENCY STRESS (SMA-1)", 
                    "ACTIVE TELE-COLLECTIONS ROUTING: Account is 31-60 DPD overdue. Route file to priority outbound dialing queues.")
        elif bucket_val == 3:
            return ("BUCKET_3", "SEVERE DELINQUENCY PRE-NPA (SMA-2)", 
                    "FIELD AGENT ALLOCATION & VISIT: Account is 61-90 DPD overdue. Initiate doorstep field asset collection procedures.")
        else:
            return ("BUCKET_4", "NON-PERFORMING ASSET (NPA / DEFAULT)", 
                    "LEGAL RECOVERY ACTION: Account exceeds 90 DPD. Suspend active accounts. Initiate asset repossession protocols.")

    @staticmethod
    def extract_field_action_code(row: dict) -> str:
        try:
            bkt = int(row.get("LAN_BKT", 0))
            dpd = int(row.get("LAN_DPD", 0))
            pdt = str(row.get("LAN_PDT", "PERSONAL_LOAN")).strip().upper()
            ecs_per = float(row.get("ECS_SUCCESS_PER", 100))
            max_dpd_3m = int(row.get("MAX_DAY_3M", 0))

            if bkt == 0 and dpd == 0:
                return "PAID_VIA_CLEARING"
            if bkt >= 4 or dpd > 90:
                if pdt == "GOLD_LOAN": return "GOLD_JEWELRY_SENT_TO_PUBLIC_AUCTION"
                if pdt == "VEHICLE_LOAN": return "VEHICLE_SEIZED_GARAGE_AUCTION_LISTED"
                if pdt in ["HOME_LOAN", "LAP"]:
                    return "RECEIVER_APPOINTED_PROPERTY_SEAL_INITIATED" if dpd > 120 else "SARFAESI_POSSESSION_NOTICE_ISSUED"
                return "ARBITRATION_PROCEEDINGS_INITIATED" if max_dpd_3m > 120 else "FINAL_LEGAL_DEMAND_NOTICE"
            if bkt == 3 or (60 < dpd <= 90):
                if pdt in ["HOME_LOAN", "LAP", "VEHICLE_LOAN"]: return "HOUSE_LOCKED_ASSET_REPO_TRIGGERED"
                return "CARD_BLOCKED_EXTERNAL_ASSIGNMENT" if pdt == "CREDIT_CARD" else "LEGAL_SECTIONS_138_NOTICE_SERVED"
            return "FIELD_VISIT_ARRANGED"
        except Exception:
            return "FIELD_VISIT_PENDING"
