import dearpygui.dearpygui as dpg
import os
import threading
import time
from typing import Dict, Optional
from register_device import register_model_and_device
from generate_protos import generate_protos
from assistant_client import GoogleAssistantClient

class AssistantGUI:
    def __init__(self):
        self.assistant: Optional[GoogleAssistantClient] = None
        self.setup_complete = False
        self.setup_status: Dict[str, bool] = {}
        self.command_input = ""
        
        # Initialize DearPyGui
        dpg.create_context()
        dpg.create_viewport(title="Google Assistant Interface", width=1000, height=600)
        dpg.setup_dearpygui()
        
        # Set default theme
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 10, 10)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 5, 5)
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 6, 4)
        
        dpg.bind_theme(global_theme)
        
        self.create_main_window()
        
    def check_setup_status(self) -> Dict[str, bool]:
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
            # Add status to log
            self.add_to_log(f"Checking {file}: {'Found' if required_files[file] else 'Not found'}")
        
        self.setup_status = required_files
        return required_files
    
    def add_to_log(self, message: str):
        """Add message to log with timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        current_log = dpg.get_value("setup_log")
        new_log = f"[{timestamp}] {message}\n{current_log}"
        dpg.set_value("setup_log", new_log)
    
    def update_progress(self, progress: float, message: str = ""):
        """Update progress bar and status message"""
        dpg.set_value("setup_progress", progress)
        if message:
            dpg.set_value("status_text", message)
            self.add_to_log(message)
    
    def run_setup_step(self, step_type: str) -> bool:
        """Run a setup step and show its progress"""
        try:
            self.add_to_log(f"Starting {step_type} step...")
            if step_type == "register":
                self.update_progress(0.5, "Registering device...")
                result = register_model_and_device()
                if result:
                    self.update_progress(1.0, "Device registration complete")
                else:
                    self.update_progress(0.0, "Device registration failed")
                return result
                
            elif step_type == "protos":
                self.update_progress(0.5, "Generating protocol buffers...")
                result = generate_protos()
                if result:
                    self.update_progress(1.0, "Protocol buffers generated")
                else:
                    self.update_progress(0.0, "Protocol buffer generation failed")
                return result
                
            return False
            
        except Exception as e:
            error_msg = f"Error in {step_type}: {str(e)}"
            self.update_progress(0.0, error_msg)
            return False
    
    def create_main_window(self):
        """Create the main application window"""
        with dpg.window(label="Google Assistant Interface", tag="main_window", width=1000, height=600, no_close=True):
            # Setup Status Section
            with dpg.collapsing_header(label="Setup Status", default_open=True):
                # Progress bar
                dpg.add_progress_bar(tag="setup_progress", default_value=0.0, width=-1)
                # Status text
                dpg.add_text("Ready", tag="status_text")
                # Setup log
                dpg.add_input_text(
                    tag="setup_log",
                    multiline=True,
                    readonly=True,
                    width=-1,
                    height=100
                )
                
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label="Check Status",
                        callback=self.update_setup_status,
                        width=120
                    )
                    dpg.add_button(
                        label="Run Setup",
                        callback=self.run_setup_wizard,
                        width=120
                    )
            
            # Command Interface Section
            with dpg.collapsing_header(label="Assistant Interface", default_open=True):
                dpg.add_input_text(
                    label="Command",
                    tag="command_input",
                    width=-1,
                    callback=self.on_command_input
                )
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label="Send",
                        callback=self.send_command,
                        enabled=False,
                        tag="send_button",
                        width=120
                    )
                dpg.add_text("", tag="response_text", wrap=400)
            
            # Example Commands Section
            with dpg.collapsing_header(label="Example Commands", default_open=True):
                example_commands = [
                    "What's the weather like today?",
                    "Tell me a joke",
                    "What time is it?",
                    "What can you do?",
                    "Who are you?",
                    "What's the capital of France?"
                ]
                
                for cmd in example_commands:
                    dpg.add_button(
                        label=cmd,
                        callback=lambda s, a, u: self.set_command(u),
                        user_data=cmd,
                        width=-1
                    )
            
            # Settings Section
            with dpg.collapsing_header(label="Settings", default_open=True):
                dpg.add_button(
                    label="Reset Device Registration",
                    callback=self.reset_registration,
                    width=-1
                )
    
    def update_setup_status(self):
        """Update the setup status display"""
        self.add_to_log("Checking setup status...")
        status = self.check_setup_status()
        
        status_text = "Setup Status Summary:\n"
        all_ready = True
        for file, exists in status.items():
            status_text += f"{'✓' if exists else '✗'} {file}\n"
            if not exists:
                all_ready = False
        
        self.update_progress(1.0 if all_ready else 0.0, status_text)
        
        # Enable/disable interface based on setup status
        self.setup_complete = all_ready
        if self.setup_complete and not self.assistant:
            try:
                self.assistant = GoogleAssistantClient()
                dpg.configure_item("send_button", enabled=True)
                self.add_to_log("Assistant initialized successfully")
            except Exception as e:
                self.add_to_log(f"Failed to initialize assistant: {str(e)}")
        
    def run_setup_wizard(self):
        """Run the setup wizard"""
        def setup_thread():
            self.update_progress(0.0, "Starting setup wizard...")
            status = self.check_setup_status()
            
            # Step 1: Check credentials
            if not status['credentials.json']:
                self.update_progress(0.0, "⚠️ credentials.json not found!\n"
                                       "Please place your Google Cloud credentials file in the application directory.")
                return
            
            # Step 2: Generate Protos
            if not (status['embedded_assistant_pb2.py'] and status['embedded_assistant_pb2_grpc.py']):
                if not self.run_setup_step("protos"):
                    return
            
            # Step 3: Register Device
            if not (status['device_config.json'] and status['token.json']):
                if not self.run_setup_step("register"):
                    return
            
            self.update_progress(1.0, "🎉 Setup completed successfully!")
            self.update_setup_status()
        
        # Run setup in separate thread to avoid blocking GUI
        threading.Thread(target=setup_thread, daemon=True).start()
    
    def on_command_input(self, sender, app_data):
        """Handle command input changes"""
        self.command_input = app_data
    
    def set_command(self, command: str):
        """Set command from example buttons"""
        dpg.set_value("command_input", command)
        self.command_input = command
    
    def send_command(self):
        """Send command to Assistant"""
        if not self.command_input:
            dpg.set_value("response_text", "Please enter a command")
            return
        
        if not self.assistant:
            dpg.set_value("response_text", "Assistant not initialized. Please complete setup first.")
            return
        
        def send_thread():
            try:
                dpg.set_value("response_text", "Processing command...")
                result = self.assistant.send_command(self.command_input)
                dpg.set_value("response_text", "Command processed successfully" if result else "Command failed")
            except Exception as e:
                dpg.set_value("response_text", f"Error: {str(e)}")
        
        # Run command in separate thread to avoid blocking GUI
        threading.Thread(target=send_thread, daemon=True).start()
    
    def reset_registration(self):
        """Reset device registration"""
        try:
            files_to_remove = ['token.json', 'device_config.json']
            for file in files_to_remove:
                if os.path.exists(file):
                    os.remove(file)
            
            status_msg = "Device registration reset! Please run setup again."
            self.update_progress(0.0, status_msg)
            self.setup_complete = False
            self.assistant = None
            dpg.configure_item("send_button", enabled=False)
            self.update_setup_status()
            
        except Exception as e:
            error_msg = f"Error resetting registration: {str(e)}"
            self.update_progress(0.0, error_msg)
    
    def run(self):
        """Run the application"""
        dpg.show_viewport()
        self.update_setup_status()
        
        while dpg.is_dearpygui_running():
            dpg.render_dearpygui_frame()
        
        dpg.destroy_context()

if __name__ == "__main__":
    app = AssistantGUI()
    app.run()