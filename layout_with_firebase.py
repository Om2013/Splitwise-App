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
import firebase_admin
from firebase_admin import credentials, db
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button 

cred = credentials.Certificate("firebase_config.json")
firebase_admin.initialize_app(cred,{
    "databaseURL":"https://splitwiseapp-70def-default-rtdb.firebaseio.com"
})

# Store user 
user_data = {"otp": "", 
             "name": "", 
             "password": "", 
             "email": ""}

sm = ScreenManager(transition=SlideTransition())


# ---------------- POPUP ----------------
def show_popup(title, message):
    popup = Popup(
        title=title,
        content=Label(text=message),
        size_hint=(None, None),
        size=(450, 300)
    )
    popup.open()


# ---------------- FIREBASE----------------
def write_email_and_password(userid, email, password, name):
    if userid is None:
        userid = random.randint(1000, 9999)
    ref = db.reference(f"users/{userid}")
    ref.set({
        "name": name,
        "password": password,
        "email": email
    })
    print(f"USER {userid} is added successfully")


#-------------------Add Members-----------------
def add_members(instance):
    email = group_member_email_input.text.strip()
    name = group_member_name_input.text.strip()
    contact = group_member_contact_input.text.strip()

    ref = db.reference("users")
    users_data=ref.get()

    if users_data:
        for userid, userinfo in users_data.items():
            if userinfo.get("email","").lower() == email.lower():
                show_popup(title="Error",message="Email Already Exists!")

            userid=random.randint(1000,9999)
            password=random.randint(1000,9999)

            ref = db.reference(f"users/{userid}")
            ref.set({
                "name":name,
                "email":email,
                "password":password,
                "contact":contact                
            })
            show_popup(title="Valid",message="Updated to Database")

            group_member_name_input.text = ""
            group_member_email_input.text = ""
            group_member_contact_input.text = ""

            if name  == "":
                            show_popup(text="Enter Missing Fields",message="Name is Missing!")
                            add_members()
                        
            if email == "":
                            show_popup(text="Enter Missing Fields",message="Email is Missing")
                            add_members()

            if contact == "":
                            show_popup(text="Enter Missing Fields",message="Contact is Missing!")
                            add_members()
            
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
            sender_password = "lzuz alep whft sfhn"
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
            sm.current = "Dashboard"

        elif otp_input.text == "":
            show_popup("Error","OTP Not Entered")
            write_email_and_password(None, user_data["email"], user_data["password"], user_data["name"])
        else:
            show_popup("Error", "Invalid OTP")

    layout.add_widget(Button(text="Verify OTP", on_press=verify_otp))

    def go_to_login(instance):
        sm.current = "Log In"

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
        email_text = email_field.text.strip()
        password_text = password_field.text.strip()

        if not email_text or not password_text:
            show_popup("Error", "Please enter Email and Password")
            return

        ref = db.reference("users")
        users_data = ref.get()

        if users_data:
            for userid, user_info in users_data.items():
                if email_text == user_info.get("email") and password_text == user_info.get("password"):
                    show_popup("Success", f"Welcome {user_info.get('name')}!")
                    sm.current = "Dashboard"
                    return
            show_popup("Error", "Email or Password is Invalid")
        else:
            show_popup("Error", "No users found. Please Sign Up first.")

    layout.add_widget(Button(text="Submit", on_press=login_check))

    def go_to_signup(instance):
        sm.current = "Sign Up"

    layout.add_widget(Button(text="Back to Sign Up", on_press=go_to_signup))

    return layout


