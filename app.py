import streamlit as st
import os
from register_device import register_model_and_device
from generate_protos import generate_protos
from assistant_client import GoogleAssistantClient

def check_setup_status():
    """Check if all required files exist"""
    required_files = {
        'credentials.json': False,
        'device_config.json': False,
        'token.json': False,
        'embedded_assistant_pb2.py': False,
        'embedded_assistant_pb2_grpc.py': False
    }
    
    for file in required_files:
        required_files[file] = os.path.exists(file)
    
    return required_files

def run_setup_step(step_type, message):
    """Run a setup step and show its progress"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    status_text.text(f"Running: {message}")
    
    try:
        if step_type == "register":
            status_text.text("Starting device registration...")
            if register_model_and_device():
                progress_bar.progress(1.0)
                status_text.text(f"✅ Completed: {message}")
                return True
            else:
                status_text.text(f"❌ Failed: {message}")
                return False
                
        elif step_type == "protos":
            status_text.text("Generating protocol buffers...")
            if generate_protos():
                progress_bar.progress(1.0)
                status_text.text(f"✅ Completed: {message}")
                return True
            else:
                status_text.text(f"❌ Failed: {message}")
                return False
                
    except Exception as e:
        status_text.text(f"❌ Failed: {message}")
        st.error(f"Error: {e}")
        return False

def setup_wizard():
    """Setup wizard for first-time configuration"""
    st.title("Google Assistant Setup Wizard")
    
    setup_status = check_setup_status()
    
    # Step 1: Check credentials
    st.header("Step 1: Google Cloud Credentials")
    if not setup_status['credentials.json']:
        st.warning("⚠️ credentials.json not found!")
        st.markdown("""
        Please follow these steps to get your credentials:
        1. Go to [Google Cloud Console](https://console.cloud.google.com)
        2. Create a new project or select existing one
        3. Enable Google Assistant API
        4. Configure OAuth consent screen
        5. Create OAuth 2.0 Client ID (Desktop app)
        6. Download the JSON file and rename it to `credentials.json`
        7. Place the file in the same directory as this application
        """)
        return False
    else:
        st.success("✅ credentials.json found!")
    
    # Step 2: Generate Protos
    st.header("Step 2: Generate Protocol Buffers")
    if not (setup_status['embedded_assistant_pb2.py'] and setup_status['embedded_assistant_pb2_grpc.py']):
        if st.button("Generate Protos"):
            if run_setup_step("protos", "Generating protocol buffers"):
                setup_status['embedded_assistant_pb2.py'] = True
                setup_status['embedded_assistant_pb2_grpc.py'] = True
            else:
                return False
    else:
        st.success("✅ Protocol buffers already generated!")
    
    # Step 3: Register Device
    st.header("Step 3: Register Device")
    if not (setup_status['device_config.json'] and setup_status['token.json']):
        if st.button("Register Device"):
            if run_setup_step("register", "Registering device"):
                setup_status['device_config.json'] = True
                setup_status['token.json'] = True
            else:
                return False
    else:
        st.success("✅ Device already registered!")
    
    # Check if all setup is complete
    if all(setup_status.values()):
        st.success("🎉 Setup completed successfully!")
        return True
    
    return False

class AssistantInterface:
    def __init__(self):
        self.assistant = GoogleAssistantClient()
        
    def send_command(self, command):
        """Send command to Assistant"""
        try:
            with st.spinner("Processing command..."):
                result = self.assistant.send_command(command)
                return result
        except Exception as e:
            st.error(f"Error: {e}")
            return False

def handle_command(assistant, command):
    """Handle command input and execution"""
    if command:
        assistant.send_command(command)

def main():
    st.set_page_config(
        page_title="Google Assistant Interface",
        page_icon="🎙️",
        layout="wide"
    )
    
    # Initialize session state for command input
    if 'command_input' not in st.session_state:
        st.session_state.command_input = ''
    
    # Check if setup is complete
    setup_status = check_setup_status()
    
    if not all(setup_status.values()):
        if not setup_wizard():
            return
        
    # Main interface
    st.title("🎙️ Google Assistant Interface")
    
    assistant = AssistantInterface()
    
    # Command input with Enter key handling
    command = st.text_input(
        "Enter your command:",
        key="command_input",
        on_change=handle_command,
        args=(assistant, st.session_state.command_input,)
    )
    
    col1, col2 = st.columns([1, 6])
    
    with col1:
        if st.button("Send", key="send_button"):
            if command:
                handle_command(assistant, command)
            else:
                st.warning("Please enter a command")
    
    # Example commands
    with st.sidebar:
        st.success("Connected to Google Assistant")
        
        st.subheader("Example Commands")
        example_commands = [
            "What's the weather like today?",
            "Tell me a joke",
            "What time is it?",
            "What can you do?",
            "Who are you?",
            "What's the capital of France?"
        ]
        
        for cmd in example_commands:
            if st.button(cmd, key=f"cmd_{cmd}"):
                handle_command(assistant, cmd)
    
        # Settings
        st.subheader("Settings")
        if st.button("Reset Device Registration"):
            try:
                files_to_remove = ['token.json', 'device_config.json']
                for file in files_to_remove:
                    if os.path.exists(file):
                        os.remove(file)
                st.success("Device registration reset! Please refresh the page.")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Error resetting registration: {e}")

if __name__ == "__main__":
    main()