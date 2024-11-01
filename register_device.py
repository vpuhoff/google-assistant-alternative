# register_device.py
import json
import os
from pathlib import Path
import google.auth.transport.requests
import google.oauth2.credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import subprocess
import sys

def install_requirements():
    """Install required packages"""
    packages = [
        'google-assistant-sdk[samples]',
        'google-auth-oauthlib',
        'google-auth-httplib2',
        'google-assistant-grpc',
        'grpcio'
    ]
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package])
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to install {package}: {e}")

def get_project_id():
    """Get project ID from credentials file"""
    with open('credentials.json', 'r') as f:
        creds = json.load(f)
        return creds['installed']['project_id']

def authenticate():
    """Authenticate using OAuth"""
    SCOPES = ['https://www.googleapis.com/auth/assistant-sdk-prototype']
    creds = None

    if os.path.exists('token.json'):
        try:
            with open('token.json', 'r') as f:
                token_data = json.load(f)
                
            with open('credentials.json', 'r') as f:
                cred_data = json.load(f)
                
            creds = google.oauth2.credentials.Credentials(
                token=token_data.get('token'),
                refresh_token=token_data.get('refresh_token'),
                token_uri=cred_data['installed']['token_uri'],
                client_id=cred_data['installed']['client_id'],
                client_secret=cred_data['installed']['client_secret'],
                scopes=SCOPES
            )
        except Exception as e:
            print(f"Error loading saved credentials: {e}")
            if os.path.exists('token.json'):
                os.remove('token.json')
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        token_data = {
            'token': creds.token,
            'refresh_token': creds.refresh_token
        }
        with open('token.json', 'w') as f:
            json.dump(token_data, f)

    return creds

def register_model_and_device():
    """Register model and device using command line tools"""
    try:
        print("Installing requirements...")
        install_requirements()
        
        print("Getting project ID...")
        project_id = get_project_id()
        print(f"Project ID: {project_id}")
        
        print("Authenticating...")
        credentials = authenticate()
        if not credentials:
            print("Failed to authenticate")
            return False
            
        # Create the device configuration
        model_id = f'assistant-model-{project_id}'
        device_id = f'assistant-device-{project_id}'
        
        config = {
            'device_model_id': model_id,
            'device_id': device_id,
            'project_id': project_id
        }
        
        # Save the configuration
        with open('device_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print("\nDevice configuration created successfully!")
        print(f"Model ID: {model_id}")
        print(f"Device ID: {device_id}")
        print("\nConfiguration saved to device_config.json")
        
        return True
        
    except Exception as e:
        print(f"Error during registration: {e}")
        return False

if __name__ == '__main__':
    if register_model_and_device():
        print("\nSetup completed successfully!")
    else:
        print("\nSetup failed. Please check the errors above and try again.")