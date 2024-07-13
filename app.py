from flask import Flask, request, jsonify, send_from_directory
from twilio.rest import Client
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging

# Initialize Flask application
app = Flask(__name__, static_url_path='', static_folder='static')
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins for local development

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables from .env file
load_dotenv()

# Twilio configuration using environment variables
ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
DEVELOPER_PHONE_NUMBER = os.getenv('DEVELOPER_PHONE_NUMBER')

# Initialize Twilio client outside of route handler
client = Client(ACCOUNT_SID, AUTH_TOKEN)

@app.route('/scan', methods=['POST'])
def scan():
    app.logger.info('Request received')
    phone_number = request.form.get('phone_number')
    victim_name = request.form.get('victim_name')
    victim_phone_number = request.form.get('victim_phone_number')
    crime_type = request.form.get('crime_type')
    location = request.form.get('location')
    
    if not location:
        return jsonify({"success": False, "error": "Location is required"}), 400
    
    if phone_number:
        message = f"Phone Number: {phone_number}\nLocation: {location}"
    elif victim_name and victim_phone_number and crime_type:
        message = f"Name: {victim_name}\nPhone Number: {victim_phone_number}\nCrime Type: {crime_type}\nLocation: {location}"
    else:
        return jsonify({"success": False, "error": "All fields are required for victim form"}), 400
    
    try:
        client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=DEVELOPER_PHONE_NUMBER
        )
        return jsonify({"success": True}), 200
    except Exception as e:
        app.logger.error(f'Error processing request: {str(e)}')
        return jsonify({"success": False, "error": str(e)}), 500

# Route to confirm server is running
@app.route('/')
def home():
    return send_from_directory(app.static_folder, 'index.html')

# For deployment on Render.com or similar platforms
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
