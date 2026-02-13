import random
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
import smtplib
from email.mime.text import MIMEText

# Store user info
user_data = {"otp": "", 
             "name": "", ""
             "password": "", 
             "email": ""}

sm = ScreenManager(transition=SlideTransition())


# Popup
def show_popup(title, message):
    popup = Popup(
        title=title,
        content=Label(text=message),
        size_hint=(None, None),
        size=(450, 300)
    )
    popup.open()


# ---------------- SIGNUP SCREEN ----------------
def build_signup_layout():
    layout = BoxLayout(orientation="vertical", padding=40, spacing=20)
    layout.add_widget(Label(text="Sign Up", font_size=30))

    name_input = TextInput(hint_text="Name", multiline=False)
    email_input = TextInput(hint_text="Email", multiline=False)
    password_input = TextInput(hint_text="Password", password=True)

    layout.add_widget(name_input)
    layout.add_widget(email_input)
    layout.add_widget(password_input)

    def send_otp(instance):
        if not name_input.text or not email_input.text or not password_input.text:
            show_popup("Error", "Please fill all fields!")
            return

        otp = str(random.randint(100000, 999999))
        user_data["otp"] = otp
        user_data["email"] = email_input.text
        user_data["name"] = name_input.text
        user_data["password"] = password_input.text

        try:
            sender_email = "omradhakrishnan2013@gmail.com"
            sender_password = "lzuz alep whft sfhn"  # Gmail App Password
            receiver_email = user_data["email"]

            subject = "Your Splitwise App OTP Code"

            body = f"""
Hello {user_data['name']},

Welcome to Splitwise!

Your One-Time Password (OTP) is:

{otp}

This code is valid for a short time.
Please do not share this OTP with anyone for security reasons.

If you did not request this, you can safely ignore this email.

Happy splitting!
— Splitwise Team
"""

            message = MIMEText(body)
            message["Subject"] = subject
            message["From"] = sender_email
            message["To"] = receiver_email

            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            server.quit()

            show_popup("Success", "OTP has been sent to your email!")

        except Exception as e:
            show_popup("Error", f"Failed to send email:\n{str(e)}")

    layout.add_widget(Button(text="Send OTP", on_press=send_otp))

    otp_input = TextInput(hint_text="Enter OTP", multiline=False)
    layout.add_widget(otp_input)

    def verify_otp(instance):
        if otp_input.text == user_data["otp"]:
            show_popup("Success", "OTP Verified Successfully!")
            sm.current = "Login"
        else:
            show_popup("Error", "Invalid OTP")

    layout.add_widget(Button(text="Verify OTP", on_press=verify_otp))

    def go_to_login(instance):
        sm.current = "Login"

    layout.add_widget(Button(text="Already signed up? Go to login", on_press=go_to_login))

    return layout


# ---------------- LOGIN SCREEN ----------------
def build_login_layout():
    layout = BoxLayout(orientation="vertical", padding=40, spacing=20)
    layout.add_widget(Label(text="Login", font_size=30))

    email_field = TextInput(hint_text="Email", multiline=False)
    password_field = TextInput(hint_text="Password", password=True)

    layout.add_widget(email_field)
    layout.add_widget(password_field)

    def login_check(instance):
        if not email_field.text or not password_field.text:
            show_popup("Error", "Invalid Email or Password")
            return

        if email_field.text == user_data["email"] and password_field.text == user_data["password"]:
            show_popup("Success", "Login Successful!")
            sm.current = "Dashboard"
        else:
            show_popup("Error", "Invalid Email or Password")

    def go_to_signup(instance):
        sm.current = "Signup"

    layout.add_widget(Button(text="Continue", on_press=login_check))
    layout.add_widget(Button(text="⬅ Back to Sign Up", on_press=go_to_signup))

    return layout


# ---------------- DASHBOARD ----------------
def build_dashboard():
    layout = BoxLayout()
    layout.add_widget(Label(text="Welcome to Splitwise!", font_size=40))
    return layout


# Create Screens
signup_screen = Screen(name="Signup")
signup_screen.add_widget(build_signup_layout())

login_screen = Screen(name="Login")
login_screen.add_widget(build_login_layout())

dashboard_screen = Screen(name="Dashboard")
dashboard_screen.add_widget(build_dashboard())

sm.add_widget(signup_screen)
sm.add_widget(login_screen)
sm.add_widget(dashboard_screen)


# ---------------- APP ----------------
class Splitwise(App):
    def build(self):
        return sm


if __name__ == "__main__":
    Splitwise().run()