# ---------------- DASHBOARD ----------------
def build_dashboard():
    layout = FloatLayout(size_hint=(1,1))
    layout.add_widget(Label(text="Welcome to Splitwise!", font_size=50, pos_hint={"center_x":0.5,"top":1}))

    info_float = FloatLayout(size_hint=(None,None), size=(800,120), pos_hint={"center_x":0.5,"top":0.85})

    owe_layout = BoxLayout(orientation="vertical", size_hint=(None,None), size=(250,100), pos_hint={"center_x":0.35,"center_y":0.5})
    owe_layout.add_widget(Label(text="You Owe:", font_size=28))
    owe_layout.add_widget(Label(text=str(0), font_size=28))
    info_float.add_widget(owe_layout)

    others_owe_layout = BoxLayout(orientation="vertical", size_hint=(None,None), size=(250,100), pos_hint={"center_x":0.65,"center_y":0.5})
    others_owe_layout.add_widget(Label(text="Others Owe:", font_size=28))
    others_owe_layout.add_widget(Label(text=str(0), font_size=28))
    info_float.add_widget(others_owe_layout)

    layout.add_widget(info_float)

    button_bar = BoxLayout(
        orientation="horizontal",
        size_hint=(0.95, None),
        height=120,
        spacing=50,
        pos_hint={"center_x":0.5, "y":0.05}
    )
    add_expense_button = Button(
        text="Add Expense",
        font_size=32,
        size_hint=(1,None),  
        height=120
    )
    add_group_member_button = Button(
        text="Add Member",
        font_size=32,
        size_hint=(1,None),
        height=120
    )

    button_bar.add_widget(add_expense_button)
    button_bar.add_widget(add_group_member_button)
    layout.add_widget(button_bar)

    def go_expense(instance):
        sm.current = "Add Expense"

    def go_member(instance):
        sm.current = "Add Member"

    add_expense_button.bind(on_press=go_expense)
    add_group_member_button.bind(on_press=go_member)

    return layout

# ---------------- ADD EXPENSE SCREEN ----------------
def build_add_expense_screen():
    layout = BoxLayout(orientation="vertical", spacing=30, padding=60)
    
    payer_input = TextInput(hint_text="Who Paid", size_hint=(1,None), height=70, font_size=28)
    description_input = TextInput(hint_text="Description", size_hint=(1,None), height=70, font_size=28)
    amount_input = TextInput(hint_text="Amount", size_hint=(1,None), height=70, font_size=28)
    
    layout.add_widget(payer_input)
    layout.add_widget(description_input)
    layout.add_widget(amount_input)
    
    submit_button = Button(text="Submit Expense", size_hint=(1,None), height=80, font_size=32)
    layout.add_widget(submit_button)
    
    back_button_expense = Button(text="Back to Dashboard", size_hint=(1,None), height=80, font_size=32)
    def back_to_dashboard_expense(instance):
        sm.current = "Dashboard"

    back_button_expense.bind(on_press=back_to_dashboard_expense)
    layout.add_widget(back_button_expense)
    
    return layout

# ---------------- ADD MEMBER SCREEN ----------------
def build_add_group_member_screen():
    global group_member_name_input, group_member_email_input, group_member_contact_input
    layout = BoxLayout(orientation="vertical", spacing=30, padding=60)
    
    group_member_name_input = TextInput(hint_text="Enter Person Name", size_hint=(1,None), height=70, font_size=28)
    group_member_email_input = TextInput(hint_text="Enter Email", size_hint=(1,None), height=70, font_size=28)
    group_member_contact_input = TextInput(hint_text="Enter Contact", size_hint=(1,None), height=70, font_size=28)
    
    layout.add_widget(group_member_name_input)
    layout.add_widget(group_member_email_input)
    layout.add_widget(group_member_contact_input)
    
    submit_button = Button(text="Submit Member", size_hint=(1,None), height=80, font_size=32,on_press=add_members)
    layout.add_widget(submit_button)

    back_button_member = Button(text="Back to Dashboard", size_hint=(1,None), height=80, font_size=32)
    
    def back_to_dashboard_member(instance):
        sm.current = "Dashboard"
    back_button_member.bind(on_press=back_to_dashboard_member)
    layout.add_widget(back_button_member)
    
    return layout

# ---------------- SCREENS ----------------

sign_up_screen = Screen(name="Sign Up")
sign_up_screen.add_widget(build_signup_layout())

login_screen = Screen(name="Log In")
login_screen.add_widget(build_login_layout())

dashboard_screen = Screen(name="Dashboard")
dashboard_screen.add_widget(build_dashboard())

add_expense_screen = Screen(name="Add Expense")
add_expense_screen.add_widget(build_add_expense_screen())

add_member_screen = Screen(name="Add Member")
add_member_screen.add_widget(build_add_group_member_screen())

# Add screens to ScreenManager
sm.add_widget(sign_up_screen)
sm.add_widget(login_screen)
sm.add_widget(dashboard_screen)
sm.add_widget(add_expense_screen)
sm.add_widget(add_member_screen)

# ---------------- APP ----------------
class Splitwise(App):
    def build(self):
        return sm

if __name__ == "__main__":
    Splitwise().run()