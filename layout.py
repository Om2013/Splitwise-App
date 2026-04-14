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
from email.mime.multipart import MIMEMultipart
from kivy.uix.spinner import Spinner 
from kivy.uix.gridlayout import GridLayout
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

signed_in_name=""
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
    ref.push({
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
                return 

            userid=random.randint(1000,9999)
            password=random.randint(1000,9999)

        ref = db.reference(f"users/{userid}")
        ref.push({
            "name":name,
            "email":email,
            "password":password,
            "contact":contact                
        })
        show_popup(title="Valid",message="Updated to Database")

        group_member_name_input.text = ""
        group_member_email_input.text = ""
        group_member_contact_input.text = ""

        send_email_to_new_user(email)

#------------------ADD EXPENSE------------------
def add_expense(instance):
    
    global group_member

    description=description_input.text.strip()
    amount=amount_input.text.strip()
    who_paid=who_paid_spinner.text
    group_member=fetch_group_members()

    group_member=[m for m in group_member if m and isinstance(m,str)]

    if not description or not amount or not who_paid:
        show_popup("Invalid","All Fields Not Entered!")
        return 
    
    if not group_member:
        show_popup("Invalid","Group Member Not Found!")
        return 
    try:
        
    
        amount=float(amount)
    except:
        show_popup("Error","Invalid Amount")
        return 
    
    split_amount=round(amount/len(group_member),2)
    split_dict={}
    for member in group_member:
        split_dict[str(member)]=split_amount

    #split_dict=dict.fromkeys(group_member,split_amount)
    try:
        ref=db.reference("transactions")
        ref.push({
            "transaction_id":random.randint(1000,9999),
            "description":description,
            "amount":amount,
            "who_paid":who_paid,
            "split":split_dict
        })

        show_popup("Valid","Expense has been added!")
        description_input.text = ""
        amount_input.text=""
        who_paid_spinner.text = "Select Member"
    except Exception as e:
        print("firebase_error")
        show_popup("Error",str(e))

#-------------------FETCH GROUP MEMBERS-------------#
def fetch_group_members():
    global group_member
    group_member=[]
    ref=db.reference("users")
    users_data=ref.get()
    for userid,userinfo in users_data.items():
        name=userinfo.get("name")
        group_member.append(name)
    return group_member

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
"""

            msg = MIMEMultipart(body)
            msg["subject"] = subject 
            msg["From"] = sender_email 
            msg["To"] = receiver_email 
            msg.attach(MIMEText(body,"plain"))
            try:
                server = smtplib.SMTP("smtp.gmail.com",587)
                server.starttls()
                server.login(sender_email,sender_password)
                server.sendmail(sender_email,receiver_email,msg.as_string())
                server.quit()
                show_popup("OTP Sent!","Please check your email")

            except:
                show_popup("Error","Failed to Send the Email!")

            show_popup("Success", "OTP has been sent to your email!")

        except Exception as e:
            show_popup("Error", f"Failed to send email:\n{str(e)}")

    layout.add_widget(Button(text="Send OTP", on_press=send_otp))

    otp_input = TextInput(hint_text="Enter OTP", multiline=False)
    layout.add_widget(otp_input)

    def verify_otp(instance):
        if otp_input.text == "":
            show_popup("Error","OTP Not Entered")

        elif otp_input.text == user_data["otp"]:
            show_popup("Success", "OTP Verified Successfully!")
            write_email_and_password(None, user_data["email"], user_data["password"], user_data["name"])
            sm.current = "Dashboard"

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
                    global signed_in_name
                    signed_in_name=user_info.get("name")
                    dashboard_screen.clear_widgets()
                    dashboard_screen.add_widget(build_dashboard())
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
    global owe_amount_label, others_owe_amount, signed_in_name
    layout = FloatLayout(size_hint=(1,1))
    layout.add_widget(Label(text="Welcome to Splitwise!", font_size=50, pos_hint={"center_x":0.5,"top":1}))

    info_float = FloatLayout(size_hint=(None,None), size=(800,120), pos_hint={"center_x":0.5,"top":0.85})

    owe_layout = BoxLayout(orientation="vertical", size_hint=(None,None), size=(250,100), pos_hint={"center_x":0.35,"center_y":0.5})
    owe_label=Label(text="You Owe:", font_size=28)
    owe_layout.add_widget(owe_label)
    owe_amount_label=Label(text=str(0), font_size=28)
    owe_layout.add_widget(owe_amount_label)
    info_float.add_widget(owe_layout)

    others_owe_layout = BoxLayout(orientation="vertical", size_hint=(None,None), size=(250,100), pos_hint={"center_x":0.65,"center_y":0.5})
    others_owe_label=Label(text="Others Owe:", font_size=28)
    others_owe_amount=Label(text=str(0), font_size=28)
    others_owe_layout.add_widget(others_owe_label)
    others_owe_layout.add_widget(others_owe_amount)
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


    add_expense_button.bind(on_press=go_expense)
    add_group_member_button.bind(on_press=go_member)

    if signed_in_name:
        i_owe,others_owe_me=calculate_balance()
        owe_amount_label.text=(str(i_owe))
        others_owe_amount.text=(str(others_owe_me))
    else:
        i_owe=0.0
        others_owe_me=0.0

    group=fetch_group_members()
    num_of_length=len(group)
    

    columns=3+num_of_length

    table=GridLayout(cols=columns,size_hint_y=(None),spacing=5,padding=5)
    headers=["description","amount","who_paid"]+group
    for col in headers:
        table.add_widget(Label(text=col,color=(255,255,0),size_hint_y=None, height=40))

    
    ref = db.reference("transactions")
    data=ref.get()

    print(data)
    i_owe=0.0
    others_owe=0.0

    if not data or not isinstance(data,dict):
        layout.add_widget(Label(text="No Transactions Yet!"))
        return layout 
    
    else:
        for transaction_id, transaction_data in data.items():
            description=transaction_data.get("description","")
            amount=transaction_data.get("amount","")
            who_paid=transaction_data.get("who_paid","")

            table.add_widget(Label(text=str(description),size_hint_y=None,color="blue",height=40))
            table.add_widget(Label(text=f"{who_paid}"),size_hint_y=None,color="red",height=40)
            table.add_widget(Label(text=f"{amount}",size_hint_y=None, color="pink",height=40))

            split=transaction_data.get("split",{})
            for member in group:
                share=split.get(member,"") 
                if isinstance(share,(int,float)):
                    share_text=f"{share:.2f}"
                elif share== "" or share is None:
                    share_text="-"
                else:
                    try:
                        share_text=f"{float(share):.2f}"
                    except Exception:
                        share_text=str(share)          
                table.add_widget(Label(text=share_text,size_hint_y=None,color="blue",height=40))

                layout.add_widget(table)            


    return layout

def calculate_balance():
    data=db.reference("transactions").get()
    i_owe=0.0
    others_owe_me=0.0
    if not data:
        return i_owe,others_owe_me
    if not isinstance(data,dict):
        print("Invalid Data Format",data)
        return 
    
    for data_id,data_info in data.items():
        who_paid=data_info.get("who_paid","")

        if who_paid != signed_in_name:
            i_owe=i_owe+data_info["split"][signed_in_name]

        if who_paid == signed_in_name:
            split_data=data_info["split"]
            
            for name,amount in split_data.items():
                if name != signed_in_name:
                    others_owe_me+=amount
    return round(i_owe,2),round(others_owe_me,2)


def go_expense(instance):
    sm.transition.direction="left"
    sm.current = "Add Expense"

def go_member(instance):
    sm.transition.direction="right"
    sm.current = "Add Member"


# ---------------- ADD EXPENSE SCREEN ----------------
def build_add_expense_screen():
    global description_input, amount_input, who_paid_spinner

    layout = BoxLayout(orientation="vertical", spacing=30, padding=60)
    group=fetch_group_members()
    who_paid_spinner = Spinner(
    text="Who Paid",
    values=group,
    size_hint=(0.8, None),
    pos_hint={"center_x":0.5, "y":0.05}
)
    description_input = TextInput(hint_text="Description", size_hint=(1,None), height=70, font_size=28)
    amount_input = TextInput(hint_text="Amount", size_hint=(1,None), height=70, font_size=28)

    layout.add_widget(who_paid_spinner)
    layout.add_widget(description_input)
    layout.add_widget(amount_input)
    
    
    submit_button = Button(text="Submit Expense", size_hint=(1,None), height=80, font_size=32,on_press=add_expense)
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

def send_email_to_new_user(email):
    sender_email = "omradhakrishnan2013@gmail.com"
    sender_password = "lzuz alep whft sfhn"
    subject = "Added as a Group Member in Splitwise App"

    ref = db.reference("users")
    users_data=ref.get()
    password = None 
    if users_data:
        for userid, userinfo in users_data.items():
            if userinfo["email"] == email:
                password = userinfo["password"] 
                break 
    if not password:
         show_popup("Error","Password Not Found")
         return 
    
    body = f"You Have Been Added as a Group Member in Splitwise. You can now login with this email : {email},  and password {password} "
    
    msg = MIMEMultipart(body)
    msg["subject"] = subject 
    msg["From"] = sender_email 
    msg["To"] = email 
    msg.attach(MIMEText(body,"plain"))
    try:
        server = smtplib.SMTP("smtp.gmail.com",587)
        server.starttls()
        server.login(sender_email,sender_password)
        server.sendmail(sender_email,email,msg.as_string())
        server.quit()
        show_popup("Sent","Email Notification Sent to New Member!")
    except:
         show_popup("Error","Failed to Send the Email!")
         

            
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
