# app.py - UPDATED VERSION with working B2C
from flask import Flask, render_template, jsonify, request
import requests
import base64
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# =============================================
# CONFIGURATION
# =============================================
CONSUMER_KEY = os.getenv('CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')
PASSKEY = os.getenv('PASSKEY', 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919')
SHORTCODE = os.getenv('SHORTCODE', '174379')
CALLBACK_URL = os.getenv('CALLBACK_URL', 'https://macrosporic-osculant-giovani.ngrok-free.dev/api/callback')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'sandbox')

# =============================================
# B2C CONFIGURATION - FIXED VERSION
# =============================================
B2C_INITIATOR_NAME = os.getenv('B2C_INITIATOR_NAME', 'testapi')
B2C_INITIATOR_PASSWORD = os.getenv('B2C_INITIATOR_PASSWORD', 'Safaricom123!')

# Get URLs from environment - NO DEFAULTS WITH PLACEHOLDERS!
B2C_RESULT_URL = os.getenv('B2C_RESULT_URL')
B2C_TIMEOUT_URL = os.getenv('B2C_TIMEOUT_URL')
B2C_QUEUE_TIMEOUT_URL = os.getenv('B2C_QUEUE_TIMEOUT_URL')

# Print B2C configuration on startup
print("\n" + "="*60)
print("🔧 B2C URL CONFIGURATION")
print("="*60)
print(f"B2C_RESULT_URL: {B2C_RESULT_URL}")
print(f"B2C_TIMEOUT_URL: {B2C_TIMEOUT_URL}")
print(f"B2C_QUEUE_TIMEOUT_URL: {B2C_QUEUE_TIMEOUT_URL}")
print("="*60 + "\n")

# Validate B2C URLs
if not all([B2C_RESULT_URL, B2C_TIMEOUT_URL, B2C_QUEUE_TIMEOUT_URL]):
    print("⚠️  WARNING: Some B2C URLs are missing! Check your .env file.")
    print("   B2C payments may fail until these are configured.")

