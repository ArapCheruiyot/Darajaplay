# simple_test.py
import requests
import base64

# PASTE YOUR ACTUAL CREDENTIALS HERE (from developer portal)
CONSUMER_KEY=CONSUMER_KEY = "3fI0iUI6PRFGuxkXuLuGEUJC1GooXjuleTz7GdRM3nMiGKZa"
CONSUMER_SECRET="wbfr5CfG011inEy7StAxWnPiymuWJ9dzsxgdoz6bKrJqcUv2v98CjvOAp1whLAGI"

print("="*50)
print("SIMPLE DARAJA AUTH TEST")
print("="*50)

# Encode credentials
credentials = f"{CONSUMER_KEY}:{CONSUMER_SECRET}"
encoded = base64.b64encode(credentials.encode()).decode()

headers = {"Authorization": f"Basic {encoded}"}
url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

print(f"URL: {url}")
print(f"Authorization: Basic {encoded[:20]}...")

try:
    print("\n📡 Sending request...")
    response = requests.get(url, headers=headers, timeout=10)
    
    print(f"✅ Status Code: {response.status_code}")
    print(f"📥 Response Headers: {dict(response.headers)}")
    print(f"📥 Raw Response: '{response.text}'")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"\n✅ JSON Response: {data}")
            if 'access_token' in data:
                print(f"\n🎉 SUCCESS! Token: {data['access_token'][:20]}...")
            else:
                print("\n❌ No access_token in response")
        except:
            print("\n❌ Response is not valid JSON")
    else:
        print(f"\n❌ HTTP Error {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("\n❌ Connection Error: Cannot reach Daraja. Check your internet.")
except requests.exceptions.Timeout:
    print("\n❌ Timeout: Daraja took too long to respond")
except Exception as e:
    print(f"\n❌ Error: {str(e)}")