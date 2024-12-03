from flask import Flask, request, jsonify, send_file
from flask_pymongo import PyMongo
from bson import ObjectId
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter, PdfMerger

# Flask app
app = Flask(__name__)

# MongoDB configuration
app.config["MONGO_URI"] = "mongodb+srv://ramapavy:JfYoTZ25G3xZ13pi@events.j6el4.mongodb.net/events"
mongo = PyMongo(app)

# MongoDB collections
events_collection = mongo.db.events

# Route to save event data into MongoDB
@app.route('/save-event', methods=['POST'])
def save_event():
    try:
        # Get JSON data from the request
        event_data = request.json

        # Validate required fields
        required_fields = ["association_name", "event_name"]
        for field in required_fields:
            if field not in event_data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Insert event data into MongoDB
        inserted_id = events_collection.insert_one(event_data).inserted_id

        return jsonify({"message": "Event data saved successfully", "id": str(inserted_id)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to retrieve event data from MongoDB and generate a PDF
@app.route('/generate-pdf/<event_id>', methods=['GET'])
def generate_pdf(event_id):
    try:
        # Retrieve event data from MongoDB
        event_data = events_collection.find_one({"_id": ObjectId(event_id)})

        if not event_data:
            return jsonify({"error": "Event not found"}), 404

        # Create a buffer to hold the overlay PDF
        buffer = BytesIO()

        # Generate overlay PDF using reportlab
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Add form data to the PDF dynamically
        c.setFont("Helvetica", 12)
        y = height - 100  # Starting Y position
        line_height = 20

        c.drawString(50, y, f"Association Name: {event_data.get('association_name', '')}")
        y -= line_height
        c.drawString(50, y, f"Event Name: {event_data.get('event_name', '')}")
        y -= line_height

        # Secretary details
        c.drawString(50, y, "Secretary Details:")
        y -= line_height
        for name, roll, mobile in zip(
            event_data.get("secretary_name", []),
            event_data.get("secretary_roll", []),
            event_data.get("secretary_mobile", []),
        ):
            c.drawString(70, y, f"Name: {name}, Roll: {roll}, Mobile: {mobile}")
            y -= line_height

        # Convenor details
        c.drawString(50, y, "Convenor Details:")
        y -= line_height
        for name, roll, mobile in zip(
            event_data.get("convenor_name", []),
            event_data.get("convenor_roll", []),
            event_data.get("convenor_mobile", []),
        ):
            c.drawString(70, y, f"Name: {name}, Roll: {roll}, Mobile: {mobile}")
            y -= line_height

        # Volunteer details
        c.drawString(50, y, "Volunteer Details:")
        y -= line_height
        for name, roll, mobile in zip(
            event_data.get("volunteer_name", []),
            event_data.get("volunteer_roll", []),
            event_data.get("volunteer_mobile", []),
        ):
            c.drawString(70, y, f"Name: {name}, Roll: {roll}, Mobile: {mobile}")
            y -= line_height

        c.save()

        # Load the original template PDF
        template_pdf_path = "KRIYA_2K24_ERM_PP[1].pdf"
        original_pdf = PdfReader(template_pdf_path)

        # Load the generated overlay
        buffer.seek(0)
        overlay_pdf = PdfReader(buffer)

        # Merge the overlay onto the original template
        writer = PdfWriter()
        for page in original_pdf.pages:
            overlay_page = overlay_pdf.pages[0]  # Use the first page of overlay
            page.merge_page(overlay_page)
            writer.add_page(page)

        # Save the merged PDF to a buffer
        output_buffer = BytesIO()
        writer.write(output_buffer)
        output_buffer.seek(0)

        # Send the final PDF as response
        return send_file(
            output_buffer,
            as_attachment=True,
            download_name="filled_form.pdf",
            mimetype="application/pdf",
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
