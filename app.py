from flask import Flask, request, send_file
from io import BytesIO
from pdfrw import PdfReader, PdfWriter, PageMerge, PdfDict

app = Flask(__name__)

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    try:
        # Parse form data from the request
        form_data = request.json

        # Debugging: Print received form data
        print("Received Form Data:", form_data)

        # Load the existing PDF
        pdf_path = "KRIYA_2K24_ERM_PP[1].pdf"  # Ensure this exists
        template_pdf = PdfReader(pdf_path)
        output_pdf = PdfWriter()

        # Field Mapping (Update with your actual PDF field names)
        field_mapping = {
            "ASSOCIATION_NAME": form_data.get("association_name", ""),
            "EVENT_NAME": form_data.get("event_name", ""),
            "SECRETARY_NAME": ", ".join(form_data.get("secretary_name", [])),
            "SECRETARY_ROLL": ", ".join(form_data.get("secretary_roll", [])),
            "SECRETARY_MOBILE": ", ".join(form_data.get("secretary_mobile", [])),
            "CONVENOR_NAME": ", ".join(form_data.get("convenor_name", [])),
            "CONVENOR_ROLL": ", ".join(form_data.get("convenor_roll", [])),
            "CONVENOR_MOBILE": ", ".join(form_data.get("convenor_mobile", [])),
            "VOLUNTEER_NAME": ", ".join(form_data.get("volunteer_name", [])),
            "VOLUNTEER_ROLL": ", ".join(form_data.get("volunteer_roll", [])),
            "VOLUNTEER_MOBILE": ", ".join(form_data.get("volunteer_mobile", [])),
        }

        # Fill form fields
        for page in template_pdf.pages:
            annotations = page.Annots
            if annotations:
                for annotation in annotations:
                    field_name = annotation.T[1:-1]  # Remove parentheses around field name
                    if field_name in field_mapping:
                        annotation.update(PdfDict(V=field_mapping[field_name]))

            # Add page to output
            output_pdf.addpage(page)

        # Save the updated PDF to memory buffer
        buffer = BytesIO()
        output_pdf.write(buffer)
        buffer.seek(0)

        # Send the updated PDF as response
        return send_file(buffer, as_attachment=True, download_name="filled_form.pdf", mimetype="application/pdf")

    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
