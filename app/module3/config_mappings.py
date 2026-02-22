# config_mappings.py

# ======================================
# STATUS NORMALISATION (ALWAYS → ENGLISH)
# ======================================
STATUS_NORMALISE = {
    "Belum Diselesaikan": "Pending",
    "Dalam Tindakan": "In Progress",
    "Telah Diselesaikan": "Completed",
    "Tertangguh": "Delayed",
}

# ======================================
# STATUS TRANSLATION (FOR DISPLAY)
# ======================================
STATUS_TRANSLATION = {
    "ms": {
        "Pending": "Belum Diselesaikan",
        "In Progress": "Dalam Tindakan",
        "Completed": "Telah Diselesaikan",
        "Delayed": "Tertangguh",
    },
    "en": {
        "Belum Diselesaikan": "Pending",
        "Dalam Tindakan": "In Progress",
        "Telah Diselesaikan": "Completed",
        "Tertangguh": "Delayed",
    }
}

# ======================================
# PRIORITY TRANSLATION
# ======================================
PRIORITY_TRANSLATION = {
    "ms": {
        "High": "Tinggi",
        "Medium": "Sederhana",
        "Low": "Rendah",
    },
    "en": {
        "Tinggi": "High",
        "Sederhana": "Medium",
        "Rendah": "Low",
    }
}
