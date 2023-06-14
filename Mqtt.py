import paho.mqtt.client as mqtt
import ssl

#------------------------------------ DEFINE CLASSES ------------------------------------#

class MQTTClient:
    def __init__(self, broker_address, broker_port):
        self.broker_address = broker_address
        self.broker_port = broker_port
        self.subscribe_topics = ["DryveSystem1/MODE"]
        self.publish_topics = ["DryveSystem1/RS", "DryveSystem1/CAM", "DryveSystem1/ALERT", "DryveSystem1/S"]
        self.AUTO = None
        self.SPEED = None

        # Create MQTT client instance
        self.client = mqtt.Client(transport="websockets")

        # Set callback functions
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def connect(self):
        # Connect to MQTT broker
        self.client.connect(self.broker_address, self.broker_port, 60)

        # Start MQTT loop to process network traffic, callbacks, and reconnections
        self.client.loop_start()

    def disconnect(self):
        # Stop MQTT loop and disconnect from broker
        self.client.loop_stop()
        self.client.disconnect()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT broker")

            # Subscribe to topics
            for topic in self.subscribe_topics:
                client.subscribe(topic)
        else:
            print("Connection failed with error code " + str(rc))

    def on_message(self, client, userdata, msg):
        
        topic = msg.topic
        payload = msg.payload.decode("utf-8")
        print("Received message: " + topic + " " + payload)

        # Process the received variables
        if topic == self.subscribe_topics[0]:
            self.process_MODE(payload)

    def process_MODE(self, message):
        # Parse the message to extract variables
        variables = message.split(",")
        self.AUTO = int(variables[0].strip())
        self.SPEED = int(variables[1].strip())
        # print(variables)
        # self.AUTO = int(variables[0][1])
        # self.SPEED = int(variables[1][0])

        # Print the received variables
        print("AUTO: ", self.AUTO)
        print("SPEED: ", self.SPEED)

    def publish_message(self, topic, message):
        # Publish message to the specified topic
        self.client.publish(topic, message)