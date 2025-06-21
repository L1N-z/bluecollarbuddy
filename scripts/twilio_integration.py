import os
import json
from datetime import datetime
from typing import Dict, List, Optional

class TwilioWhatsAppIntegration:
    def __init__(self, account_sid: str = None, auth_token: str = None, phone_number: str = None):
        self.account_sid = account_sid or os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = auth_token or os.getenv('TWILIO_AUTH_TOKEN')
        self.phone_number = phone_number or os.getenv('TWILIO_PHONE_NUMBER')
        
        if not all([self.account_sid, self.auth_token, self.phone_number]):
            raise ValueError("Missing required Twilio credentials")
    
    def send_message(self, to: str, message: str) -> Dict[str, any]:
        """Send a WhatsApp message using Twilio API"""
        import requests
        import base64
        
        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"
        
        # Prepare authentication
        auth_string = f"{self.account_sid}:{self.auth_token}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        headers = {
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'From': self.phone_number,
            'To': to,
            'Body': message
        }
        
        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            
            result = response.json()
            print(f"Message sent successfully. SID: {result.get('sid')}")
            
            return {
                'success': True,
                'message_sid': result.get('sid'),
                'status': result.get('status'),
                'timestamp': datetime.now().isoformat()
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to send message: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_message_status(self, message_sid: str) -> Dict[str, any]:
        """Get the status of a sent message"""
        import requests
        import base64
        
        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages/{message_sid}.json"
        
        auth_string = f"{self.account_sid}:{self.auth_token}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        headers = {
            'Authorization': f'Basic {auth_b64}'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            return {
                'success': True,
                'status': result.get('status'),
                'error_code': result.get('error_code'),
                'error_message': result.get('error_message'),
                'date_sent': result.get('date_sent'),
                'date_updated': result.get('date_updated')
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_media_message(self, to: str, message: str, media_url: str) -> Dict[str, any]:
        """Send a WhatsApp message with media attachment"""
        import requests
        import base64
        
        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"
        
        auth_string = f"{self.account_sid}:{self.auth_token}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        headers = {
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'From': self.phone_number,
            'To': to,
            'Body': message,
            'MediaUrl': media_url
        }
        
        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            
            result = response.json()
            return {
                'success': True,
                'message_sid': result.get('sid'),
                'status': result.get('status')
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e)
            }

# Example usage and testing
if __name__ == "__main__":
    # Initialize the integration
    try:
        twilio = TwilioWhatsAppIntegration()
        
        # Test sending a message
        test_number = "whatsapp:+1234567890"  # Replace with actual test number
        test_message = "Hello! This is a test message from your WhatsApp agent."
        
        result = twilio.send_message(test_number, test_message)
        print(f"Send result: {json.dumps(result, indent=2)}")
        
        # If message was sent successfully, check its status
        if result.get('success') and result.get('message_sid'):
            import time
            time.sleep(2)  # Wait a moment before checking status
            
            status_result = twilio.get_message_status(result['message_sid'])
            print(f"Status result: {json.dumps(status_result, indent=2)}")
            
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please set the following environment variables:")
        print("- TWILIO_ACCOUNT_SID")
        print("- TWILIO_AUTH_TOKEN") 
        print("- TWILIO_PHONE_NUMBER")
