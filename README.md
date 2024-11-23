# Sphero RVR Autonomous Kit (Python)

This repository contains Python code for the SparkFun Advanced Autonomous Kit, designed to run on a Raspberry Pi and control the Sphero RVR.

## Getting Started

### Prerequisites
To ensure the code runs correctly, you need to compile the Protocol Buffers file used in the project. Follow these steps:

1. Install the Protocol Buffers compiler (`protoc`). For installation instructions, refer to the [official gRPC documentation](https://grpc.io/docs/protoc-installation/).

2. Compile the `message.proto` file:
   ```bash
   protoc --python_out=protobuf/ protobuf/message.proto
   ```
    Run this command from the root of the project directory.

## Running the Code

After compiling the Protocol Buffers file, you can execute the main script:

```bash
python main.py
```

Ensure that all dependencies are installed and the Raspberry Pi is properly set up to interface with the Sphero RVR.
