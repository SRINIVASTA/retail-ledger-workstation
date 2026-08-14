# collections_engine.py
from dataclasses import dataclass

@dataclass
class BucketPlaybook:
    bucket_id: int
    stage_name: str
    risk_level: str  # Safe, Low, Medium, High, Critical
    ui_color: str    # Hex code matching alert rules
    tag_name: str    # Behavioral action keyword
    message: str
    strategy_action: str

class LoanCollectionsEngine:
    """
    Evaluates loan delinquency metrics and generates point-of-collection 
    behavioral playbooks and operational nudges.
    """

    @classmethod
    def get_playbook(cls, row_slice: dict) -> BucketPlaybook:
        # Safely extract and evaluate the collection bucket value
        try:
            bucket_val = int(row_slice.get('LAN_BKT', 0))
        except (ValueError, TypeError):
            bucket_val = 0

        # BUCKET 0: Fully Performing Asset
        if bucket_val == 0:
            return BucketPlaybook(
                bucket_id=0,
                stage_name="Bucket 0: Fully Performing Asset",
                risk_level="Safe / Normal",
                ui_color="#2E7D32", # Green
                tag_name="GROWTH",
                message="🟢 This loan is completely current. Account behavior is healthy.",
                strategy_action="Account is safe. High priority candidate for pre-approved multi-product top-ups, gold loans, or interest rate drops."
            )

        # BUCKET 1: Early Delinquency
        elif bucket_val == 1:
            return BucketPlaybook(
                bucket_id=1,
                stage_name="Bucket 1: Early Delinquency (SMA-0)",
                risk_level="Low Risk",
                ui_color="#1976D2", # Blue
                tag_name="SOFT NUDGE",
                message="🔵 Missed current cycle billing installment. 1-30 Days Past Due.",
                strategy_action="Send automated digital nudges (WhatsApp/SMS links). Trigger soft IVR voice drops. Likely a payroll cycle mismatch."
            )

        # BUCKET 2: Mid-Tier Delinquency
        elif bucket_val == 2:
            return BucketPlaybook(
                bucket_id=2,
                stage_name="Bucket 2: Early Stress Delinquency (SMA-1)",
                risk_level="Medium Risk",
                ui_color="#EF6C00", # Orange
                tag_name="INTENSE CALLING",
                message="🟠 Consecutive second cycle bouncing. 31-60 Days Past Due.",
                strategy_action="Route file to live outbound tele-calling desks. Lock in a formal Promise-to-Pay (PTP) date with follow-up confirmation."
            )

        # BUCKET 3: Hard Delinquency Cliff
        elif bucket_val == 3:
            return BucketPlaybook(
                bucket_id=3,
                stage_name="Bucket 3: Severe Delinquency (SMA-2)",
                risk_level="High Risk",
                ui_color="#C62828", # Dark Orange/Red
                tag_name="FIELD DEPLOYMENT",
                message="🔴 Pre-NPA Warning Threshold. 61-90 Days Past Due.",
                strategy_action="Deploy designated area field agents for a direct doorstep visit. Initiate financial restructuring or loan-term extension talks."
            )

        # BUCKET 4: Non-Performing Asset Default
        else:
            return BucketPlaybook(
                bucket_id=4,
                stage_name="Bucket 4: Non-Performing Asset (NPA / Default)",
                risk_level="CRITICAL / DEFAULT",
                ui_color="#B71C1C", # Deep Crimson
                tag_name="LEGAL RECOVERY",
                message="💀 Permanent Impairment. Over 90 Days Past Due.",
                strategy_action="Freeze credit limits across all connected products. Issue formal legal notices, pull collateral records, or clear for repo settlement."
            )
