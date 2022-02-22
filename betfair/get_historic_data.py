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
import time

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


# setup logging
logging.basicConfig(level=logging.INFO,filemode="w",filename=f"{HOME}/script_stat/get_historic_data/status.log")  # change to DEBUG to see log all updates

with open(f"{HOME}/pass_info.json","r") as f:
    pass_info = json.load(f)


curr_date = datetime(2018,11,3)
day = timedelta(days=1)
end_date = datetime(2022,2,6)

while curr_date <= end_date:
    try:
        # create trading instance
        trading = betfairlightweight.APIClient(pass_info["betfair"]["username"], pass_info["betfair"]["password"], app_key=pass_info["betfair"]["app_key"],certs=f'{HOME}/login_tokens/betfair')
        
        # login
        trading.login()
    except:
        print("Loging attempt failed sleeping for 1 minute")
        time.sleep(60)
        continue

    # get file list
    try:
        while curr_date <= end_date:
            data_base_dir = f"{HOME}/database/tennis/{curr_date.strftime('%d_%m_%Y')}"
            if not os.path.exists(data_base_dir):
                os.mkdir(data_base_dir)
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
            
            if len(file_list) > 0:
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
        logging.info(f"Removing directory {data_base_dir}")
        shutil.rmtree(data_base_dir)
        os.system('clear')
        print("taking rest of 1 minute")
        time.sleep(60)


    try:
        trading.logout()
    except:
        pass
    
    send_email("adiga23@gmail.com",f"Database Download interrupted {datetime.now().strftime('%d/%m/%Y')}",f"Downloaded till {curr_date.strftime('%d/%m/%Y')}")
