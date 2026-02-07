import random
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

user_data = {
    "otp": "",
    "name": "",
    "password": "",
    "email": ""
}

root_layout = None
enter_otp_input = None
result_label = None
email_input = None


# -------- SIGN UP + OTP SCREEN --------
def build_signup_layout():
    global enter_otp_input, result_label, email_input

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
            result_label.text = "Please fill all fields!"
            return

        otp = str(random.randint(100000, 999999))
        user_data["otp"] = otp
        user_data["email"] = email_input.text
        user_data["name"] = name_input.text
        user_data["password"] = password_input.text

        sender_email = "omradhakrishnan2013@gmail.com"
        sender_password = "lzuz alep whft sfhn"  # Gmail app password
        receiver_email = email_input.text

        subject = "Your Splitwise App OTP Code"
        body = f"""
Hello {name_input},

Welcome to Splitwise!

Your One-Time Password (OTP) is:

{otp}

This code is valid for a short time.  
Please do not share this OTP with anyone for security reasons.

If you did not request this, you can safely ignore this email.

Happy splitting! 
— Splitwise Team
"""

        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            server.quit()
            result_label.text = "OTP sent to your email"
        except Exception as e:
            result_label.text = "Failed to send OTP"
            print(e)

    send_btn = Button(text="Send OTP")
    send_btn.bind(on_press=send_otp)
    layout.add_widget(send_btn)

    enter_otp_input = TextInput(hint_text="Enter OTP", multiline=False)
    layout.add_widget(enter_otp_input)

    verify_btn = Button(text="Verify OTP")
    verify_btn.bind(on_press=verify_otp)
    layout.add_widget(verify_btn)

    # Button to go directly to login if already signed up
    login_btn = Button(text="Already signed up? Click to login")
    login_btn.bind(on_press=lambda x: open_login_layout())
    layout.add_widget(login_btn)

    result_label = Label(text="")
    layout.add_widget(result_label)

    return layout


# -------- OTP VERIFY --------
def verify_otp(instance):
    if enter_otp_input.text == user_data["otp"]:
        open_login_layout()
    else:
        result_label.text = "Invalid OTP"


# -------- LOGIN SCREEN --------
def open_login_layout():
    root_layout.clear_widgets()
    root_layout.add_widget(build_login_layout())


def build_login_layout():
    layout = BoxLayout(orientation="vertical", padding=40, spacing=20)

    layout.add_widget(Label(text="Login", font_size=30))

    email_field = TextInput(hint_text="Email", multiline=False)
    password_field = TextInput(hint_text="Password", password=True)

    layout.add_widget(email_field)
    layout.add_widget(password_field)

    def login_check(instance):
        if email_field.text == user_data["email"]:
            if password_field.text == user_data["password"]:
                result_label.text = "Okay, Logged in!"
                open_app_layout(None)
            else:
                result_label.text = "Wrong password!"
        else:
            result_label.text = "SIGN UP!"
            # Go back to signup page
            root_layout.clear_widgets()
            root_layout.add_widget(build_signup_layout())

    continue_btn = Button(text="Continue")
    continue_btn.bind(on_press=login_check)
    layout.add_widget(continue_btn)

    global result_label
    result_label = Label(text="")
    layout.add_widget(result_label)

    return layout


# -------- FINAL APP SCREEN --------
def open_app_layout(instance):
    root_layout.clear_widgets()
    root_layout.add_widget(Label(text="Continued", font_size=40))


# -------- APP --------
class Splitwise(App):
    def build(self):
        global root_layout
        root_layout = BoxLayout()
        root_layout.add_widget(build_signup_layout())
        return root_layout


if __name__ == "__main__":
    Splitwise().run()
 