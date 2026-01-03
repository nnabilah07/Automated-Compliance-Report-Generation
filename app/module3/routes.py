from flask import (
    Blueprint,
    render_template,
    send_file,
    request,
    current_app
)
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
from datetime import datetime
import os

# --------------------------------
# IMPORT DUMMY DATA
# --------------------------------
from dummy_data import get_defects_for_role, calculate_stats

# --------------------------------
# CREATE BLUEPRINT
# --------------------------------
routes = Blueprint("routes", __name__)

# =================================================
# DASHBOARD ROUTE (THIS MAKES THE UI OPEN)
# =================================================
@routes.route("/")
def dashboard():
    role = request.args.get("role", "Homeowner")

    defects = get_defects_for_role(role)
    stats = calculate_stats(defects)

    if role == "Homeowner":
        template = "dashboard_homeowner.html"
    elif role == "Developer":
        template = "dashboard_developer.html"
    else:
        template = "dashboard_legal.html"

    return render_template(
        template,
        role=role,
        defects=defects,
        stats=stats
    )

# =================================================
# PDF EXPORT ROUTE
# =================================================
@routes.route("/export_pdf", methods=["POST"])
def export_pdf():
    role = request.form.get("role", "Homeowner")

    defects = get_defects_for_role(role)
    stats = calculate_stats(defects)

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # -------------------------------
    # HEADER
    # -------------------------------
    pdf.setFont("Helvetica-Bold", 16)

    if role == "Legal":
        title = "DLP Full Compliance Report"
        prepared_by = "Legal Officer"
    elif role == "Developer":
        title = "DLP Repair Compliance Report"
        prepared_by = "Developer"
    else:
        title = "DLP Defect Claim Report"
        prepared_by = "Homeowner"

    pdf.drawString(50, height - 50, title)

    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, height - 70, f"Prepared by: {prepared_by}")
    pdf.drawString(
        50,
        height - 85,
        f"Generated on: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
    )

    # -------------------------------
    # SUMMARY
    # -------------------------------
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, height - 120, "Report Summary")

    pdf.setFont("Helvetica", 10)
    pdf.drawString(70, height - 140, f"Total Defects: {stats['total']}")
    pdf.drawString(70, height - 155, f"Pending: {stats['pending']}")
    pdf.drawString(70, height - 170, f"Completed: {stats['completed']}")

    # -------------------------------
    # DEFECT DETAILS
    # -------------------------------
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, height - 200, "Defect Details")

    y = height - 220
    pdf.setFont("Helvetica", 10)

    for defect in defects:

        if y < 160:
            pdf.showPage()
            y = height - 50
            pdf.setFont("Helvetica", 10)

        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(
            50,
            y,
            f"Defect ID: {defect['id']} | Unit: {defect['unit']}"
        )
        y -= 15

        pdf.setFont("Helvetica", 10)
        pdf.drawString(70, y, f"Description: {defect['desc']}")
        y -= 15
        pdf.drawString(70, y, f"Status: {defect['status']}")
        y -= 15

        # Homeowner remark (only for homeowner reports)
        if role == "Homeowner" and defect.get("remarks"):
            pdf.drawString(70, y, f"Remark: {defect['remarks']}")
            y -= 15

        # Optional image evidence
        image_path = defect.get("image")
        if image_path:
            full_path = os.path.join(current_app.root_path, image_path)
            if os.path.exists(full_path):
                img = ImageReader(full_path)
                pdf.drawImage(img, 70, y - 120, width=180, height=120)
                y -= 130

        y -= 10

    # -------------------------------
    # FOOTER
    # -------------------------------
    pdf.setFont("Helvetica-Oblique", 9)
    pdf.drawString(
        50,
        40,
        "This report is system-generated under DLP-CRAM and includes timestamped records for compliance verification."
    )
    pdf.drawString(
        50,
        25,
        "Digital Signature Hash: DLP-CRAM-2025-XYZ123"
    )

    pdf.save()
    buffer.seek(0)

    filename = (
        "dlp_full_compliance_report.pdf"
        if role == "Legal"
        else "dlp_report.pdf"
    )

    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype="application/pdf"
    )

# =================================================
# UPDATE DEFECT STATUS (BACKEND UPDATE)
# =================================================
@routes.route("/update_status", methods=["POST"])
def update_status():
    data = request.json
    defect_id = int(data.get("id"))
    new_status = data.get("status")

    # Since this is dummy data, we update in-memory list
    defects = get_defects_for_role("Developer")  # Developer sees all

    for d in defects:
        if d["id"] == defect_id:
            d["status"] = new_status
            break

    return {
        "status": "success",
        "message": "Defect status updated"
    }

@routes.route("/add_remark", methods=["POST"])
def add_remark():
    data = request.json
    defect_id = int(data["id"])
    remark = data["remark"]

    defects = get_defects_for_role("Developer")

    for d in defects:
        if d["id"] == defect_id:
            d["remarks"] = remark
            break

    return {"status": "success"}
