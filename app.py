from flask import Flask, request, jsonify
from flask_cors import CORS
from twilio.rest import Client
import random
import time
import os

app = Flask(__name__)
CORS(app)

otp_store = {}
OTP_EXPIRY_SECONDS = 300  # 5 minutes

# Twilio credentials from environment variables
TWILIO_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE = os.getenv('TWILIO_PHONE_NUMBER')
client = Client(TWILIO_SID, TWILIO_AUTH)

@app.route('/send_otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    phone = data.get('phone')

    if not phone:
        return jsonify({'status': 'error', 'message': 'Phone number is required'}), 400

    otp = str(random.randint(100000, 999999))
    otp_store[phone] = {'otp': otp, 'timestamp': time.time()}

    try:
        message = client.messages.create(
            body=f"Your OTP is {otp}",
            from_=TWILIO_PHONE,
            to=phone
        )
        return jsonify({'status': 'success', 'message': 'OTP sent successfully'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    phone = data.get('phone')
    otp_input = data.get('otp')

    record = otp_store.get(phone)
    if not record:
        return jsonify({'status': 'error', 'message': 'No OTP found for this number'}), 400

    if time.time() - record['timestamp'] > OTP_EXPIRY_SECONDS:
        return jsonify({'status': 'error', 'message': 'OTP expired'}), 400

    if record['otp'] != otp_input:
        return jsonify({'status': 'error', 'message': 'Incorrect OTP'}), 400

    del otp_store[phone]
    return jsonify({'status': 'success', 'message': 'OTP verified successfully'}), 200

@app.route('/', methods=['GET'])
def home():
    return "OTP API is running!", 200
