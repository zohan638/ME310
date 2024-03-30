# ME310 Project Repository

Welcome to the ME310-Volvo 2023 Project Repository! 

## Overview

The repository contains several key Python and C++ scripts, used for integrating various sub-systems together running on a RaspberryPi. The key sub-systems here are:
- `Teensy/Actuators`
- `MQTT/WebApp`
- `Camera Server + Droplet Detection`
- ``

### Key Components

- `Controller.py`: Manages the main control flow of the project, coordinating between different modules.
- `Mqtt.py`: Handles MQTT messaging for real-time communication between devices.
- `camsv.html` and `camsv.py`: Work together to facilitate video streaming services.
- `cpp.py`: Contains utility functions used across the project.
- `main.py`: The entry point of the project, initializing and starting the main application.
- `video_feed.cpp`: A C++ file dedicated to managing video feed processing.

### Teensy Folder

The `teensy` folder contains code specifically for the Teensy microcontroller, which is utilized in this project for its high-performance hardware control capabilities.

## Getting Started

To get started with this project, clone this repository to your local machine. Ensure you have Python installed, and install any dependencies listed in the project files.
