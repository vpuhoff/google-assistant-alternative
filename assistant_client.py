# assistant_client.py
import os
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

import json
import wave
import pyaudio
import google.auth.transport.requests
import google.oauth2.credentials
import grpc
from google_auth_oauthlib.flow import InstalledAppFlow
from google.assistant.embedded.v1alpha2 import (
    embedded_assistant_pb2,
    embedded_assistant_pb2_grpc
)

class GoogleAssistantClient:
    def __init__(self):
        self.credentials_path = 'credentials.json'
        self.token_path = 'token.json'
        self.device_config_path = 'device_config.json'
        self.api_endpoint = 'embeddedassistant.googleapis.com'
        self.language_code = 'en-US'
        self.SCOPES = ['https://www.googleapis.com/auth/assistant-sdk-prototype']
        
        # Audio settings
        self.audio = pyaudio.PyAudio()
        
        # Load device config
        if not os.path.exists(self.device_config_path):
            raise Exception("Device configuration not found. Please run register_device.py first")
            
        with open(self.device_config_path, 'r') as f:
            config = json.load(f)
            self.device_model_id = config['device_model_id']
            self.device_id = config['device_id']
            #print(f"Loaded device config: model_id={self.device_model_id}, device_id={self.device_id}")

    def play_audio(self, audio_data):
        """Play audio response"""
        try:
            # Configure audio stream
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                output=True
            )
            
            # Play audio
            stream.write(audio_data)
            
            # Cleanup
            stream.stop_stream()
            stream.close()
            
        except Exception as e:
            print(f"Error playing audio: {e}")

    def authenticate(self):
        credentials = None
        
        if os.path.exists(self.token_path):
            try:
                with open(self.token_path, 'r') as f:
                    token_data = json.load(f)
                    
                with open(self.credentials_path, 'r') as f:
                    cred_data = json.load(f)
                    
                credentials = google.oauth2.credentials.Credentials(
                    token=token_data.get('token'),
                    refresh_token=token_data.get('refresh_token'),
                    token_uri=cred_data['installed']['token_uri'],
                    client_id=cred_data['installed']['client_id'],
                    client_secret=cred_data['installed']['client_secret'],
                    scopes=self.SCOPES
                )
            except Exception as e:
                print(f"Error loading credentials: {e}")
                credentials = None

        if not credentials or not credentials.valid:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path,
                    scopes=self.SCOPES
                )
                credentials = flow.run_local_server(port=0)
                
                token_data = {
                    'token': credentials.token,
                    'refresh_token': credentials.refresh_token
                }
                with open(self.token_path, 'w') as f:
                    json.dump(token_data, f)
            except Exception as e:
                print(f"Error during authentication: {e}")
                raise

        return credentials

    def send_command(self, command):
        """Send command and play audio response"""
        try:
            credentials = self.authenticate()
            
            channel_credentials = grpc.ssl_channel_credentials()
            auth_credentials = grpc.metadata_call_credentials(
                lambda context, callback: callback([
                    ('authorization', f'Bearer {credentials.token}')
                ], None)
            )
            
            composite_credentials = grpc.composite_channel_credentials(
                channel_credentials, auth_credentials
            )
            
            with grpc.secure_channel(self.api_endpoint, composite_credentials) as channel:
                assistant = embedded_assistant_pb2_grpc.EmbeddedAssistantStub(channel)
                
                config = embedded_assistant_pb2.AssistConfig(
                    text_query=command,
                    audio_out_config=embedded_assistant_pb2.AudioOutConfig(
                        encoding=1,  # LINEAR16
                        sample_rate_hertz=16000,
                        volume_percentage=100,
                    ),
                    dialog_state_in=embedded_assistant_pb2.DialogStateIn(
                        language_code=self.language_code,
                        conversation_state=b'',
                        is_new_conversation=True
                    ),
                    device_config=embedded_assistant_pb2.DeviceConfig(
                        device_id=self.device_id,
                        device_model_id=self.device_model_id
                    )
                )
                
                request = embedded_assistant_pb2.AssistRequest(config=config)
                responses = assistant.Assist(iter([request]))
                
                print("Processing responses...")
                audio_data = b''
                
                for response in responses:
                    if response.audio_out.audio_data:
                        audio_data += response.audio_out.audio_data
                
                if audio_data:
                    print("Playing audio response...")
                    self.play_audio(audio_data)
                    return True
                else:
                    print("No audio response received")
                    return False
                    
        except Exception as e:
            print(f"Error during command execution: {e}")
            if hasattr(e, 'details'):
                print(f"Error details: {e.details()}")
            return False

    def cleanup(self):
        """Cleanup audio resources"""
        self.audio.terminate()

def main():
    try:
        print("Initializing Google Assistant Client...")
        assistant = GoogleAssistantClient()
        
        try:
            while True:
                command = input("\nEnter your command (or 'exit' to quit): ")
                
                if command.lower() == 'exit':
                    break
                    
                print("\nSending command to Assistant...")
                assistant.send_command(command)
                
        finally:
            assistant.cleanup()
            
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
        print("\nTry removing token.json and running register_device.py again if authentication fails.")

if __name__ == '__main__':
    main()