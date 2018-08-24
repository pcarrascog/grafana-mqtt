import paho.mqtt.client as paho
import paho.mqtt as mqtt
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from urlparse import parse_qs
import cgi

class GP(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
    def do_HEAD(self):
        self._set_headers()
    #def do_GET(self):
    #    self._set_headers()
    #    print self.path
    #    print parse_qs(self.path[2:])
    #    self.wfile.write("<html><body><h1>Get Request Received!</h1></body></html>")
    def do_POST(self):
        self._set_headers()
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST'}
        )
        print form
        print form.getvalue("topic")
        print form.getvalue("payload")
        #print form("evalMatches")  
        #msg = {'topic':form.getvalue("topic"), 'payload':form.getvalue("payload"), 'qos':0, 'retain':False}
         
        #multiple([msg], 'localhost', '1883', 'hook', 60) #, will, auth, tls,
            # protocol, transport)
        #self.wfile.write("<html><body><h1>POST Request Received!</h1></body></html>")

def run(server_class=HTTPServer, handler_class=GP, port=8088):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print 'Server running at localhost:8088...'
    httpd.serve_forever()
############
# MQTT 

def _do_publish(client):
    """Internal function"""

    message = client._userdata.pop()

    if isinstance(message, dict):
        client.publish(**message)
    elif isinstance(message, tuple):
        client.publish(*message)
    else:
        raise ValueError('message must be a dict or a tuple')

def _on_connect(client, userdata, flags, rc):
    """Internal callback"""
    #pylint: disable=invalid-name, unused-argument

    if rc == 0:
        if len(userdata) > 0:
            _do_publish(client)
    else:
        raise mqtt.MQTTException(paho.connack_string(rc))

def _on_publish(client, userdata, mid):
    """Internal callback"""
    #pylint: disable=unused-argument

    if len(userdata) == 0:
        client.disconnect()
    else:
        _do_publish(client)

def multiple(msgs, hostname="localhost", port=1883, client_id="", keepalive=60,
             will=None, auth=None, tls=None, protocol=paho.MQTTv311,
             transport="tcp"):
    """Publish multiple messages to a broker, then disconnect cleanly.
    This function creates an MQTT client, connects to a broker and publishes a
    list of messages. Once the messages have been delivered, it disconnects
    cleanly from the broker.
    msgs : a list of messages to publish. Each message is either a dict or a
           tuple.
           If a dict, only the topic must be present. Default values will be
           used for any missing arguments. The dict must be of the form:
           msg = {'topic':"<topic>", 'payload':"<payload>", 'qos':<qos>,
           'retain':<retain>}
           topic must be present and may not be empty.
           If payload is "", None or not present then a zero length payload
           will be published.
           If qos is not present, the default of 0 is used.
           If retain is not present, the default of False is used.
           If a tuple, then it must be of the form:
           ("<topic>", "<payload>", qos, retain)
    hostname : a string containing the address of the broker to connect to.
               Defaults to localhost.
    port : the port to connect to the broker on. Defaults to 1883.
    client_id : the MQTT client id to use. If "" or None, the Paho library will
                generate a client id automatically.
    keepalive : the keepalive timeout value for the client. Defaults to 60
                seconds.
    will : a dict containing will parameters for the client: will = {'topic':
           "<topic>", 'payload':"<payload">, 'qos':<qos>, 'retain':<retain>}.
           Topic is required, all other parameters are optional and will
           default to None, 0 and False respectively.
           Defaults to None, which indicates no will should be used.
    auth : a dict containing authentication parameters for the client:
           auth = {'username':"<username>", 'password':"<password>"}
           Username is required, password is optional and will default to None
           if not provided.
           Defaults to None, which indicates no authentication is to be used.
    tls : a dict containing TLS configuration parameters for the client:
          dict = {'ca_certs':"<ca_certs>", 'certfile':"<certfile>",
          'keyfile':"<keyfile>", 'tls_version':"<tls_version>",
          'ciphers':"<ciphers">}
          ca_certs is required, all other parameters are optional and will
          default to None if not provided, which results in the client using
          the default behaviour - see the paho.mqtt.client documentation.
          Alternatively, tls input can be an SSLContext object, which will be
          processed using the tls_set_context method.
          Defaults to None, which indicates that TLS should not be used.
    transport : set to "tcp" to use the default setting of transport which is
          raw TCP. Set to "websockets" to use WebSockets as the transport.
    """

    if not isinstance(msgs, list):
        raise ValueError('msgs must be a list')

    client = paho.Client(client_id=client_id,
                         userdata=msgs, protocol=protocol, transport=transport)

    client.on_publish = _on_publish
    client.on_connect = _on_connect

    if auth:
        username = auth.get('username')
        if username:
            password = auth.get('password')
            client.username_pw_set(username, password)
        else:
            raise KeyError("The 'username' key was not found, this is "
                           "required for auth")

    if will is not None:
        client.will_set(**will)

    if tls is not None:
        if isinstance(tls, dict):
            client.tls_set(**tls)
        else:
            # Assume input is SSLContext object
            client.tls_set_context(tls)

    client.connect(hostname, port, keepalive)
    client.loop_forever()


def single(topic, payload=None, qos=0, retain=False, hostname="localhost",
           port=1883, client_id="", keepalive=60, will=None, auth=None,
           tls=None, protocol=paho.MQTTv311, transport="tcp"):
    """Publish a single message to a broker, then disconnect cleanly.
    This function creates an MQTT client, connects to a broker and publishes a
    single message. Once the message has been delivered, it disconnects cleanly
    from the broker.
    topic : the only required argument must be the topic string to which the
            payload will be published.
    payload : the payload to be published. If "" or None, a zero length payload
              will be published.
    qos : the qos to use when publishing,  default to 0.
    retain : set the message to be retained (True) or not (False).
    hostname : a string containing the address of the broker to connect to.
               Defaults to localhost.
    port : the port to connect to the broker on. Defaults to 1883.
    client_id : the MQTT client id to use. If "" or None, the Paho library will
                generate a client id automatically.
    keepalive : the keepalive timeout value for the client. Defaults to 60
                seconds.
    will : a dict containing will parameters for the client: will = {'topic':
           "<topic>", 'payload':"<payload">, 'qos':<qos>, 'retain':<retain>}.
           Topic is required, all other parameters are optional and will
           default to None, 0 and False respectively.
           Defaults to None, which indicates no will should be used.
    auth : a dict containing authentication parameters for the client:
           auth = {'username':"<username>", 'password':"<password>"}
           Username is required, password is optional and will default to None
           if not provided.
           Defaults to None, which indicates no authentication is to be used.
    tls : a dict containing TLS configuration parameters for the client:
          dict = {'ca_certs':"<ca_certs>", 'certfile':"<certfile>",
          'keyfile':"<keyfile>", 'tls_version':"<tls_version>",
          'ciphers':"<ciphers">}
          ca_certs is required, all other parameters are optional and will
          default to None if not provided, which results in the client using
          the default behaviour - see the paho.mqtt.client documentation.
          Defaults to None, which indicates that TLS should not be used.
          Alternatively, tls input can be an SSLContext object, which will be
          processed using the tls_set_context method.
    transport : set to "tcp" to use the default setting of transport which is
          raw TCP. Set to "websockets" to use WebSockets as the transport.
    """






############
run()
