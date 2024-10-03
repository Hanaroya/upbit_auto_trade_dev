import requests
import smtplib
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders
import get_properties as gp
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

myprops = gp.get_properties()
def post_message(channel, text):
    client = WebClient(token=myprops['SLACK_KEY'])
    try:
        response = client.chat_postMessage(
            channel=channel, #채널 id를 입력합니다.
            text=text
        )
    except SlackApiError as e:
        assert e.response["error"]
        
def regular_percent_message(percent:float, coin:str, channel:str):
    if ((0 < percent % 1 < 0.1) or (0.9 < percent % 1 < 1)) and percent > 1:  post_message(channel=channel, text="{}: {}% up".format(coin, round(percent, 3)))
    if ((0 < percent % 1 < 0.1) or (0.9 < percent % 1 < 1)) and percent < -1:  post_message(channel=channel, text="{}: {}% down".format(coin, round(percent, 3)))

def send_mail(send_from, send_to, subject, message, files=[], server="localhost", port=587, username='', password='', use_tls=True):
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(message))

    for path in files:
        part = MIMEBase('application', "octet-stream")
        with open(path, 'rb') as file:
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        'attachment; filename="{}"'.format(Path(path).name))
        msg.attach(part)

    smtp = smtplib.SMTP(server, port)
    if use_tls:
        smtp.starttls()
    smtp.login(username, password)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.quit()