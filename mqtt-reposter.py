import paho.mqtt.client as mqtt
import json
from datetime import datetime, timezone

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.publish("mqtt-reposter/LWT",payload="connected", qos=0, retain=True) 
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.unsubscribe("$SYS/#")

    client.subscribe([("TheengsGateway/BTtoMQTT/XXXXXXXXXXXA", 0),
                      ("TheengsGateway/BTtoMQTT/XXXXXXXXXXXB", 0),
                      ("TheengsGateway/BTtoMQTT/XXXXXXXXXXXC", 0),
                      ("TheengsGateway/BTtoMQTT/XXXXXXXXXXXD", 0),
                      ("TheengsGateway/BTtoMQTT/XXXXXXXXXXXE", 0),])

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
   m_decode=str(msg.payload.decode("utf-8","ignore"))
   m_in=json.loads(m_decode) #decode json data
   id = m_in['id'].replace(":", "")
   if id == "XXXXXXXXXXXA":
      id = "Room 1"
   elif id == "XXXXXXXXXXXB":
      id = "Room 2"
   elif id == "XXXXXXXXXXXC":
      id = "Room 3"
   elif id == "XXXXXXXXXXXD":
      id = "Room 4"
   else:
      id = "Room 5"

   for v, k in m_in.items():
      if v == "tempc" or v == "hum" or v == "rssi" or v == "batt": # getting the values that are needed
        client.publish('mqtt-reposter/'+id+'/'+v, k, qos=0)

   now = datetime.now(timezone.utc).isoformat(" ", "seconds")
   client.publish('mqtt-reposter/'+id+'/last_seen', now, qos=0)

client = mqtt.Client(client_id="mqtt-reposter", clean_session=False, userdata=None, protocol=mqtt.MQTTv311, transport="tcp")
client.will_set("mqtt-reposter/LWT", payload="disconnected", qos=0, retain=True)
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(username="mqtt-reposter", password="verysecurepassword")
client.connect("192.168.1.1", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
