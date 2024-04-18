import time as t
import json
import AWSIoTPythonSDK.MQTTLib as AWSIoTPyMQTT
# Define ENDPOINT, CLIENT_ID, PATH_TO_CERT, PATH_TO_KEY, PATH_TO_ROOT, MESSAGE, TOPIC, and RANGE
ENDPOINT = "a30vkaao4lvmpj-ats.iot.eu-north-1.amazonaws.com"
CLIENT_ID = "#"
PATH_TO_CERT = "C:/Users/Edoardo/git/ToolIoT/connect_device_package/TestWildcard.cert.pem"
PATH_TO_KEY = "C:/Users/Edoardo/git/ToolIoT/connect_device_package/TestWildcard.private.key"
PATH_TO_ROOT = "C:/Users/Edoardo/git/ToolIoT/connect_device_package/root-CA.crt"
MESSAGE = "Hello World"
TOPIC = "test/testing"
RANGE = 20
myAWSIoTMQTTClient = AWSIoTPyMQTT.AWSIoTMQTTClient(CLIENT_ID)
myAWSIoTMQTTClient.configureEndpoint(ENDPOINT, 8883)
myAWSIoTMQTTClient.configureCredentials(PATH_TO_ROOT, PATH_TO_KEY, PATH_TO_CERT)
myAWSIoTMQTTClient.connect()

myAWSIoTMQTTClient.subscribe('command/device/'+CLIENT_ID, 0, print)

print('Begin Publish')
for i in range (RANGE):
  data = "{} [{}]".format(MESSAGE, i+1)
  message = {"message" : data}
  myAWSIoTMQTTClient.publish(TOPIC, json.dumps(message), 1)
  print("Published: '" + json.dumps(message) + "' to the topic: " + "'test/testing'")
  t.sleep(0.1)
  
while True:
  t.sleep(10)
  
print('Publish End')
myAWSIoTMQTTClient.disconnect()
