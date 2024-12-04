from flask import Flask, render_template, request, send_file, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from bson import ObjectId
from xhtml2pdf import pisa
from io import BytesIO

app = Flask(__name__)

# Enable CORS for the app
CORS(app)

# MongoDB configuration
app.config["MONGO_URI"] = "mongodb+srv://ramapavy:JfYoTZ25G3xZ13pi@events.j6el4.mongodb.net/events"
mongo = PyMongo(app)

# MongoDB collection
events_collection = mongo.db.events

@app.route('/', methods=['GET'])
def get_event():
    return render_template('index.html')

@app.route('/save-event', methods=['POST'])
def save_event():
    try:
        event_data = request.json
        required_fields = ["association_name", "event_name", "secretary", "convenors", "volunteers"]
        for field in required_fields:
            if field not in event_data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Insert event data into MongoDB
        inserted_id = events_collection.insert_one(event_data).inserted_id
        return jsonify({"message": "Event data saved successfully", "eventID": str(inserted_id)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate-pdf/<event_id>', methods=['GET'])
def generate_pdf(event_id):
    try:
        event_data = events_collection.find_one({"_id": ObjectId(event_id)})
        if not event_data:
            return jsonify({"error": "Event not found"}), 404

        # Render the event data into HTML
        rendered_html = render_template('sample_event.html', data=event_data)

        # Convert HTML to PDF
        pdf_buffer = BytesIO()
        pisa_status = pisa.CreatePDF(BytesIO(rendered_html.encode('utf-8')), pdf_buffer)
        pdf_buffer.seek(0)

        if pisa_status.err:
            return jsonify({"error": "Failed to generate PDF"}), 500

        # Return the generated PDF as a file download
        return send_file(pdf_buffer, as_attachment=True, download_name="event_details.pdf", mimetype="application/pdf")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
