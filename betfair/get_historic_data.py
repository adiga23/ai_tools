import logging
import betfairlightweight
import os
from datetime import timedelta
from datetime import datetime
import shutil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json

HOME = os.getenv("HOME")

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


"""
Historic is the API endpoint that can be used to
download data betfair provide.
https://historicdata.betfair.com/#/apidocs
"""

# setup logging
logging.basicConfig(level=logging.INFO,filemode="w",filename=f"{HOME}/script_stat/get_historic_data/status.log")  # change to DEBUG to see log all updates

# create trading instance
trading = betfairlightweight.APIClient("adiga23@gmail.com", "Aar@07122014", app_key="gTjbUG3i87ZDyCw8",certs=f'{HOME}/betfair_keys')

# login
trading.login()

curr_date = datetime(2015,4,1)
day = timedelta(days=1)
end_date = datetime(2015,5,30)

# get file list
try:
    while curr_date <= end_date:
        file_list = trading.historic.get_file_list(
            "Tennis",
            "Basic Plan",
            from_day=curr_date.day,
            from_month=curr_date.month,
            from_year=curr_date.year,
            to_day=curr_date.day,
            to_month=curr_date.month,
            to_year=curr_date.year,
            market_types_collection=[],
            countries_collection=[],
            file_type_collection=[],
        )
        os.system("clear")
        logging.info(f"Number of files for {curr_date.strftime('%d/%m/%Y')} : {len(file_list)}")
        
        data_base_dir = f"{HOME}/database/tennis/{curr_date.strftime('%d_%m_%Y')}"
        if len(file_list) > 0:
            if not os.path.exists(data_base_dir):
                os.mkdir(data_base_dir)
            os.chdir(data_base_dir)
            print(f"Downloading for {curr_date.strftime('%d/%m/%Y')} : 0%")
            for count,file in enumerate(file_list):
                download = trading.historic.download_file(file_path=file)
                shutil.move(download,f"file_{count}.bz2")
                os.system("clear")
                print(f"Downloading for {curr_date.strftime('%d/%m/%Y')} : {((count+1)/len(file_list))*100:2.2f}")
        else:
            print(f"Nothing to download for {curr_date.strftime('%d/%m/%Y')}")

        curr_date += day
except:
    pass

try:
    trading.logout()
except:
    pass

curr_date -= day
send_email("adiga23@gmail.com",f"Database Download interrupted {datetime.now().strftime('%d/%m/%Y')}",f"Downloaded till {curr_date.strftime('%d/%m/%Y')}")
