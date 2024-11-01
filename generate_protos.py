# generate_protos.py
import os
import subprocess
import sys
from pathlib import Path

def install_requirements():
    """Install required packages"""
    packages = [
        'grpcio-tools',
        'google-assistant-grpc',
        'google-auth-oauthlib',
        'google-auth-httplib2',
        'google-assistant-sdk[samples]',
        'protobuf'
    ]
    
    print("Installing/upgrading required packages...")
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package])
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to install {package}: {e}")

def check_installations():
    """Check installed packages"""
    try:
        import grpc
        print(f"gRPC version: {grpc.__version__}")
        
        import grpc_tools
        print("gRPC tools installed successfully")
        
        import google.auth
        print("Google auth installed successfully")
        
        import google.assistant.embedded
        print("Google Assistant SDK installed successfully")
        
    except ImportError as e:
        print(f"Error importing package: {e}")
        return False
    
    return True

def generate_proto_file():
    """Generate the proto file"""
    proto_content = '''syntax = "proto3";

package google.assistant.embedded.v1alpha2;

// Embedded Assistant API
service EmbeddedAssistant {
    // Initiates or continues a conversation with the embedded Assistant Service.
    rpc Assist(stream AssistRequest) returns (stream AssistResponse) {}
}

message AssistRequest {
    oneof type {
        AssistConfig config = 1;
        bytes audio_in = 2;
    }
}

message AssistResponse {
    oneof type {
        bytes audio_out = 1;
        bytes device_action = 2;
        bytes device_state = 3;
    }
    DialogStateOut dialog_state_out = 5;
    string error_message = 6;
}

message AssistConfig {
    AudioInConfig audio_in_config = 1;
    AudioOutConfig audio_out_config = 2;
    DialogStateIn dialog_state_in = 3;
    DeviceConfig device_config = 4;
    string text_query = 5;
}

message AudioInConfig {
    Encoding encoding = 1;
    int32 sample_rate_hertz = 2;
}

message AudioOutConfig {
    Encoding encoding = 1;
    int32 sample_rate_hertz = 2;
    int32 volume_percentage = 3;
}

enum Encoding {
    ENCODING_UNSPECIFIED = 0;
    LINEAR16 = 1;
    FLAC = 2;
    MP3 = 3;
}

message DialogStateIn {
    string language_code = 1;
    bytes conversation_state = 2;
    bool is_new_conversation = 3;
}

message DialogStateOut {
    bytes conversation_state = 1;
    string supplemental_display_text = 2;
    string transcript = 3;
}

message DeviceConfig {
    string device_id = 1;
    string device_model_id = 2;
}'''

    # Create directory structure
    os.makedirs('google/assistant/embedded/v1alpha2', exist_ok=True)

    proto_path = 'google/assistant/embedded/v1alpha2/embedded_assistant.proto'
    with open(proto_path, 'w') as f:
        f.write(proto_content)

    return proto_path

def compile_proto(proto_path):
    """Compile proto file using protoc command"""
    try:
        from grpc_tools import protoc
        
        # Get the current directory
        current_dir = os.getcwd()
        
        print(f"Compiling proto file: {proto_path}")
        print(f"Output directory: {current_dir}")
        
        result = protoc.main([
            'grpc_tools.protoc',
            f'-I{current_dir}',
            f'--python_out={current_dir}',
            f'--grpc_python_out={current_dir}',
            proto_path
        ])
        
        if result != 0:
            raise Exception(f"protoc returned non-zero exit status: {result}")
            
        return True
        
    except Exception as e:
        print(f"Error during proto compilation: {e}")
        return False

def move_generated_files():
    """Move generated files to current directory"""
    try:
        source_dir = 'google/assistant/embedded/v1alpha2'
        files_moved = False
        
        for file in os.listdir(source_dir):
            if file.endswith('_pb2.py') or file.endswith('_pb2_grpc.py'):
                source_path = os.path.join(source_dir, file)
                if os.path.exists(file):
                    os.remove(file)
                os.rename(source_path, file)
                files_moved = True
                print(f"Moved {file} to current directory")
        
        if not files_moved:
            raise Exception("No proto files were generated")
        
        # Clean up temporary directory
        import shutil
        shutil.rmtree('google')
        
        return True
        
    except Exception as e:
        print(f"Error moving generated files: {e}")
        return False

def generate_protos():
    """Generate Python files from proto"""
    try:
        print("\nStep 1: Installing requirements...")
        install_requirements()

        print("\nStep 2: Checking installations...")
        if not check_installations():
            return False

        print("\nStep 3: Generating proto file...")
        proto_path = generate_proto_file()

        print("\nStep 4: Compiling proto files...")
        if not compile_proto(proto_path):
            return False

        print("\nStep 5: Moving generated files...")
        if not move_generated_files():
            return False

        print("\nProto files generated successfully!")
        print("Generated files:")
        for file in os.listdir('.'):
            if file.endswith('_pb2.py') or file.endswith('_pb2_grpc.py'):
                print(f"- {file}")
        return True

    except Exception as e:
        print(f"\nError during proto generation: {e}")
        return False

if __name__ == '__main__':
    print("Starting proto generation process...")
    if generate_protos():
        print("\nSetup completed successfully!")
    else:
        print("\nSetup failed. Please check the errors above and try again.")