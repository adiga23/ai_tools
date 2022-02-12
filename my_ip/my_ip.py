import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from datetime import datetime

HOME = os.getenv("HOME")

ip_file = f"{HOME}/script_stat/my_ip/current_ip"

with open(f"{HOME}/pass_info.json","r") as f:
    pass_info = json.load(f)


def send_email(to_email,subject,msg):
    HOME = os.getenv("HOME")
    with open(f"{HOME}/pass_info.json",'r') as f:
        pass_info = json.load(f)
    python_account = pass_info["pygmail"]["username"]
    python_password = pass_info["pygmail"]["password"]

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = python_account
    message["To"] = to_email
    message.attach(MIMEText(msg,"html"))
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com',465)
        server.ehlo()
        server.login(python_account,python_password)
        server.sendmail(python_account,to_email,message.as_string())
        server.close()
        success = True
    except:
        success = False
    return(success)

try:
    with open(ip_file,"r") as f:
        lines = f.readlines()
        prev_ip = lines[0]
except:
    prev_ip = ""

current_ip=os.popen("curl ifconfig.me").read()

if current_ip != prev_ip:
    print(current_ip)
    with open(ip_file,"w") as f:
        f.write(current_ip) 

    send_email(pass_info["mygmail"]["username"],f"My current IP {datetime.now().strftime('%d/%m/%Y:%H:%M')}",f"My current ip is : {current_ip}")
    
else:
    print("ip is the same")

