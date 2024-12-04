from flask import Flask, render_template,redirect,url_for, request, send_file, jsonify,flash,session
from flask_pymongo import PyMongo
from pymongo import MongoClient
from bson import ObjectId
from xhtml2pdf import pisa
from io import BytesIO

# Flask app
app = Flask(__name__)

app.secret_key = 'xyz1234nbg789ty8inmcv2134' 

# MongoDB configuration
MONGO_URI = "mongodb+srv://Entries:ewp2025@cluster0.1tuj7.mongodb.net/event-kriya?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client["event-kriya"]
event_collection = db["event-entries"] 
workshop_collection = db["workshops"]

@app.route('/')
def home():
    return render_template('home.html')
@app.route('/event-instructions', methods=['GET', 'POST'])
def event_instructions():
    if request.method == 'POST':
        return redirect(url_for('event_detail'))
    return render_template('event_instruction.html')
@app.route('/event-detail', methods=['GET', 'POST'])
def event_detail():
    if request.method == 'POST':
        form_data = {
            "secretary": {
                "name": request.form.get("secretary_name"),
                "roll_number": request.form.get("secretary_roll_number"),
                "mobile": request.form.get("secretary_mobile"),
            },
            "convenor": {
                "name": request.form.get("convenor_name"),
                "roll_number": request.form.get("convenor_roll_number"),
                "mobile": request.form.get("convenor_mobile"),
            },
            "faculty_advisor": {
                "name": request.form.get("faculty_advisor_name"),
                "designation": request.form.get("faculty_advisor_designation"),
                "contact": request.form.get("faculty_advisor_contact"),
            },
            "judge": {
                "name": request.form.get("judge_name"),
                "designation": request.form.get("judge_designation"),
                "contact": request.form.get("judge_contact"),
            }
        }

        try:
            # Check if session has an event ID
            event_id = session.get("event_id")
            if not event_id:
                # Generate a new event ID if not already in session
                existing_event = event_collection.find_one(sort=[("event_id", -1)])
                if existing_event and "event_id" in existing_event:
                    last_event_num = int(existing_event["event_id"][4:])
                    event_id = f"EVNT{last_event_num + 1:02d}"
                else:
                    event_id = "EVNT01"
                session["event_id"] = event_id

            # Upsert to main collection with status "temporary"
            event_collection.update_one(
                {"event_id": event_id},
                {"$set": {"details": form_data, "event_id": event_id, "status": "temporary"}},
                upsert=True
            )
            flash("Event details saved temporarily!")
            return redirect(url_for('event_page'))
        except Exception as e:
            print(f"Error saving event details: {e}")
            flash("An error occurred while saving event details.")
            return redirect(url_for('event_detail'))

    return render_template('event_detail.html')
@app.route('/event', methods=['GET', 'POST'])
def event_page():
    event_id = session.get("event_id")  # Retrieve event_id from session
    if request.method == 'POST':
        # Get the form data and ensure there are no errors when fields are missing
        event_data = {
            "day_1": bool(request.form.get("day_1")),
            "day_2": bool(request.form.get("day_2")),
            "day_3": bool(request.form.get("day_3")),
            "participants": request.form.get("participants", "").strip(),
            "halls_required": request.form.get("halls_required", "").strip(),
            "team_min": request.form.get("team_min", "").strip() if request.form.get("team_min") else None,
            "team_max": request.form.get("team_max", "").strip() if request.form.get("team_max") else None,
        }

        # Check if the required fields are provided and handle missing data appropriately
        if not event_data["participants"] or not event_data["halls_required"]:
            flash("Please fill in all the required fields.")
            return redirect(url_for('event_page'))

        try:
            if event_id:
                event_collection.update_one({"event_id": event_id}, {"$set": {"event": event_data}})
                flash("Event details updated successfully!")
            else:
                flash("Error: Event ID not found in session.")
                return redirect(url_for('event_detail'))

        except Exception as e:
            print(f"Error saving event data to MongoDB: {e}")
            flash("An error occurred while updating event details. Please try again.")

        return redirect(url_for('items_page'))

    return render_template('event.html')
@app.route('/items', methods=['GET', 'POST'])
def items_page():
    event_id = session.get("event_id")  # Retrieve event_id from session

    if request.method == 'POST':
        # Retrieve item details from the form
        items_data = {
            "sno": request.form.get("sno"),
            "item_name": request.form.get("item_name"),
            "quantity": request.form.get("quantity"),
            "price_per_unit": request.form.get("price_per_unit"),
            "total_price": request.form.get("total_price"),
        }

        # Validate required fields
        if not items_data["item_name"] or not items_data["quantity"]:
            flash("Item name and quantity are required.")
            return jsonify({"success": False, "message": "Item name and quantity are required."}), 400

        try:
            if event_id:
                # Add the item details to the event in MongoDB
                event_collection.update_one({"event_id": event_id}, {"$push": {"items": items_data}})
                flash("Item details saved successfully!")
                return render_template('confirm.html', event_id=event_id)
            else:
                flash("Error: Event ID not found in session.")
                return redirect(url_for('event_detail'))
        except Exception as e:
            print(f"Error saving item data to MongoDB: {e}")
            flash("An error occurred while saving item details. Please try again.")
            return redirect(url_for('items_page'))

    return render_template('items.html')
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
        inserted_id = event_collection.insert_one(event_data).inserted_id

        return jsonify({"message": "Event data saved successfully", "id": str(inserted_id)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to retrieve event data from MongoDB and generate a PDF
@app.route('/generate-pdf/<event_id>', methods=['GET'])
def generate_pdf(event_id):
    try:
        # Fetch event data from MongoDB
        event_data = event_collection.find_one({"_id": ObjectId(event_id)})
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
    app.run(debug=True, port=9000)