# =============================================
# DARAJA AUTH FUNCTION
# =============================================
def get_access_token():
    """Get OAuth token from Daraja - with debug output"""
    
    print("\n" + "="*50)
    print("🔑 GETTING ACCESS TOKEN")
    print("="*50)
    
    # Check if credentials exist
    if not CONSUMER_KEY or not CONSUMER_SECRET:
        print("❌ ERROR: CONSUMER_KEY or CONSUMER_SECRET is missing!")
        print(f"CONSUMER_KEY exists: {'YES' if CONSUMER_KEY else 'NO'}")
        print(f"CONSUMER_SECRET exists: {'YES' if CONSUMER_SECRET else 'NO'}")
        return None
    
    # Print masked credentials for verification
    print(f"CONSUMER_KEY: {CONSUMER_KEY[:5]}...{CONSUMER_KEY[-5:] if len(CONSUMER_KEY) > 10 else '(too short)'}")
    print(f"CONSUMER_SECRET: {'*' * 8} (length: {len(CONSUMER_SECRET)})")
    print(f"ENVIRONMENT: {ENVIRONMENT}")
    
    if ENVIRONMENT == "sandbox":
        url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    else:
        url = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    
    print(f"URL: {url}")
    
    # Encode credentials
    credentials = f"{CONSUMER_KEY}:{CONSUMER_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    print(f"✓ Credentials encoded (first 20 chars): {encoded_credentials[:20]}...")
    
    headers = {"Authorization": f"Basic {encoded_credentials}"}
    
    try:
        print("📡 Sending request to Daraja...")
        response = requests.get(url, headers=headers, timeout=30)
        
        print(f"📥 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            if token:
                print(f"✅ SUCCESS! Token obtained: {token[:15]}...")
                return token
            else:
                print(f"❌ No access_token in response: {data}")
                return None
        else:
            print(f"❌ HTTP Error {response.status_code}")
            print(f"Response text: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Cannot reach Daraja. Check your internet.")
        return None
    except requests.exceptions.Timeout:
        print("❌ Timeout: Daraja took too long to respond")
        return None
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

# =============================================
# STK PUSH FUNCTION
# =============================================
def generate_password():
    """Generate password for STK Push"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    data_to_encode = SHORTCODE + PASSKEY + timestamp
    password = base64.b64encode(data_to_encode.encode()).decode()
    print(f"✓ Password generated for timestamp: {timestamp}")
    return password, timestamp

def send_stk_push(phone, amount, reference, description):
    """Send STK Push to customer phone with debug"""
    
    print("\n" + "="*50)
    print("🚀 SENDING STK PUSH")
    print("="*50)
    print(f"📱 Phone: {phone}")
    print(f"💰 Amount: {amount}")
    print(f"🏷️ Reference: {reference}")
    print(f"📝 Description: {description}")
    
    # Get access token
    token = get_access_token()
    if not token:
        print("❌ Failed to get access token - aborting STK Push")
        return {"error": "Failed to get access token", "ResponseCode": "1"}
    
    print(f"✓ Token obtained, length: {len(token)}")
    
    # Set URL based on environment
    if ENVIRONMENT == "sandbox":
        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    else:
        url = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    
    print(f"📡 STK Push URL: {url}")
    
    # Generate password and timestamp
    password, timestamp = generate_password()
    
    # Prepare payload
    payload = {
        "BusinessShortCode": SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),  # Ensure amount is integer
        "PartyA": phone,
        "PartyB": SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": CALLBACK_URL,
        "AccountReference": str(reference)[:12],
        "TransactionDesc": str(description)[:13]
    }
    
    print(f"📦 Payload: {payload}")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        print("📤 Sending request to Daraja STK endpoint...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"📥 Response Status: {response.status_code}")
        print(f"📥 Response Body: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ResponseCode') == '0':
                print("✅ STK Push initiated successfully!")
            else:
                print(f"⚠️ STK Push returned code: {result.get('ResponseCode')}")
            return result
        else:
            print(f"❌ HTTP Error {response.status_code}")
            return {
                "error": f"HTTP {response.status_code}", 
                "ResponseCode": "1",
                "ResponseDescription": response.text
            }
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Cannot reach Daraja")
        return {"error": "Connection Error", "ResponseCode": "1"}
    except requests.exceptions.Timeout:
        print("❌ Timeout: Daraja took too long to respond")
        return {"error": "Timeout", "ResponseCode": "1"}
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return {"error": str(e), "ResponseCode": "1"}

# =============================================
# B2C PAYOUT FUNCTION - FIXED
# =============================================
def generate_security_credential(password):
    """
    Generate security credential for B2C
    In sandbox, you can use the password directly
    """
    print(f"🔐 Generating security credential (sandbox mode)")
    return password

def send_b2c_payment(phone, amount, remarks, occasion=""):
    """Send B2C payment to customer"""
    
    print("\n" + "="*50)
    print("💰 SENDING B2C PAYMENT")
    print("="*50)
    print(f"📱 To: {phone}")
    print(f"💰 Amount: {amount}")
    print(f"📝 Remarks: {remarks}")
    
    # Get access token
    token = get_access_token()
    if not token:
        print("❌ Failed to get access token")
        return {"error": "Failed to get access token", "ResponseCode": "1"}
    
    # Set URL based on environment
    if ENVIRONMENT == "sandbox":
        url = "https://sandbox.safaricom.co.ke/mpesa/b2c/v1/paymentrequest"
    else:
        url = "https://api.safaricom.co.ke/mpesa/b2c/v1/paymentrequest"
    
    # Generate security credential
    security_credential = generate_security_credential(B2C_INITIATOR_PASSWORD)
    
    # Prepare payload with validated URLs
    payload = {
        "InitiatorName": B2C_INITIATOR_NAME,
        "SecurityCredential": security_credential,
        "CommandID": "BusinessPayment",
        "Amount": int(amount),
        "PartyA": SHORTCODE,
        "PartyB": phone,
        "Remarks": remarks[:100],
        "QueueTimeOutURL": B2C_QUEUE_TIMEOUT_URL,
        "ResultURL": B2C_RESULT_URL,
        "Occasion": occasion[:100] if occasion else ""
    }
    
    print(f"📦 Payload URLs:")
    print(f"   QueueTimeOutURL: {payload['QueueTimeOutURL']}")
    print(f"   ResultURL: {payload['ResultURL']}")
    print(f"📦 Full Payload: {payload}")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        print("📤 Sending B2C request to Daraja...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"📥 Response Status: {response.status_code}")
        print(f"📥 Response Body: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            return {
                "error": f"HTTP {response.status_code}",
                "ResponseCode": "1",
                "ResponseDescription": response.text
            }
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return {"error": str(e), "ResponseCode": "1"}

# =============================================
# ROUTES
# =============================================

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/test')
def test():
    """Test endpoint to verify API is working"""
    return jsonify({
        "status": "working",
        "message": "M-Pesa Playground is ready!",
        "credentials": {
            "consumer_key_set": bool(CONSUMER_KEY),
            "consumer_secret_set": bool(CONSUMER_SECRET),
            "passkey_set": bool(PASSKEY),
            "environment": ENVIRONMENT
        }
    })

@app.route('/api/c2b/stkpush', methods=['POST'])
def stk_push():
    """Handle STK Push from frontend"""
    
    print("\n" + "="*60)
    print("📨 STK PUSH REQUEST RECEIVED")
    print("="*60)
    
    try:
        data = request.json
        print(f"Request data: {data}")
        
        phone = data.get('phone')
        amount = data.get('amount')
        reference = data.get('reference', 'Test123')
        description = data.get('description', 'Sandbox Payment')
        
        if not phone or not amount:
            print("❌ Missing required fields")
            return jsonify({
                "error": "Phone and amount required",
                "ResponseCode": "1"
            }), 400
        
        print(f"📱 Processing payment: {phone} - KES {amount}")
        
        result = send_stk_push(phone, amount, reference, description)
        
        print("✅ Returning result to frontend")
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Error in stk_push route: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": str(e),
            "ResponseCode": "1"
        }), 500

@app.route('/api/b2c/payout', methods=['POST'])
def b2c_payout():
    """Handle B2C payout from frontend"""
    
    print("\n" + "="*60)
    print("💰 B2C PAYOUT REQUEST RECEIVED")
    print("="*60)
    
    try:
        data = request.json
        print(f"Request data: {data}")
        
        phone = data.get('phone')
        amount = data.get('amount')
        remarks = data.get('remarks', 'Payment')
        occasion = data.get('occasion', '')
        
        if not phone or not amount:
            return jsonify({
                "error": "Phone and amount required",
                "ResponseCode": "1"
            }), 400
        
        # Format phone number
        if phone.startswith('0'):
            phone = '254' + phone[1:]
        elif phone.startswith('7'):
            phone = '254' + phone
        elif phone.startswith('+254'):
            phone = phone[1:]
        
        print(f"📱 Processing B2C payment to: {phone} - KES {amount}")
        
        # Validate URLs before sending
        if not B2C_RESULT_URL or not B2C_QUEUE_TIMEOUT_URL:
            return jsonify({
                "error": "B2C URLs not configured",
                "ResponseCode": "1",
                "ResponseDescription": "Check B2C_RESULT_URL and B2C_QUEUE_TIMEOUT_URL in .env"
            }), 500
        
        result = send_b2c_payment(phone, amount, remarks, occasion)
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Error in b2c_payout route: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": str(e),
            "ResponseCode": "1"
        }), 500

@app.route('/api/b2c/result', methods=['POST'])
def b2c_result():
    """B2C transaction result callback"""
    data = request.json
    print("\n" + "="*50)
    print("📞 B2C RESULT CALLBACK RECEIVED")
    print("="*50)
    print(f"Callback data: {data}")
    return jsonify({"ResultCode": 0, "ResultDesc": "Success"})

@app.route('/api/b2c/timeout', methods=['POST'])
def b2c_timeout():
    """B2C timeout callback"""
    data = request.json
    print("\n" + "="*50)
    print("⏰ B2C TIMEOUT CALLBACK RECEIVED")
    print("="*50)
    print(f"Timeout data: {data}")
    return jsonify({"ResultCode": 0, "ResultDesc": "Success"})

@app.route('/api/callback', methods=['POST'])
def callback():
    """Receive M-Pesa callback"""
    data = request.json
    print("\n" + "="*50)
    print("📞 CALLBACK RECEIVED FROM M-PESA")
    print("="*50)
    print(f"Callback data: {data}")
    return jsonify({"ResultCode": 0, "ResultDesc": "Success"})

@app.route('/api/debug/env', methods=['GET'])
def debug_env():
    """Debug endpoint to check environment variables"""
    return jsonify({
        "consumer_key_set": bool(CONSUMER_KEY),
        "consumer_key_length": len(CONSUMER_KEY) if CONSUMER_KEY else 0,
        "consumer_secret_set": bool(CONSUMER_SECRET),
        "consumer_secret_length": len(CONSUMER_SECRET) if CONSUMER_SECRET else 0,
        "passkey_set": bool(PASSKEY),
        "passkey_length": len(PASSKEY) if PASSKEY else 0,
        "shortcode": SHORTCODE,
        "callback_url": CALLBACK_URL,
        "environment": ENVIRONMENT,
        "b2c_result_url": B2C_RESULT_URL,
        "b2c_timeout_url": B2C_TIMEOUT_URL,
        "b2c_queue_timeout_url": B2C_QUEUE_TIMEOUT_URL
    })

@app.route('/api/debug/b2c-config')
def debug_b2c_config():
    """Debug endpoint to check B2C configuration"""
    return jsonify({
        "B2C_RESULT_URL": B2C_RESULT_URL,
        "B2C_TIMEOUT_URL": B2C_TIMEOUT_URL,
        "B2C_QUEUE_TIMEOUT_URL": B2C_QUEUE_TIMEOUT_URL,
        "CALLBACK_URL": CALLBACK_URL,
        "B2C_INITIATOR_NAME": B2C_INITIATOR_NAME,
        "all_urls_configured": all([B2C_RESULT_URL, B2C_TIMEOUT_URL, B2C_QUEUE_TIMEOUT_URL])
    })

# =============================================
# RUN APP
# =============================================
if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 STARTING M-PESA PLAYGROUND")
    print("="*60)
    
    # Check credentials on startup
    print("\n📋 CONFIGURATION CHECK:")
    print(f"CONSUMER_KEY: {'✅ SET' if CONSUMER_KEY else '❌ MISSING'}")
    print(f"CONSUMER_SECRET: {'✅ SET' if CONSUMER_SECRET else '❌ MISSING'}")
    print(f"PASSKEY: {'✅ SET' if PASSKEY else '❌ MISSING'}")
    print(f"SHORTCODE: {SHORTCODE}")
    print(f"CALLBACK_URL: {CALLBACK_URL}")
    print(f"ENVIRONMENT: {ENVIRONMENT}")
    
    # B2C Configuration Check
    print("\n📋 B2C CONFIGURATION CHECK:")
    print(f"B2C_RESULT_URL: {'✅ SET' if B2C_RESULT_URL else '❌ MISSING'}")
    print(f"B2C_TIMEOUT_URL: {'✅ SET' if B2C_TIMEOUT_URL else '❌ MISSING'}")
    print(f"B2C_QUEUE_TIMEOUT_URL: {'✅ SET' if B2C_QUEUE_TIMEOUT_URL else '❌ MISSING'}")
    print(f"B2C_INITIATOR_NAME: {'✅ SET' if B2C_INITIATOR_NAME else '❌ MISSING'}")
    
    # Test token generation on startup
    print("\n🔑 Testing token generation on startup...")
    token = get_access_token()
    if token:
        print("✅ Token generation successful!")
    else:
        print("❌ Token generation failed - check your credentials")
    
    print("\n📍 Server running at http://127.0.0.1:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000)