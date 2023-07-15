#import schedule
import time
import csv
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Function to read nurse data from a CSV file
def read_nurse_data(file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        nurses = list(reader)
    return nurses

# Function to print nurse details, ADD YOUR OWN LOGIC HERE DEPENDING ON YOUR TYPE OF FILE
def print_nurse_details(nurse):
    print(f"Name: {nurse['name']}")
    print(f"Email: {nurse['email']}")
    print(f"License Issue Date: {nurse['license_issue_date']}")
    print()

# Function to send email notifications
def send_email_notification(nurse_name, nurse_email, days_until_expiration):
    sender_email = "<sender_email>" # Put the email address of your preferred sender
    sender_password = "<sender_password" #Update with the right password
    smtp_server = "<sender_server>" # Update with your preferred SMTP server

    subject = "NURSE LICENSE EXPIRATION REMINDER"
    if days_until_expiration in range(0, 60):
        message = f"Dear {nurse_name}, \n\nYour license will expire in {days_until_expiration} days.\nPlease consider making plans to renew your license.\n\nBest regards,\n<Person_Sending>\n<Designation>"
    elif days_until_expiration < 0:
        message = f"Dear {nurse_name}, \n\nYour license has already expired!\nPlease renew your license as asoon as possible.\n\nBest regards,\n<Person_Sending>\n<Designation>"
    else:
        message = f"Dear {nurse_name}, \n\nYour license is in good condition!.\n\nBest regards,\n<Person_Sending>\n<Designation>"

    # Construct the email
    email = MIMEMultipart()
    email['From'] = sender_email
    email['To'] = nurse_email
    email['Subject'] = subject
    email.attach(MIMEText(message, 'plain'))

    # Connect with the SMTP server to send the email
    with smtplib.SMTP(smtp_server, 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(email)


# Function to send notification
def send_notification(nurse, days_until_expiration):
    if days_until_expiration in range(0, 60):
        print(f"Dear {nurse['name']}, your license will expire in {days_until_expiration} days.")
    elif days_until_expiration < 0:
        print(f"Dear {nurse['name']}, \n\nYour license has already expired!")
    else:
        print(f"Dear {nurse['name']}, \n\nYour license is in good condition!")
    print()


# Sample nurse data file path (update with your file path)
nurse_data_file = 'nurse_data.csv'

# Read data from a given csv file
nurses = read_nurse_data(nurse_data_file)

# Check license expiration and send notifications
for nurse in nurses:
    issue_date = datetime.datetime.strptime(nurse["license_issue_date"], "%Y-%m-%d").date()
    expiration_date = issue_date + datetime.timedelta(days=365)
    days_until_expiration = (expiration_date - datetime.date.today()).days

    # Print nurse details
    print_nurse_details(nurse)

    send_notification(nurse, days_until_expiration)

    send_email_notification(nurse['name'], nurse['email'], days_until_expiration)


# print(f"Code Success!!")