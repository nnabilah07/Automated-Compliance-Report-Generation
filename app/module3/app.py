from flask import Flask, render_template, request, send_file, jsonify
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io
from datetime import datetime

# -------------------------------
# CREATE FLASK APP INSTANCE
# -------------------------------
app = Flask(__name__)

# =====================================================================
# MOCK DATABASE & AI SERVICE
# =====================================================================

all_defects_data = [
    {"id": 101, "unit": "A-10-1", "desc": "Wall crack in master bedroom", "status": "Pending", "owner_id": 1},
    {"id": 102, "unit": "B-05-2", "desc": "Leaking pipe in kitchen", "status": "In Progress", "owner_id": 2},
    {"id": 103, "unit": "A-10-1", "desc": "Broken tile in bathroom", "status": "Completed", "owner_id": 1},
    {"id": 104, "unit": "C-01-5", "desc": "Faulty wiring in living room", "status": "Pending", "owner_id": 3},
    {"id": 105, "unit": "B-05-2", "desc": "Stuck balcony door", "status": "Completed", "owner_id": 2},
]

def get_defects_for_role(role):
    """Filters defects based on user role."""
    user_id = 1  # simulate Homeowner login
    if role == 'Homeowner':
        return [d for d in all_defects_data if d['owner_id'] == user_id]
    return all_defects_data  # Developer & Legal see all

def mock_ai_generate_narrative(defect_desc):
    """Simulates AI narrative generation."""
    return f"AI Analysis: The reported '{defect_desc}' has been analyzed. Severity: Moderate. Recommended action: Immediate inspection by a qualified technician."

# =====================================================================
# ROUTES
# =====================================================================

@app.route("/")
def dashboard():
    role = request.args.get("role", "Homeowner")
    defects = get_defects_for_role(role)

    stats = {
        "total": len(defects),
        "pending": len([d for d in defects if d['status'] in ['Pending', 'In Progress']]),
        "completed": len([d for d in defects if d['status'] == 'Completed'])
    }

    # Render the correct template based on role
    if role == "Homeowner":
        template = "dashboard_homeowner.html"
    elif role == "Developer":
        template = "dashboard_developer.html"
    else:  # Legal/Admin
        template = "dashboard_legal.html"

    return render_template(template, defects=defects, stats=stats, role=role)


@app.route("/generate_report", methods=['POST'])
def generate_report():
    role = request.args.get("role", "Homeowner")
    defects = get_defects_for_role(role)

    report_type = "Generic Report"
    if role == 'Homeowner': 
        report_type = "Defect Claim Report"
    elif role == 'Developer': 
        report_type = "Repair Compliance Report"
    else: 
        report_type = "Full Compliance Report"

    report_metadata = {
        "report_type": report_type,
        "generated_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "digital_signature_hash": "a1b2c3d4e5_MOCK_SIGNATURE"
    }

    return jsonify({"metadata": report_metadata, "content": defects, "status": "success"})


@app.route('/ai_narrative', methods=['POST'])
def ai_narrative():
    data = request.json
    description = data.get('description', '')
    narrative = mock_ai_generate_narrative(description)
    return jsonify({"ai_narrative": narrative})


@app.route('/add_remark', methods=['POST'])
def add_remark():
    # Mock endpoint
    return jsonify({"status": "success", "message": "Note added successfully."})


@app.route("/export_pdf", methods=["POST"])
def export_pdf():
    role = request.form.get("role", "Homeowner")  # Use POST form data
    defects = get_defects_for_role(role)

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Draw header
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, height - 50, "DLP Compliance Report")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, height - 70, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    pdf.drawString(50, height - 85, f"Report for: {role}")

    # Table header
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, height - 110, "ID")
    pdf.drawString(100, height - 110, "Unit")
    pdf.drawString(200, height - 110, "Description")
    pdf.drawString(450, height - 110, "Status")
    pdf.line(50, height - 115, width - 50, height - 115)

    y = height - 130
    pdf.setFont("Helvetica", 11)
    for d in defects:
        if y < 50:
            pdf.showPage()
            pdf.setFont("Helvetica-Bold", 18)
            pdf.drawString(50, height - 50, "DLP Compliance Report")
            pdf.setFont("Helvetica", 10)
            pdf.drawString(50, height - 70, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            pdf.drawString(50, height - 85, f"Report for: {role}")
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(50, height - 110, "ID")
            pdf.drawString(100, height - 110, "Unit")
            pdf.drawString(200, height - 110, "Description")
            pdf.drawString(450, height - 110, "Status")
            pdf.line(50, height - 115, width - 50, height - 115)
            y = height - 130
            pdf.setFont("Helvetica", 11)

        pdf.drawString(50, y, str(d["id"]))
        pdf.drawString(100, y, d["unit"])
        pdf.drawString(200, y, d["desc"])
        pdf.drawString(450, y, d["status"])
        y -= 20

    pdf.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="dlp_report.pdf", mimetype="application/pdf")


if __name__ == "__main__":
    app.run(debug=True)
