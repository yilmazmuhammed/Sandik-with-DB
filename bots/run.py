from datetime import date

from bots.mail import send_mail_all_data
from bots.pay_contributions_from_other import pay_automatic_instructions_in_website

if __name__ == "__main__":
    if date.today().day in [1, 25]:
        pay_automatic_instructions_in_website()
    send_mail_all_data()