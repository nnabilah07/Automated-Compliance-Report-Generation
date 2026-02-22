# dummy_data.py

from datetime import datetime

# ==================================================
# SIMULATED USERS (FOR ROLE-BASED VIEWS)
# ==================================================

USERS = {
    1: {"name": "Homeowner A", "unit": "A-10-1", "role": "Homeowner"},
    2: {"name": "Homeowner B", "unit": "B-05-2", "role": "Homeowner"},
    3: {"name": "Homeowner C", "unit": "C-01-5", "role": "Homeowner"},
    4: {"name": "Homeowner D", "unit": "D-12-8", "role": "Homeowner"}
}

SIMULATED_LOGIN_USER_ID = 1  # change to test different homeowners


# ==================================================
# FULL MOCK DEFECT DATA (SYSTEM-WIDE)
# ==================================================

all_defects_data = [
    {
        "id": 101,
        "unit": "A-10-1",
        "desc": "Wall crack in master bedroom",
        "reported_date": "2025-12-15",
        "status": "Pending",
        "owner_id": 1,
        "urgency": "High",
        "deadline": "2026-01-13",
        "remarks": "Crack widening slightly over time"
    },
    {
        "id": 102,
        "unit": "B-05-2",
        "desc": "Leaking pipe under kitchen sink",
        "reported_date": "2025-12-18",
        "status": "In Progress",
        "owner_id": 2,
        "urgency": "High",
        "deadline": "2026-01-09",
        "remarks": "Temporary fix applied, replacement pending"
    },
    {
        "id": 103,
        "unit": "A-10-1",
        "desc": "Broken tile in bathroom",
        "reported_date": "2025-12-01",
        "status": "Completed",
        "owner_id": 1,
        "urgency": "Low",
        "deadline": "2025-12-31",
        "remarks": "Tile replaced successfully"
    },
    {
        "id": 104,
        "unit": "C-01-5",
        "desc": "Faulty electrical wiring in living room",
        "reported_date": "2025-12-10",
        "status": "Delayed",
        "owner_id": 3,
        "urgency": "High",
        "deadline": "2026-01-05",
        "remarks": "Contractor unavailable, rescheduled"
    },
    {
        "id": 105,
        "unit": "B-05-2",
        "desc": "Balcony sliding door stuck",
        "reported_date": "2025-12-03",
        "status": "Completed",
        "owner_id": 2,
        "urgency": "Low",
        "deadline": "2026-01-03",
        "remarks": "Roller mechanism adjusted"
    },
    {
        "id": 106,
        "unit": "D-12-8",
        "desc": "Ceiling water stain near air-conditioner",
        "reported_date": "2025-12-20",
        "status": "Pending",
        "owner_id": 4,
        "urgency": "High",
        "deadline": "2026-01-12",
        "remarks": "Inspection scheduled"
    }
]


# ==================================================
# ROLE-BASED DATA ACCESS
# ==================================================

def get_defects_for_role(role):
    """
    Homeowner  → sees only own unit defects
    Developer  → sees all defects
    Legal      → sees all defects (read-only)
    """

    if role == "Homeowner":
        defects = [
            d.copy() for d in all_defects_data
            if d["owner_id"] == SIMULATED_LOGIN_USER_ID
        ]
    else:
        defects = [d.copy() for d in all_defects_data]

    # 🔥 Dynamically calculate compliance fields
    for d in defects:
        d["hda_compliant"] = calculate_hda_compliance(
            d["reported_date"],
            d["deadline"]
        )

        d["is_overdue"] = calculate_overdue(
            d["deadline"],
            d["status"]
        )

    return defects

# ==================================================
# DASHBOARD STATISTICS (DYNAMIC)
# ==================================================

def calculate_stats(defects):
    return {
        "total": len(defects),
        "pending": len([
            d for d in defects
            if d["status"] in ["Pending", "In Progress", "Delayed"]
        ]),
        "completed": len([
            d for d in defects
            if d["status"] == "Completed"
        ]),
        "critical": len([
            d for d in defects
            if d["urgency"] == "High" and not d["hda_compliant"]
        ]),
        "overdue": len([
            d for d in defects
            if d.get("is_overdue")
        ])
    }

# ==================================================
# DATE CALCULATIONS
# ==================================================

def calculate_hda_compliance(reported_date, deadline, allowed_days=30):
    """
    HDA rule: scheduled completion must be within 30 days
    from reported date.
    """
    reported = datetime.strptime(reported_date, "%Y-%m-%d").date()
    due = datetime.strptime(deadline, "%Y-%m-%d").date()
    duration = max((due - reported).days, 0)
    return duration <= allowed_days


def calculate_overdue(deadline, status):
    """
    Overdue if:
    - Today is past deadline
    - AND status is not Completed
    """
    today = datetime.today().date()
    due = datetime.strptime(deadline, "%Y-%m-%d").date()

    if status == "Completed":
        return False

    return today > due