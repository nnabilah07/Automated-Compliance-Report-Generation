# report_data.py
from datetime import datetime

# ==================================================
# NEGERI CODE MAPPING (FOR CLAIM NUMBER FORMAT)
# ==================================================

NEGERI_CODE = {
    "Selangor": "SGR",
    "Johor": "JHR",
    "Pulau Pinang": "PNG",
    "Perak": "PRK",
    "Kedah": "KDH",
    "Perlis": "PLS",
    "Negeri Sembilan": "NSN",
    "Melaka": "MLK",
    "Pahang": "PHG",
    "Terengganu": "TRG",
    "Kelantan": "KTN",
    "Sabah": "SBH",
    "Sarawak": "SWK",
    "Kuala Lumpur": "WPKL",
    "Putrajaya": "WPPJ",
    "Labuan": "WPLB"
}

# ==================================================
# TRIBUNAL CASE INFORMATION
# ==================================================

TRIBUNAL_CASE = {
    "tribunal": "Tribunal Tuntutan Pengguna Malaysia",
    "lokasi_tribunal": "Shah Alam",
    "tarikh_jana": datetime.now().strftime("%d-%m-%Y"),
    "amaun_tuntutan": "RM 12,000.00",
    "dokumen": "Dokumen Sokongan Borang 1",
    "negeri": "Selangor"
}


# ==================================================
# PIHAK TERLIBAT (CLAIMANT & RESPONDENT DETAILS)
# ==================================================
# NOTE: Update these fields with actual claimant/respondent information
# These will appear in the BORANG 1 PDF export

PIHAK_YANG_MENUNTUT = {
    "nama": "Ahmad bin Abdullah",                    # Claimant's full name
    "no_kp": "880515-14-5678",                       # IC/Passport number
    "alamat_1": "No. 12, Jalan Harmoni 3/5",        # Address line 1
    "alamat_2": "Taman Harmoni, 43000 Kajang",      # Address line 2 (city, postcode)
    "no_telefon": "012-345 6789",                   # Phone number
    "email": "ahmad.abdullah@email.com",            # Email address
    "keterangan": "Pemilik unit kediaman"           # Description
}

PENENTANG = {
    "nama": "ABC Development Sdn. Bhd.",            # Respondent/Developer name
    "no_pendaftaran": "201901234567 (123456-A)",    # Company registration number
    "alamat_1": "Level 10, Menara ABC",             # Address line 1
    "alamat_2": "Jalan Sultan Ismail, 50250 KL",   # Address line 2
    "no_telefon": "03-2123 4567",                   # Phone number
    "email": "info@abcdevelopment.com.my",          # Email/Fax
    "keterangan": "Pemaju projek perumahan"         # Description
}


# ==================================================
# BUILD SUMMARY STATISTICS (FROM DASHBOARD STATS)
# ==================================================

def build_summary_stats(stats, defects=None):
    """
    Build structured statistical summary
    Includes overdue count for Tribunal analysis
    """

    overdue_count = 0
    if defects:
        overdue_count = len([d for d in defects if d.get("is_overdue")])

    return {
        "jumlah_kecacatan": stats.get("total", 0),
        "belum_diselesaikan": stats.get("pending", 0),
        "telah_diselesaikan": stats.get("completed", 0),
        "kritikal": stats.get("critical", 0),
        "overdue": overdue_count
    }


# ==================================================
# BUILD DEFECT DETAILS (TABLE → REPORT)
# ==================================================

def build_defect_list(defects, role):
    """
    Convert raw defect data into structured report format.
    Remarks are included ONLY for Homeowner.
    """

    report_defects = []

    for d in defects:
        defect_item = {
            "id_kecacatan": d.get("id"),
            "unit": d.get("unit", "-"),
            "keterangan": d.get("desc", "-"),
            "status": d.get("status", "-"),
            "tarikh_lapor": d.get("reported_date", "-"),
            "tarikh_akhir": d.get("deadline", "-"),
            "tertunggak": "Ya" if d.get("is_overdue") else "Tidak",
            "hda_compliance_30_hari": "Ya" if d.get("hda_compliant") else "Tidak",
            "keutamaan": d.get("urgency", "Normal"),
            "bukti_imej": f"evidence/defect_{d.get('id')}.jpg"
        }

        # Only Homeowner sees remarks
        if role == "Homeowner" and d.get("remarks"):
            defect_item["ulasan"] = d.get("remarks")

        report_defects.append(defect_item)

    return report_defects

# ==================================================
# GENERATE CLAIM NUMBER (NO TUNTUTAN)
# Format: TTPM/SGR/2026/000001
# ==================================================

def generate_no_tuntutan(negeri, running_no):
    tahun = datetime.now().year

    negeri_code = NEGERI_CODE.get(negeri, "UNK")  
    # UNK = Unknown (safety fallback)

    return f"TTPM/{negeri_code}/{tahun}/{running_no:06d}"

# ==================================================
# ROLE CONTEXT (AI GUIDANCE STRUCTURE)
# ==================================================

def build_role_context(role):
    if role == "Homeowner":
        return {
            "tajuk_laporan": "Laporan Tuntutan Kecacatan Defect Liability Period (DLP)",
            "tujuan": (
                "Laporan ini disediakan bagi merumuskan kecacatan yang "
                "berlaku dalam tempoh Defect Liability Period (DLP) "
                "untuk rujukan Tribunal."
            )
        }

    if role == "Developer":
        return {
            "tajuk_laporan": "Laporan Pematuhan Pembaikan Defect Liability Period (DLP)",
            "tujuan": (
                "Laporan ini disediakan untuk menunjukkan status pembaikan "
                "dan pematuhan pemaju terhadap kecacatan yang dilaporkan."
            )
        }

    # Legal / Tribunal
    return {
        "tajuk_laporan": "Laporan Gambaran Keseluruhan Pematuhan Defect Liability Period (DLP)",
        "tujuan": (
            "Laporan ini disediakan sebagai gambaran keseluruhan status "
            "kecacatan dan pematuhan untuk rujukan Tribunal."
        )
    }


# ==================================================
# FINAL REPORT DATA (SEND THIS TO AI)
# ==================================================

def build_report_data(role, defects, stats, running_no=None):

    negeri = TRIBUNAL_CASE["negeri"]

    # If no running number passed → auto generate simple number
    if running_no is None:
        running_no = 1   # temporary default
        # OR use timestamp version:
        # running_no = int(datetime.now().strftime("%H%M%S"))

    no_tuntutan = generate_no_tuntutan(negeri, running_no)

    tribunal_case = TRIBUNAL_CASE.copy()
    tribunal_case["no_tuntutan"] = no_tuntutan
    tribunal_case["kod_negeri"] = NEGERI_CODE.get(negeri, "UNK")

    return {
        "maklumat_kes": tribunal_case,
        "pihak_yang_menuntut": PIHAK_YANG_MENUNTUT,
        "penentang": PENENTANG,
        "konteks_peranan": build_role_context(role),
        "ringkasan_statistik": build_summary_stats(stats, defects),
        "senarai_kecacatan": build_defect_list(defects, role),
        "nota_penting": (
            "Laporan ini dijana oleh sistem sebagai dokumen sokongan "
            "kepada Borang 1 Tribunal Tuntutan Pengguna Malaysia (TTPM)."
        )
    }
