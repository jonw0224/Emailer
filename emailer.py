################################################################################
# Author: Jonathan Weaver
# Written with assistance from granite4.1:8b LLM model under Ollama
# Date: 06/30/2026
# Version: 1.02
# Revisons:
#   06/26/2026 - 1.00 - Created script, configuration file, email list file, and 
#                       campaign file 
#   06/27/2026 - 1.01 - Changed so that the email list file is specified with
#                       each campaign record in the campaign file. Also added
#                       field merge functionality so that the subject and email
#                       body contents can be personalized with each email. The
#                       field from the email list file is included in the
#                       subject or the email body template as {{FieldName}} and
#                       will be substituted by the actual value.
#   06/30/2026 - 1.02 - Added mail merge functionality so that the body template
#                       can use fields from the campaign list.
#
# MIT License
#
# Copyright (c) 2026 Jonathan Weaver
#
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal 
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
# SOFTWARE.
################################################################################


################################################################################
# Imports
################################################################################
import csv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from configparser import ConfigParser
import time
from datetime import datetime
import re
import argparse

################################################################################
# Global Variables / Constants
################################################################################
CONFIGFILEPATH = "smtp.conf"
EMAILCAMPAIGNPATH = "email_campaigns.csv"

################################################################################
# Load the configuration file given the file path
################################################################################
def load_config(file_path):
    """Load SMTP server configuration from a .conf file."""
    parser = ConfigParser()
    parser.read(file_path)
    
    smtp_server = parser.get('SMTP_SERVER', 'server')
    smtp_port = parser.getint('SMTP_SERVER', 'port')
    username = parser.get('AUTHENTICATION', 'username')
    password = parser.get('AUTHENTICATION', 'password')
    use_ssl = parser.getboolean('SMTP_SERVER', 'use_ssl')  # Read the SSL configuration
    
    sender_name = parser.get('SUBJECT_AND_SENDER', 'sender_name')
    sender_email = parser.get('SUBJECT_AND_SENDER', 'sender_email')
    email_delay = parser.getint('SMTP_SERVER', 'delay_between_emails_seconds')
    
    return smtp_server, smtp_port, username, password, use_ssl, sender_name, sender_email, email_delay

################################################################################
# Load the email list from a CSV file given the file path
################################################################################
def load_email_list(file_path):
    """Load the email list from a CSV file."""
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return [row for row in reader]

################################################################################
# Load the campaigns list from a CSV file given the file path
################################################################################
def load_campaigns(file_path):
    """Load campaign data from a CSV file."""
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return [row for row in reader]

################################################################################
# Load the email HTML body template given the file path
################################################################################
def read_html_template(html_file_path):
    """Read the HTML template from a file and return its content."""
    with open(html_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    return html_content

################################################################################
# Merge the email template with the fields specified in the email list
################################################################################
def merge_email_data(html_template, email_data):
    """Perform find-and-replace for tags in the HTML template using data from email_data."""
    # Use regex to replace placeholders like {{FirstName}} with actual values
    html_content = html_template
    for key, value in email_data.items():
        placeholder = "{{" + key + "}}"
        html_content = re.sub(placeholder, value, html_content)
    return html_content
    
################################################################################
# Send the email using the SMTP server
################################################################################
def send_email(to_addr, subject, body_html, smtp_server, smtp_port, username, password, use_ssl, sender_name, sender_email):
    """Send an email using the specified SMTP server and security protocol."""
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['To'] = to_addr
    msg['From'] = f"{sender_name} <{sender_email}>"
    
    # Attach the HTML body
    html = MIMEText(body_html, 'html')
    msg.attach(html)

    try:
        if use_ssl:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection
                server.ehlo()
                server.login(username, password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()  # Secure the connection using STARTTLS
                server.ehlo()
                server.login(username, password)
                server.send_message(msg)
        print(f"Email sent to {to_addr}")
    except Exception as e:
        print(f"Failed to send email to {to_addr}: {e}")

################################################################################
# Main Program
################################################################################
def main():
    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser(
        prog='GALPEmailScript.py',
        description='Send Email campaigns using an SMTP server' )
    ap.add_argument( "--conf", default = CONFIGFILEPATH, help = "Configuration file containing the SMTP and email sender information. Default " + CONFIGFILEPATH )
    ap.add_argument( "--campaign", default = EMAILCAMPAIGNPATH, help = "CSV file containing the email campaign information. Default " + EMAILCAMPAIGNPATH)

    options = ap.parse_args()

    # Load configurations from smtp.conf
    smtp_server, smtp_port, username, password, use_ssl, sender_name, sender_email, email_delay = load_config(options.conf)
    
    campaigns = load_campaigns(options.campaign)
    
    today_date = datetime.now().strftime('%Y-%m-%d')  # Get today's date in 'YYYY-MM-DD' format
    matching_campaign = next((c for c in campaigns if c['Date'].strip() == today_date), None)
    
    if not matching_campaign:
        print("No matching campaign date found for today.")
        return
    
    html_template_path = matching_campaign['Body']
    email_list_file_path = matching_campaign['EmailList']

    emails = load_email_list(email_list_file_path)
    
    with open(html_template_path, 'r', encoding='utf-8') as template_file:
        email_template = template_file.read()
    
    # Send emails
    for recipient in emails:
        # Use a full To: line
        full_name = f"{recipient['FirstName']} {recipient['LastName']}"
        formatted_to_email = f"{full_name} <{recipient['Email']}>"
        
        # Personalize the email body
        email_body_html = merge_email_data(email_template, recipient)
        email_body_html = merge_email_data(email_body_html, matching_campaign)
        
        # Get the email subject. Personalize the email subject
        subject_template = matching_campaign['Subject'].strip()  # Use the subject from the matched campaign
        subject = merge_email_data(subject_template, recipient)
        
        try:
            send_email(formatted_to_email, subject, email_body_html, smtp_server, smtp_port, username, password, use_ssl, sender_name, sender_email)
        except Exception as e:
            print(f"An error occurred while sending an email to {formatted_to_email}: {e}")
        
        # Add a delay between sending each email
        time.sleep(email_delay)

################################################################################
# If Script Directly called, run main()
################################################################################
if __name__ == "__main__":
    main()
    
