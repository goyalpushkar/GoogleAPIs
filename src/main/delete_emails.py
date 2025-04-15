'''
pip install --upgrade google-api-python-client

https://developers.google.com/gmail/api/quickstart/python
https://www.systoolsgroup.com/imap/
https://docs.python.org/3/library/imaplib.html#imaplib.IMAP4.list

'''
import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import imaplib
import email
from email.header import decode_header

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail']


def delete_message(service, user_id, message_id):
  """Delete a Message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value me
    can be used to indicate the authenticated user.
    message_id: ID of Message to delete.
  """
  try:
    service.users().messages().delete(userId=user_id, id=message_id).execute()
    print(f'Message with ID: {message_id} deleted successfully.')
  except HttpError as error:
    print(f'An error occurred: {error}')
    return error


def connect_to_gmail(username, password, tokens_path):
    # create an IMAP4 class with SSL
    # Gmail                            Server                Authentication          Port
    # SMTPServer(Outgoing Messages)    smtp.gmail.com        SSL                     465
    #                                  smtp.gmail.com        StartTLS                587
    # IMAPServer(Incoming Messages)    imap.gmail.com        SSL                     993
    # smtp.gmail.com:465 - socket.gaierror: [Errno 11001] getaddrinfo failed
    # imap = imaplib.IMAP4_SSL("smtp.gmail.com:465")
    # # authenticate
    # imap.login(username, password)
    # print(imap.list())

    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(tokens_path):
        creds = Credentials.from_authorized_user_file(tokens_path, SCOPES)

    print(creds)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(tokens_path, 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])

        if not labels:
            print('No labels found.')
            return
        print('Labels:')
        for label in labels:
            print(label['name'])

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')


def check_email(imap, type):
    # select the mailbox I want to delete in
    # if you want SPAM, use imap.select("SPAM") instead
    num_of_emails =  imap.select(type)   # "INBOX"
    # Returned data is the count of messages in mailbox
    return num_of_emails


def search_email(imap, pattern):

    # search(charset, criterion)
    # charset may be None, in which case no CHARSET will be specified in the request to the server

    # # search for specific mails by sender
    # status, messages = imap.search(None, 'FROM "googlealerts-noreply@google.com"')
    #
    # # to get mails by subject
    # status, messages = imap.search(None, 'SUBJECT "Thanks for Subscribing to our Newsletter !"')
    #
    # # to get mails after a specific date
    # status, messages = imap.search(None, 'SINCE "01-JAN-2020"')
    #
    # # to get mails before a specific date
    # status, messages = imap.search(None, 'BEFORE "01-JAN-2020"')

    status, messages = imap.search(None, pattern)
    return status, messages


def gmail_handling():
    # Connect to Gmail
    token_path = "gmail_api_tokens.json"
        # 'gmail_api_client_secret_468031038030-dtq1r0jkkoej0ubjefp5pplsatlkkd0t.apps.googleusercontent.com.json'
    imap_handler = connect_to_gmail(username, password, token_path)

    # Get Count of emails
    num_of_emails = check_email(imap_handler, "INBOX")
    print(f"num_of_emails: {num_of_emails}\n")

    # Search specific emails
    status, messages = search_email(imap_handler, 'SUBJECT "Airflow alert: <TaskInstance: oms_allocation_fr"')
    print(f"status: {status}\n"
          f"messages: {messages}")


if __name__ == '__main__':
    # account credentials
    username = "pgoyal@cswg.com"
    password = "20One$Garv"
    gmail_handling()