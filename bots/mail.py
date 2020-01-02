import smtplib

from views.backup import csv_list_backup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def sendemail(from_addr, to_addr_list,
              subject, message,
              login='yardimlasmasandigi@yaani.com', password='Yardimlasma01',
              smtpserver='smtp.yaanimail.com:587'):
    msg = MIMEMultipart()
    msg["From"] = from_addr
    msg["To"] = ','.join(to_addr_list)
    msg["Subject"] = subject
    body = MIMEText(message, "plain")
    msg.attach(body)

    server = smtplib.SMTP(smtpserver)
    server.starttls()
    server.login(login, password)
    problems = server.sendmail(from_addr, to_addr_list, msg.as_string())
    server.quit()
    return problems


def send_mail_all_data():
    sendemail(from_addr='yardimlasmasandigi@yaani.com',
              to_addr_list=['halil_yilmaz1997@hotmail.com'],
              subject='Yardımlaşma Sandığı - Yedekleme',
              message="\n".join(csv_list_backup.all_data_list()))


# import schedule
# import time  # to make system sleep after avery call.

if __name__ == "__main__":
    send_mail_all_data()
    # schedule.every(1).weeks.do(send_mail_all_data)
    # while True:
    #     schedule.run_pending()
    #     time.sleep(2)  # System will rest for 2 seconds
