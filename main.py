from Mqtt import MQTTClient
from Controller import Control
from cpp import Detection
from camsv import CameraStream
import time
import argparse
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Input Arguments")
    parser.add_argument("--ip", type=str, help="IP address", default = "192.168.42.1")
    parser.add_argument("--port", type=int, help="Port number", default = 9001)
    parser.add_argument("--serial_port", type=str, help="Serial port", default="/dev/ttyS0")
    parser.add_argument("--baud", type=str, help="Baud Rate", default=9600)
    parser.add_argument("--cam_id", type=str, help="Camera Device ID", default=0)
    parser.add_argument("--cam_port", type=str, help="Camera Feed Port", default=5000)
    parser.add_argument("--cam_handle", type=str, help="URL Handle for Camera Feed", default="/single_image")

    args = parser.parse_args()
    ip_address = args.ip
    port = args.port
    serial_port = args.serial_port
    baud_rate = args.baud
    cam_id = args.cam_id
    cam_port = args.cam_port
    cam_handle = args.cam_handle

    #------------------------------------ CONNECT TO MQTT ------------------------------------#

    # Create an instance of MQTTClient
    mqtt_client = MQTTClient(ip_address, port)

    # Connect to the MQTT broker
    mqtt_client.connect()
    
    #------------------------------------ CONTROL SYSTEM ------------------------------------#

    # Create instance of control logic
    controller = Control()

    # Initiate Spin and Alert counters
    S = 0
    ALERT = 0
    alert_counter = 0

    # Connect to Micro-controller
    ser = controller.connect_to_serial(serial_port, baud_rate)

    # Setting up GPIO
    controller.initialize_GPIO()

    # Start Camera Server
    stream = CameraStream(cam_id, cam_port, cam_handle)
    stream.disable_flask_logging()
    stream.run()
    time.sleep(5)
    
    # Start Detection Script
    detection = Detection(cam_port, cam_handle)
    detection.run()

    try:
        while True:

            # CAM = Camera.get_dirty()        # Some function to read camera SW: 0=clear, 1=blury
            # RS = Rain.get_state()           # Some function to read rain sens: 0=no rain, 1=rain
            latest_output = detection.get_latest_output()
            if latest_output > 6:
                CAM = 1
            else:
                CAM = 0
            
            RS = 0

            AUTO = mqtt_client.AUTO
            SPEED = mqtt_client.SPEED

            if AUTO == 1:                                   # IF THE MESSAGE IS 1 WE ARE IN AUTOMATIC MODE AND DO STATE BASED CONTROL
                # S = Arduino.speed                         # READ IF SPINNING OR NOT FROM ARDUINO
                S = controller.S
                state = controller.state(RS, CAM, S)
                controller.logic(state)
                
                alert_counter = controller.alert_counter
                
                if alert_counter == 5:
                    AUTO = 2
                    
            elif AUTO == 0:                                 # Manual mode: the user specifies if to spin and at what speed through MQTT (SPEED: 0=No, 1=50%, 2=100%)     
                if SPEED == 0:
                    #arduino.speed(0)                       # no spinning of both
                    controller.ser.flushOutput()
                    controller.ser.flushInput()
                    controller.ser.write(str(0).encode())
                    # time.sleep(.1)
                    try:
                        message = int(controller.ser.readline().strip().decode('utf-8'))
                        print(f"Motor speed returned: {message}%")
                        mqtt_client.publish_message("DryveSystem1/RPi_return", str(f"Motor speed returned: {message}%"))
                    except:
                        print("Error detected")
                        mqtt_client.publish_message("DryveSystem1/RPi_return", f"Error detected")

                elif SPEED == 1:
                    #arduino.speed(50%)                     # spinning at 50% and air burst
                    controller.ser.flushOutput()
                    controller.ser.flushInput()
                    controller.ser.write(str(27).encode())
                    # time.sleep(.1)
                    try:
                        message = int(controller.ser.readline().strip().decode('utf-8'))
                        print(f"Motor speed returned: {message}%")
                        mqtt_client.publish_message("DryveSystem1/RPi_return", f"Motor speed returned: {message}%")
                    except:
                        print("Error detected")
                        mqtt_client.publish_message("DryveSystem1/RPi_return", f"Error detected")

                elif SPEED == 2:
                    #arduino.speed(100%)                    # spinning at max and continuous air
                    controller.ser.flushOutput()
                    controller.ser.flushInput()
                    controller.ser.write(str(25).encode())
                    # time.sleep(.1)
                    try:
                        message = int(controller.ser.readline().strip().decode('utf-8'))
                        print(f"Motor speed returned: {message}%")
                        mqtt_client.publish_message("DryveSystem1/RPi_return", f"Motor speed returned: {message}%")
                    except:
                        print("Error detected")
                        mqtt_client.publish_message("DryveSystem1/RPi_return", f"Error detected")

            elif AUTO == 2:                                 # the user requests the truck to PARK
                # flash LED
                controller.ser.flushOutput()
                controller.ser.flushInput()
                controller.set_pin(True)
                # time.sleep(.1)
                try:
                    message = int(controller.ser.readline().strip().decode('utf-8'))
                    print(f"Motor speed returned: {message}%")
                    mqtt_client.publish_message("DryveSystem1/RPi_return", f"Motor speed returned: {message}%")
                except:
                    print("Error detected")
                    mqtt_client.publish_message("DryveSystem1/RPi_return", f"Error detected")
                time.sleep(3)
                print("Done Parking!")
                mqtt_client.publish_message("DryveSystem1/RPi_return", f"Done Parking!")
                controller.set_pin(False)

                # Publish values for variables RS, CAM, Alert and Spin to MQTT
                # mqtt_client.publish_message("DryveSystem1/RS", RS)
                # mqtt_client.publish_message("DryveSystem1/CAM", CAM)
                # mqtt_client.publish_message("DryveSystem1/ALERT", ALERT)  
                # mqtt_client.publish_message("DryveSystem1/S", S)              # TO ADD TO TELL USER IF WE'RE CLEANING OR NOT  

                # print(AUTO)
                # print(SPEED)
                # print(ALERT)

    except KeyboardInterrupt:
        print("Exitting...")
        time.sleep(2)

    except:
        print("Failure")

    finally:
        # Close Serial
        controller.disconnect_serial()

        # Release GPIO
        controller.disconnect_GPIO()
        
        # Disconnect from the MQTT broker
        mqtt_client.disconnect()
        print("Clean up!")
    
    