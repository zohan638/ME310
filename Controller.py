import RPi.GPIO as GPIO
import time
import serial

class Control:
    def __init__(self):
        self.S = 0
        self.alert_counter = 0
        self.int_pin = 23
        self.ser = None
        self.stateval = 1

    #----------------------------- CONNECT TO MICRO-CONTROLLER ------------------------------#

    def connect_to_serial(self, serial_port, baudrate):
        while True:
            print("Connecting...")
            try:
                self.ser = serial.Serial(serial_port, baudrate)
                print(f"[done] Serial connection successful! Return: {self.ser.isOpen()}")
                break
            
            except serial.SerialException:
                print("Failed to connect to serial device. Retrying in 5 seconds...")
                time.sleep(5)
        return self.ser
    
    def disconnect_serial(self):
        # Close Serial
        self.ser.close()
    
    #------------------------------------ RPi GPIO SETUP -------------------------------------#

    def initialize_GPIO(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.int_pin, GPIO.OUT)
        self.set_pin(False)
    
    def set_pin(self, val=False):
        GPIO.output(self.int_pin, val)

    def disconnect_GPIO(self):
        # Release GPIO
        GPIO.cleanup()

    def state(self, RS, CAM, S):
        switch = {
            (0, 0, 0): 1,
            (0, 0, 1): 2,
            (0, 1, 0): 3,
            (0, 1, 1): 4,
            (1, 0, 0): 5,
            (1, 0, 1): 6,
            (1, 1, 0): 7,
            (1, 1, 1): 8,
        }
        return switch.get((RS, CAM, S), None)

    def logic(self, state):
        """
        0% -> off
        25% -> blast
        27% -> continuous air
        """
        if state == 1:
            ### Do nothing
            if self.stateval != state:
                self.ser.flushOutput()
                self.ser.flushInput()
                self.ser.write(str(0).encode())
                time.sleep(.1)
                try:
                    print(f"Motor speed returned: {int(self.ser.readline().strip().decode('utf-8'))}%")
                except:
                    print("Error detected")
            self.S = 0
            self.alert_counter = 0
        elif state == 2:
            # Arduino.speed.Motor1()          # spin visor motor
            # Arduino.speed.Motor2()          # BLAST air every 10s
            # Arduino.wait("10s")             # wait 10s
            if self.stateval != state:
                self.ser.flushOutput()
                self.ser.flushInput()
                self.ser.write(str(25).encode())
                time.sleep(.1)
                try:
                    print(f"Motor speed returned: {int(self.ser.readline().strip().decode('utf-8'))}%")
                except:
                    print("Error detected")
            self.S = 0
            self.alert_counter = 0
        elif state == 3:
            # Arduino.speed.Motor1(0)          # NO visor motor
            # Arduino.speed.Motor2(0)          # NO air 
            if self.stateval != state:
                self.ser.flushOutput()
                self.ser.flushInput()
                self.ser.write(str(0).encode())
                time.sleep(.1)
                try:
                    print(f"Motor speed returned: {int(self.ser.readline().strip().decode('utf-8'))}%")
                except:
                    print("Error detected")
            self.S = 1
        elif state == 4:
            # Arduino.speed.Motor1()          # spin visor motor
            # Arduino.speed.Motor2()          # CONT air for 10s
            if self.stateval != state:
                self.ser.flushOutput()
                self.ser.flushInput()
                self.ser.write(str(27).encode())
                time.sleep(.1)
                try:
                    print(f"Motor speed returned: {int(self.ser.readline().strip().decode('utf-8'))}%")
                except:
                    print("Error detected")
            self.S = 1
            self.alert_counter += 1           # OPTION HERE: INCREMENTAL ARDUINO SPEED AT EVERY LOOP (SO WITH INCREASE AT EVERY COUNTER STEP - SO IF IT DOESNT GET CAM CLEAR)
        elif state == 5:
            # Do nothing
            # Arduino.speed.Motor1(0)          # NO visor motor
            # Arduino.speed.Motor2(0)          # NO air  
            if self.stateval != state:
                self.ser.flushOutput()
                self.ser.flushInput()
                self.ser.write(str(0).encode())
                time.sleep(.1)
                try:
                    print(f"Motor speed returned: {int(self.ser.readline().strip().decode('utf-8'))}%")
                except:
                    print("Error detected")
            self.S = 0
            self.alert_counter = 0
        elif state == 6:
            # Arduino.speed.Motor1()          # spin visor motor
            # Arduino.speed.Motor2()          # BLAST air every 10s
            if self.stateval != state:
                self.ser.flushOutput()
                self.ser.flushInput()
                self.ser.write(str(25).encode())
                time.sleep(.1)
                try:
                    print(f"Motor speed returned: {int(self.ser.readline().strip().decode('utf-8'))}%")
                except:
                    print("Error detected")
            self.S = 1
            self.alert_counter = 0
        elif state == 7:
            # Arduino.speed.Motor1(0)          # NO visor motor
            # Arduino.speed.Motor2(0)          # NO air
            if self.stateval != state:
                self.ser.flushOutput()
                self.ser.flushInput()
                self.ser.write(str(0).encode())
                time.sleep(.1)
                try:
                    print(f"Motor speed returned: {int(self.ser.readline().strip().decode('utf-8'))}%")
                except:
                    print("Error detected")
            self.S = 1
        elif state == 8:
            # Arduino.speed.Motor1()          # spin visor motor
            # Arduino.speed.Motor2()          # CONT air for 10s
            if self.stateval != state:
                self.ser.flushOutput()
                self.ser.flushInput()
                self.ser.write(str(27).encode())
                time.sleep(.1)
                try:
                    print(f"Motor speed returned: {int(self.ser.readline().strip().decode('utf-8'))}%")
                except:
                    print("Error detected")
            self.S = 1
            self.alert_counter += 1           # OPTION HERE: INCREMENTAL ARDUINO SPEED AT EVERY LOOP (SO WITH INCREASE AT EVERY COUNTER STEP - SO IF IT DOESNT GET CAM CLEAR)
        self.stateval = state