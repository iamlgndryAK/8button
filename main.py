from kivy.app import App
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.clock import Clock, mainthread
import paho.mqtt.client as mqtt
import ssl
import certifi

ssl_context = ssl.create_default_context(cafile=certifi.where())

Builder.load_string("""
<Grid>
    GridLayout:
        id: main_grid
        cols: 1
        size: root.width, root.height


        GridLayout:
            id: top_grid
            cols: 1

            Label:
                id: title_label
                text: "HALL"
                font_size: 125


        GridLayout:
            id: middle_grid
            cols: 4

            Label:
                id: builtin_label
                text: "BUILTIN"
                font_size: 32

                canvas.before:
                    Color:
                        rgba: (1,1,1,1)
                    Rectangle:
                        size: self.size
                        pos: self.pos

            Label:
                id: d4_label
                text: "D4"
                font_size: 32

                canvas.before:
                    Color:
                        rgba: (1,1,1,1)
                    Rectangle:
                        size: self.size
                        pos: self.pos

            Label:
                id: oo
                text: ""
                font_size: 32

                canvas.before:
                    Color:
                        rgba: (1,1,1,1)
                    Rectangle:
                        size: self.size
                        pos: self.pos

            Label:
                id: slider_label
                text: ""
                font_size: 32

                canvas.before:
                    Color:
                        rgba: (1,1,1,1)
                    Rectangle:
                        size: self.size
                        pos: self.pos

        GridLayout:
            id: bottom_grid
            cols: 4
        
        GridLayout:
            id: bottom2_grid
            cols: 4


""")


broker_address = "735cdc1a9da848019c7a8bedec3ebe5d.s1.eu.hivemq.cloud"
broker_port = 8883

client_id = "my_client_id"

username = "clash085529"
password = "08552916937aA@"


builtin_led_topic = "builtin_led_topic"
d4_pin_topic = "d4_pin_topic"
d1_pin_topic = "d1_pin_topic"
d2_pin_topic = "d2_pin_topic"
d5_pin_topic = "d5_pin_topic"
d6_pin_topic = "d6_pin_topic"
d7_pin_topic = "d7_pin_topic"
d8_pin_topic = "d8_pin_topic"

builtin_message = ""
message_builtin = ""
message_d4 = ""
message_d1 = ""
message_d2 = ""
message_d5 = ""
message_d6 = ""
message_d7 = ""
message_d8 = ""
current_builtin_message = ""

d4_message = ""
d4_status_message = ""
current_d4_message = ""

d1_message = ""
d1_status_message = ""
current_d1_message = ""

d2_message = ""
d2_status_message = ""
current_d2_message = ""

d5_message = ""
d5_status_message = ""
current_d5_message = ""

d6_message = ""
d6_status_message = ""
current_d6_message = ""

d7_message = ""
d7_status_message = ""
current_d7_message = ""

d8_message = ""
d8_status_message = ""
current_d8_message = ""

rc_status = 0

builtin_led_status = "builtin_led_status"
d4_pin_status = "d4_pin_status"
d1_pin_status = "d1_pin_status"
d2_pin_status = "d2_pin_status"
d5_pin_status = "d5_pin_status"
d6_pin_status = "d6_pin_status"
d7_pin_status = "d7_pin_status"
d8_pin_status = "d8_pin_status"

last_press_time = 0
debounce_interval = 0.3


