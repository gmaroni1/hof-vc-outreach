import os
import base64
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pickle
from typing import Optional, Dict, Any

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

class GmailService:
    def __init__(self):
        self.service = None
        self.credentials = None
        self.client_config = {
            "web": {
                "client_id": os.getenv('GOOGLE_CLIENT_ID'),
                "client_secret": os.getenv('GOOGLE_CLIENT_SECRET'),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "redirect_uris": [
                    "http://localhost:5001/api/gmail/callback",
                    "https://hof-vc-outreach.onrender.com/api/gmail/callback"
                ]
            }
        }
        
    def get_auth_url(self, state: str = None) -> str:
        """Generate OAuth2 authorization URL"""
        flow = Flow.from_client_config(
            self.client_config,
            scopes=SCOPES,
            redirect_uri=self._get_redirect_uri()
        )
        
        if state:
            flow.state = state
            
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        return auth_url
    
    def handle_callback(self, code: str, state: str = None) -> Dict[str, Any]:
        """Handle OAuth2 callback and save credentials"""
        try:
            flow = Flow.from_client_config(
                self.client_config,
                scopes=SCOPES,
                redirect_uri=self._get_redirect_uri(),
                state=state
            )
            
            # Exchange authorization code for tokens
            flow.fetch_token(code=code)
            
            # Save credentials
            credentials = flow.credentials
            self._save_credentials(credentials)
            
            # Build service
            self.service = build('gmail', 'v1', credentials=credentials)
            
            # Get user's email
            profile = self.service.users().getProfile(userId='me').execute()
            
            return {
                'success': True,
                'email': profile.get('emailAddress'),
                'message': 'Successfully connected to Gmail'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to connect to Gmail'
            }
    
    def send_email(self, to: str, subject: str, body: str, cc: str = None, bcc: str = None) -> Dict[str, Any]:
        """Send email using Gmail API"""
        try:
            # Load credentials
            credentials = self._load_credentials()
            if not credentials:
                return {
                    'success': False,
                    'error': 'Not authenticated',
                    'auth_url': self.get_auth_url()
                }
            
            # Build service
            self.service = build('gmail', 'v1', credentials=credentials)
            
            # Create message
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = subject
            
            if cc:
                message['cc'] = cc
            if bcc:
                message['bcc'] = bcc
                
            # Add body
            message.attach(MIMEText(body, 'plain'))
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send message
            send_message = {
                'raw': raw_message
            }
            
            result = self.service.users().messages().send(
                userId='me',
                body=send_message
            ).execute()
            
            return {
                'success': True,
                'message_id': result['id'],
                'message': 'Email sent successfully'
            }
            
        except HttpError as error:
            print(f'An error occurred: {error}')
            return {
                'success': False,
                'error': str(error),
                'message': 'Failed to send email'
            }
        except Exception as e:
            print(f'Unexpected error: {e}')
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to send email'
            }
    
    def check_auth_status(self) -> Dict[str, Any]:
        """Check if user is authenticated"""
        credentials = self._load_credentials()
        
        if credentials and credentials.valid:
            try:
                service = build('gmail', 'v1', credentials=credentials)
                profile = service.users().getProfile(userId='me').execute()
                return {
                    'authenticated': True,
                    'email': profile.get('emailAddress')
                }
            except:
                pass
                
        return {
            'authenticated': False,
            'auth_url': self.get_auth_url()
        }
    
    def logout(self) -> Dict[str, Any]:
        """Remove stored credentials"""
        try:
            token_path = 'gmail_token.pickle'
            if os.path.exists(token_path):
                os.remove(token_path)
            return {
                'success': True,
                'message': 'Successfully logged out'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_redirect_uri(self) -> str:
        """Get appropriate redirect URI based on environment"""
        if os.getenv('FLASK_ENV') == 'production':
            return 'https://hof-vc-outreach.onrender.com/api/gmail/callback'
        return 'http://localhost:5001/api/gmail/callback'
    
    def _save_credentials(self, credentials: Credentials):
        """Save credentials to file"""
        with open('gmail_token.pickle', 'wb') as token:
            pickle.dump(credentials, token)
    
    def _load_credentials(self) -> Optional[Credentials]:
        """Load credentials from file"""
        try:
            if os.path.exists('gmail_token.pickle'):
                with open('gmail_token.pickle', 'rb') as token:
                    credentials = pickle.load(token)
                    
                # Refresh if expired
                if credentials and credentials.expired and credentials.refresh_token:
                    from google.auth.transport.requests import Request
                    credentials.refresh(Request())
                    self._save_credentials(credentials)
                    
                return credentials
        except Exception as e:
            print(f"Error loading credentials: {e}")
            
        return None 