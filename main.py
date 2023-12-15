from kivy.app import App
from kivy.uix.button import Button


class SimpleKivyApp(App):
    def build(self):
        # Create a button with a callback function
        button = Button(text="Click me!", on_press=self.on_button_click)
        return button

    def on_button_click(self, instance):
        print("Button clicked!")


if __name__ == "__main__":
    SimpleKivyApp().run()
