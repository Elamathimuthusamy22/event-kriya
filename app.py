from flask import Flask, render_template, request, send_file, jsonify
from flask_pymongo import PyMongo
from bson import ObjectId
from xhtml2pdf import pisa
from io import BytesIO

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
        # Fetch event data from MongoDB
        event_data = events_collection.find_one({"_id": ObjectId(event_id)})
        print("Event data:", event_data)

        if not event_data:
            return jsonify({"error": "Event not found"}), 404
        
        # Render HTML
        rendered_html = render_template('index.html', data=event_data)

        print("Rendered HTML: done")
        # Convert HTML to PDF
        pdf_buffer = BytesIO()
        pisa_status = pisa.CreatePDF(BytesIO(rendered_html.encode('utf-8')), pdf_buffer)
        pdf_buffer.seek(0)
        print("PDF conversion: done")

        if pisa_status.err:
            return jsonify({"error": "Failed to generate PDF"}), 500

        # Send the PDF as response
        return send_file(pdf_buffer, as_attachment=True, download_name="event_details.pdf", mimetype="application/pdf")
    except Exception as e:
        print("Error generating test PDF:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)