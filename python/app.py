import paho.mqtt.client as mqtt 

topic_names = []

def on_message(mqttc, obj, msg,):
    # print(msg.topic + " " + str(msg.payload))
    payload = str(msg.payload)
    print(msg.topic + " Payload -> " + payload)

    topic_names.append(msg.topic)

try:
    mqttc = mqtt.Client()
    mqttc.on_message = on_message

    mqttc.connect("iot.eclipse.org", 1883, 60)

    mqttc.subscribe("7133egyptian/#", 0)

    mqttc.loop_forever()

except KeyboardInterrupt:
    print "Received topics:"
    for topic in topic_names:
        print topic
