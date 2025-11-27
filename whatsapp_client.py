"""
WhatsApp Client Module using Evolution API v2
Handles connection, messaging, and PDF sending to WhatsApp
"""

import os
import requests
import base64
import time

class WhatsAppClient:
    def __init__(self):
        self.base_url = os.environ.get('EVOLUTION_API_URL')
        self.api_key = os.environ.get('EVOLUTION_API_KEY')
        self.instance_name = "garch_bot_instance"
        
        if not self.base_url or not self.api_key:
            print("⚠️ WhatsApp credentials not configured (EVOLUTION_API_URL/KEY)")

    def _get_headers(self):
        return {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }

    def create_instance(self):
        """Create a new WhatsApp instance in Evolution API"""
        try:
            url = f"{self.base_url}/instance/create"
            payload = {
                "instanceName": self.instance_name,
                "integration": "WHATSAPP-BAILEYS",
                "qrcode": True
            }
            response = requests.post(url, json=payload, headers=self._get_headers(), timeout=10)
            
            if response.status_code == 201 or response.status_code == 200:
                return response.json()
            elif response.status_code == 403:
                # Instance already exists, try to restart it
                print(f"⚠️ Instance exists, attempting to restart...")
                restart_url = f"{self.base_url}/instance/restart/{self.instance_name}"
                restart_response = requests.put(restart_url, headers=self._get_headers(), timeout=10)
                return restart_response.json() if restart_response.status_code == 200 else None
            else:
                print(f"❌ Create instance failed: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error creating instance: {e}")
            return None

    def get_qr_code(self, max_attempts=10, wait_seconds=3):
        """Get connection QR code - polls until QR is available"""
        try:
            print(f"🔍 Attempting to get QR for instance: {self.instance_name}")
            
            # First ensure instance exists
            create_result = self.create_instance()
            print(f"📱 Instance creation result: {create_result}")
            
            # Poll for QR code (it may take a few seconds to generate)
            for attempt in range(max_attempts):
                print(f"\n🔄 Attempt {attempt + 1}/{max_attempts}...")
                
                # Check connection status first
                status_url = f"{self.base_url}/instance/connectionState/{self.instance_name}"
                try:
                    status_response = requests.get(status_url, headers=self._get_headers(), timeout=5)
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        print(f"📊 Connection status: {status_data}")
                        
                        # If already connected, no QR needed
                        if isinstance(status_data, dict) and status_data.get('state') == 'open':
                            print("✅ Instance already connected!")
                            return "ALREADY_CONNECTED"
                except Exception as e:
                    print(f"⚠️ Status check failed: {e}")
                
                # Try to get QR from connect endpoint
                connect_url = f"{self.base_url}/instance/connect/{self.instance_name}"
                try:
                    response = requests.get(connect_url, headers=self._get_headers(), timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        print(f"📦 Connect response: {data}")
                        
                        # Check if QR is available
                        if isinstance(data, dict):
                            # Check count field
                            if data.get('count', 0) > 0:
                                # QR should be available, check for base64
                                if 'base64' in data:
                                    print("✅ Found QR code!")
                                    return data['base64']
                                if 'qrcode' in data:
                                    qr_data = data['qrcode']
                                    if isinstance(qr_data, dict) and 'base64' in qr_data:
                                        print("✅ Found QR code in qrcode.base64!")
                                        return qr_data['base64']
                                    elif isinstance(qr_data, str):
                                        print("✅ Found QR code string!")
                                        return qr_data
                            elif data.get('count') == 0:
                                print(f"⏳ QR not ready yet (count=0), waiting {wait_seconds}s...")
                except Exception as e:
                    print(f"⚠️ Connect request failed: {e}")
                
                # Wait before next attempt
                if attempt < max_attempts - 1:
                    time.sleep(wait_seconds)
            
            print("❌ QR code not generated after all attempts")
            print("💡 Possible solutions:")
            print("   1. Check if CONFIG_SESSION_PHONE_VERSION is set in Evolution API")
            print("   2. Restart the Evolution API Docker container")
            print("   3. Check Evolution API logs for errors")
            return None
            
        except Exception as e:
            print(f"❌ Error getting QR: {e}")
            import traceback
            traceback.print_exc()
            return None

    def send_message(self, phone, text):
        """Send text message"""
        if not self.base_url: return None
        
        try:
            url = f"{self.base_url}/message/sendText/{self.instance_name}"
            payload = {
                "number": phone,
                "options": {
                    "delay": 1200,
                    "presence": "composing",
                    "linkPreview": True
                },
                "textMessage": {
                    "text": text
                }
            }
            response = requests.post(url, json=payload, headers=self._get_headers(), timeout=10)
            return response.json()
        except Exception as e:
            print(f"Error sending WhatsApp message: {e}")
            return None

    def send_pdf(self, phone, pdf_url, caption=""):
        """Send PDF document"""
        if not self.base_url: return None
        
        try:
            url = f"{self.base_url}/message/sendMedia/{self.instance_name}"
            payload = {
                "number": phone,
                "options": {
                    "delay": 1200,
                    "presence": "composing"
                },
                "mediaMessage": {
                    "mediatype": "document",
                    "caption": caption,
                    "media": pdf_url,
                    "fileName": "reporte_garch.pdf"
                }
            }
            response = requests.post(url, json=payload, headers=self._get_headers(), timeout=30)
            return response.json()
        except Exception as e:
            print(f"Error sending WhatsApp PDF: {e}")
            return None

# Helper functions for main.py
def get_whatsapp_qr():
    client = WhatsAppClient()
    return client.get_qr_code()

def send_whatsapp_message(text):
    target_number = os.environ.get('WHATSAPP_TARGET_NUMBER')
    if not target_number:
        print("WHATSAPP_TARGET_NUMBER not configured")
        return
        
    client = WhatsAppClient()
    return client.send_message(target_number, text)

def send_whatsapp_pdf(pdf_url, caption=""):
    target_number = os.environ.get('WHATSAPP_TARGET_NUMBER')
    if not target_number: return
        
    client = WhatsAppClient()
    return client.send_pdf(target_number, pdf_url, caption)
