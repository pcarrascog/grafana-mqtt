import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient
import datetime
import logging
def persists(msg):
    current_time = datetime.datetime.utcnow().isoformat()
    json_body = [
        {
            "measurement": "stem",
            "tags": {},
            "time": current_time,
            "fields": {
                "topic" : msg.topic,
                "value": (msg.payload)
            }
        }
    ]
    logging.info(json_body)
    influx_client.write_points(json_body)
logging.basicConfig(level=logging.INFO)
influx_client = InfluxDBClient('206.189.206.234', 8086, database='stem')
client = mqtt.Client()
client.on_connect = lambda self, mosq, obj, rc: self.subscribe("SLC/#")
client.on_message = lambda client, userdata, msg: persists(msg)
client.connect("iot.eclipse.org", 1883, 60)
client.loop_forever()
