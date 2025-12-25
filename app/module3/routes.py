from flask import Flask, send_file, request
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/export_pdf', methods=['POST'])
def export_pdf():
    role = request.form.get('role', 'Homeowner')

    # Mock data (same as before)
    stats = {'total': 5, 'pending': 2, 'completed': 3}
    defects = [
        {
            'id': 1,
            'unit': 'A-101',
            'desc': 'Leaking pipe in bathroom',
            'status': 'Pending',
            'remark': 'Check junction and seal',
            'image': 'static/mock_image1.png'
        },
        {
            'id': 2,
            'unit': 'A-102',
            'desc': 'Cracked wall in living room',
            'status': 'Completed',
            'remark': 'Repaired on 15/12/2025',
            'image': 'static/mock_image2.png'
        }
    ]

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # ======================
    # HEADER
    # ======================
    pdf.setFont("Helvetica-Bold", 16)

    if role == "Legal":
        pdf.drawString(50, height - 50, "DLP Full Compliance Report")
        prepared_by = "Legal Officer"
    else:
        pdf.drawString(50, height - 50, "DLP Defect Claim Report")
        prepared_by = "Homeowner"

    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, height - 70, f"Prepared by: {prepared_by}")
    pdf.drawString(50, height - 85,
                   f"Generated on: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    # ======================
    # SUMMARY
    # ======================
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, height - 120, "Report Summary")

    pdf.setFont("Helvetica", 10)
    pdf.drawString(70, height - 140, f"Total Defects: {stats['total']}")
    pdf.drawString(70, height - 155, f"Pending: {stats['pending']}")
    pdf.drawString(70, height - 170, f"Completed: {stats['completed']}")

    # ======================
    # DEFECT DETAILS
    # ======================
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, height - 200, "Defect Details")

    y = height - 220
    pdf.setFont("Helvetica", 10)

    for defect in defects:
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(50, y, f"Defect ID: {defect['id']}  |  Unit: {defect['unit']}")
        y -= 15

        pdf.setFont("Helvetica", 10)
        pdf.drawString(70, y, f"Description: {defect['desc']}")
        y -= 15
        pdf.drawString(70, y, f"Status: {defect['status']}")
        y -= 15

        # Homeowner remarks (ONLY for homeowner report)
        if role == "Homeowner":
            pdf.drawString(70, y, f"Remark: {defect['remark']}")
            y -= 15

        # Evidence image (allowed for both roles)
        image_path = os.path.join(app.root_path, defect['image'])
        if os.path.exists(image_path):
            img = ImageReader(image_path)
            pdf.drawImage(img, 70, y - 120, width=180, height=120)
            y -= 130
        else:
            pdf.drawString(70, y, "No image evidence provided")
            y -= 15

        y -= 10

        if y < 120:
            pdf.showPage()
            y = height - 50

    # ======================
    # FOOTER / LEGAL METADATA
    # ======================
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

    filename = "dlp_report.pdf" if role == "Homeowner" else "dlp_full_compliance_report.pdf"

    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype="application/pdf"
    )