class Grid(Widget):
    def __init__(self, **kwargs):
        super(Grid, self).__init__(**kwargs)

        global current_builtin_message

        self.client = mqtt.Client(client_id)
        self.start_client()

        self.builtin_button = Button(text='Press me!', font_size=32, background_color=[1, 1, 1, 0.5])
        self.builtin_button.bind(on_release=self.switch_builtin)

        self.d4_button = Button(text='Press me!', font_size=32, background_color=[1, 1, 1, 0.5])
        self.d4_button.bind(on_release=self.switch_d4)

        self.d1_button = Button(text='OFF', font_size=32, background_color=[1, 0, 0, 0.5])
        self.d1_button.bind(on_release=self.switch_d1)

        self.d2_button = Button(text='OFF', font_size=32, background_color=[1, 0, 0, 0.5])
        self.d2_button.bind(on_release=self.switch_d2)

        self.d5_button = Button(text='OFF', font_size=32, background_color=[1, 0, 0, 0.5])
        self.d5_button.bind(on_release=self.switch_d5)

        self.d6_button = Button(text='OFF', font_size=32, background_color=[1, 0, 0, 0.5])
        self.d6_button.bind(on_release=self.switch_d6)

        self.d7_button = Button(text='OFF', font_size=32, background_color=[1, 0, 0, 0.5])
        self.d7_button.bind(on_release=self.switch_d7)

        self.d8_button = Button(text='OFF', font_size=32, background_color=[1, 0, 0, 0.5])
        self.d8_button.bind(on_release=self.switch_d8)

        self.ids.bottom_grid.add_widget(self.builtin_button)
        self.ids.bottom_grid.add_widget(self.d4_button)
        self.ids.bottom_grid.add_widget(self.d1_button)
        self.ids.bottom_grid.add_widget(self.d2_button)
        self.ids.bottom2_grid.add_widget(self.d5_button)
        self.ids.bottom2_grid.add_widget(self.d6_button)
        self.ids.bottom2_grid.add_widget(self.d7_button)
        self.ids.bottom2_grid.add_widget(self.d8_button)

        self.ids.builtin_label.color = [0, 0, 0, 1]
        self.ids.builtin_label.bold = True

        self.ids.d4_label.color = [0, 0, 0, 1]
        self.ids.d4_label.bold = True

    def switch_builtin(self, instance):
        global builtin_message, last_press_time
        current_time = Clock.get_time()
        if current_time - last_press_time > debounce_interval:
            last_press_time = current_time
            if builtin_message == "0":
                builtin_message = "1"
                instance.background_color = [0, 1, 0, 1]
                instance.color = [1, 1, 1, 1]
                instance.text = "ON"

                self.ids.builtin_label.color = [0, 1, 0, 1]
            else:
                builtin_message = "0"
                instance.background_color = [1, 0, 0, 1]
                instance.color = [1, 1, 1, 1]
                instance.text = "OFF"

                self.ids.builtin_label.color = [1, 0, 0, 1]

            self.client.publish(builtin_led_topic, builtin_message)
            print('BuiltIn pressed')
            print(self.client.is_connected())

    def switch_d4(self, instance):
        global d4_message, last_press_time
        current_time = Clock.get_time()
        if current_time - last_press_time > debounce_interval:
            last_press_time = current_time
            if d4_message == "0":
                d4_message = "1"
                instance.background_color = [0, 1, 0, 1]
                instance.color = [1, 1, 1, 1]
                instance.text = "ON"

                self.ids.d4_label.color = [0, 1, 0, 1]
            else:
                d4_message = "0"
                instance.background_color = [1, 0, 0, 1]
                instance.color = [1, 1, 1, 1]
                instance.text = "OFF"

                self.ids.d4_label.color = [1, 0, 0, 1]

            self.client.publish(d4_pin_topic, d4_message)
            print('D4 pressed')

    def switch_d1(self, instance):
        global d1_message, last_press_time
        current_time = Clock.get_time()
        if current_time - last_press_time > debounce_interval:
            last_press_time = current_time
            if d1_message == "0":
                d1_message = "1"
                instance.background_color = [0, 1, 0, 1]
                instance.color = [1, 1, 1, 1]
                instance.text = "ON"

            else:
                d1_message = "0"
                instance.background_color = [1, 0, 0, 1]
                instance.color = [1, 1, 1, 1]
                instance.text = "OFF"

            self.client.publish(d1_pin_topic, d1_message)
            print('D1 pressed')

    def switch_d2(self, instance):
        global d2_message, last_press_time
        current_time = Clock.get_time()
        if current_time - last_press_time > debounce_interval:
            last_press_time = current_time
            if d2_message == "0":
                d2_message = "1"
                instance.background_color = [0, 1, 0, 1]
                instance.color = [1, 1, 1, 1]
                instance.text = "ON"

            else:
                d2_message = "0"
                instance.background_color = [1, 0, 0, 1]
                instance.color = [1, 1, 1, 1]
                instance.text = "OFF"

            self.client.publish(d2_pin_topic, d2_message)
            print('D2 pressed')

    def switch_d5(self, instance):
        global d5_message, last_press_time
        current_time = Clock.get_time()
        if current_time - last_press_time > debounce_interval:
            last_press_time = current_time
            if d5_message == "0":
                d5_message = "1"
                instance.background_color = [0, 1, 0, 1]
                instance.color = [1, 1, 1, 1]
                instance.text = "ON"

            else:
                d5_message = "0"
                instance.background_color = [1, 0, 0, 1]
                instance.color = [1, 1, 1, 1]
                instance.text = "OFF"

            self.client.publish(d5_pin_topic, d5_message)
            print('D5 pressed')

    def switch_d6(self, instance):
        global d6_message, last_press_time
        current_time = Clock.get_time()
        if current_time - last_press_time > debounce_interval:
            last_press_time = current_time
            if d6_message == "0":
                d6_message = "1"
                instance.background_color = [0, 1, 0, 1]
                instance.color = [1, 1, 1, 1]
                instance.text = "ON"

            else:
                d6_message = "0"
                instance.background_color = [1, 0, 0, 1]
                instance.color = [1, 1, 1, 1]
                instance.text = "OFF"

            self.client.publish(d6_pin_topic, d6_message)
            print('D6 pressed')

    def switch_d7(self, instance):
        global d7_message, last_press_time
        current_time = Clock.get_time()
        if current_time - last_press_time > debounce_interval:
            last_press_time = current_time
            if d7_message == "0":
                d7_message = "1"
                instance.background_color = [0, 1, 0, 1]
                instance.color = [1, 1, 1, 1]
                instance.text = "ON"

            else:
                d7_message = "0"
                instance.background_color = [1, 0, 0, 1]
                instance.color = [1, 1, 1, 1]
                instance.text = "OFF"

            self.client.publish(d7_pin_topic, d7_message)
            print('D7 pressed')

    def switch_d8(self, instance):
        global d8_message, last_press_time
        current_time = Clock.get_time()
        if current_time - last_press_time > debounce_interval:
            last_press_time = current_time
            if d8_message == "0":
                d8_message = "1"
                instance.background_color = [0, 1, 0, 1]
                instance.color = [1, 1, 1, 1]
                instance.text = "ON"

            else:
                d8_message = "0"
                instance.background_color = [1, 0, 0, 1]
                instance.color = [1, 1, 1, 1]
                instance.text = "OFF"

            self.client.publish(d8_pin_topic, d8_message)
            print('D8 pressed')

    def on_message(self, client, userdata, message):
        global message_builtin, message_d4, message_d1, message_d2,\
            message_d5, message_d6, message_d7, message_d8,\
            current_builtin_message, current_d4_message,\
            current_d1_message, current_d2_message, current_d5_message,\
            current_d6_message, current_d7_message, current_d8_message

        if message.topic == builtin_led_status:
            message_builtin = str(message.payload.decode("utf-8"))
            print("Received message: ", message_builtin)
            print(message.topic)

            print(current_builtin_message, message_builtin)

            print("helllloooooooooooo")
            if current_builtin_message != message_builtin:
                self.update_builtin()

        elif message.topic == d4_pin_status:
            message_d4 = str(message.payload.decode("utf-8"))
            if current_d4_message != message_d4:
                self.update_d4()

        elif message.topic == d1_pin_status:
            message_d1 = str(message.payload.decode("utf-8"))
            if current_d1_message != message_d1:
                self.update_d1()

        elif message.topic == d2_pin_status:
            message_d2 = str(message.payload.decode("utf-8"))
            if current_d2_message != message_d2:
                self.update_d2()

        elif message.topic == d5_pin_status:
            message_d5 = str(message.payload.decode("utf-8"))
            if current_d5_message != message_d5:
                self.update_d5()

        elif message.topic == d6_pin_status:
            message_d6 = str(message.payload.decode("utf-8"))
            if current_d6_message != message_d6:
                self.update_d6()

        elif message.topic == d7_pin_status:
            message_d7 = str(message.payload.decode("utf-8"))
            if current_d7_message != message_d7:
                self.update_d7()

        elif message.topic == d8_pin_status:
            message_d8 = str(message.payload.decode("utf-8"))
            if current_d8_message != message_d8:
                self.update_d8()

    @mainthread
    def update_builtin(self):
        global builtin_message, current_builtin_message
        if message_builtin == "1":
            self.builtin_button.background_color = [0, 1, 0, 1]
            self.builtin_button.color = [1, 1, 1, 1]
            self.builtin_button.text = "ON"
            self.ids.builtin_label.color = [0, 1, 0, 1]
            builtin_message = "1"

        else:
            self.builtin_button.background_color = [1, 0, 0, 1]
            self.builtin_button.color = [1, 1, 1, 1]
            self.builtin_button.text = "OFF"
            self.ids.builtin_label.color = [1, 0, 0, 1]
            builtin_message = "0"

        current_builtin_message = message_builtin

        print('Builtin pressed')

    @mainthread
    def update_d4(self):
        global d4_message, current_d4_message
        if message_d4 == "1":
            self.d4_button.background_color = [0, 1, 0, 1]
            self.d4_button.color = [1, 1, 1, 1]
            self.d4_button.text = "ON"
            self.ids.d4_label.color = [0, 1, 0, 1]
            d4_message = "1"
        else:
            self.d4_button.background_color = [1, 0, 0, 1]
            self.d4_button.color = [1, 1, 1, 1]
            self.d4_button.text = "OFF"
            self.ids.d4_label.color = [1, 0, 0, 1]
            d4_message = "0"

        current_d4_message = message_d4

        print('D4 pressed')

    @mainthread
    def update_d1(self):
        global d1_message, current_d1_message
        if message_d1 == "1":
            self.d1_button.background_color = [0, 1, 0, 1]
            self.d1_button.color = [1, 1, 1, 1]
            self.d1_button.text = "ON"
            d1_message = "1"
        else:
            self.d1_button.background_color = [1, 0, 0, 1]
            self.d1_button.color = [1, 1, 1, 1]
            self.d1_button.text = "OFF"
            d1_message = "0"

        current_d1_message = message_d1

        print('D1 pressed')

    @mainthread
    def update_d2(self):
        global d2_message, current_d2_message
        if message_d2 == "1":
            self.d2_button.background_color = [0, 1, 0, 1]
            self.d2_button.color = [1, 1, 1, 1]
            self.d2_button.text = "ON"
            d2_message = "1"
        else:
            self.d2_button.background_color = [1, 0, 0, 1]
            self.d2_button.color = [1, 1, 1, 1]
            self.d2_button.text = "OFF"
            d2_message = "0"

        current_d2_message = message_d2

        print('D2 pressed')

    @mainthread
    def update_d5(self):
        global d5_message, current_d5_message
        if message_d5 == "1":
            self.d5_button.background_color = [0, 1, 0, 1]
            self.d5_button.color = [1, 1, 1, 1]
            self.d5_button.text = "ON"
            d5_message = "1"
        else:
            self.d5_button.background_color = [1, 0, 0, 1]
            self.d5_button.color = [1, 1, 1, 1]
            self.d5_button.text = "OFF"
            d5_message = "0"

        current_d5_message = message_d5

        print('D5 pressed')

    @mainthread
    def update_d6(self):
        global d6_message, current_d6_message
        if message_d6 == "1":
            self.d6_button.background_color = [0, 1, 0, 1]
            self.d6_button.color = [1, 1, 1, 1]
            self.d6_button.text = "ON"
            d6_message = "1"
        else:
            self.d6_button.background_color = [1, 0, 0, 1]
            self.d6_button.color = [1, 1, 1, 1]
            self.d6_button.text = "OFF"
            d6_message = "0"

        current_d6_message = message_d6

        print('D6 pressed')

    @mainthread
    def update_d7(self):
        global d7_message, current_d7_message
        if message_d7 == "1":
            self.d7_button.background_color = [0, 1, 0, 1]
            self.d7_button.color = [1, 1, 1, 1]
            self.d7_button.text = "ON"
            d7_message = "1"
        else:
            self.d7_button.background_color = [1, 0, 0, 1]
            self.d7_button.color = [1, 1, 1, 1]
            self.d7_button.text = "OFF"
            d7_message = "0"

        current_d7_message = message_d7

        print('D7 pressed')

    @mainthread
    def update_d8(self):
        global d8_message, current_d8_message
        if message_d8 == "1":
            self.d8_button.background_color = [0, 1, 0, 1]
            self.d8_button.color = [1, 1, 1, 1]
            self.d8_button.text = "ON"
            d8_message = "1"
        else:
            self.d8_button.background_color = [1, 0, 0, 1]
            self.d8_button.color = [1, 1, 1, 1]
            self.d8_button.text = "OFF"
            d8_message = "0"

        current_d8_message = message_d8

        print('D8 pressed')

    def on_connect(self, client, userdata, flags, rc):
        global rc_status
        rc_status = rc
        if rc == 0:
            print("Connected to MQTT broker")
        else:
            print("Failed to connect to MQTT broker")

        return rc_status


    def start_client(self):
        global current_builtin_message

        self.client.username_pw_set(username, password)

        self.client.tls_set_context(ssl_context)
        self.client.on_connect = self.on_connect

        self.client.connect(broker_address, broker_port)

        self.client.on_message = self.on_message
        self.client.loop_start()
        print("mmmmmmmm")

        self.client.subscribe(builtin_led_status)
        self.client.subscribe(d4_pin_status)
        self.client.subscribe(d1_pin_status)
        self.client.subscribe(d2_pin_status)
        self.client.subscribe(d5_pin_status)
        self.client.subscribe(d6_pin_status)
        self.client.subscribe(d7_pin_status)
        self.client.subscribe(d8_pin_status)

        print(self.client.on_connect)


class HelloApp(App):
    def build(self):
        return Grid()



app = HelloApp()
app.run()

