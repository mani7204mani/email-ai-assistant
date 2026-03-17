import os
import base64
import json
import requests
import streamlit as st
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import re

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_client_config():
    # Try Streamlit secrets
    try:
        if "google_credentials" in st.secrets:
            client_id     = st.secrets["google_credentials"]["client_id"]
            client_secret = st.secrets["google_credentials"]["client_secret"]
            if client_id and client_secret:
                return {
                    "client_id":     client_id,
                    "client_secret": client_secret,
                }
            else:
                raise Exception("client_id or client_secret is empty in secrets!")
        else:
            raise Exception("google_credentials section not found in secrets!")
    except Exception as e:
        # If secrets fail, try credentials.json
        if os.path.exists('credentials.json'):
            with open('credentials.json') as f:
                data = json.load(f)
                key  = 'web' if 'web' in data else 'installed'
                return {
                    "client_id":     data[key]["client_id"],
                    "client_secret": data[key]["client_secret"],
                }
        # Show exact error so we know what's wrong
        raise Exception(f"Secrets error: {str(e)}")
def get_auth_url(redirect_uri):
    config = get_client_config()
    
    from urllib.parse import urlencode
    
    params = {
        "client_id":     config["client_id"],
        "redirect_uri":  redirect_uri,
        "response_type": "code",
        "scope":         "https://www.googleapis.com/auth/gmail.modify",
        "access_type":   "offline",
        "prompt":        "consent"
    }
    
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)
    return auth_url

def get_service_from_code(code, redirect_uri):
    config = get_client_config()

    # Exchange code for token directly — no Flow object needed
    token_response = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code":          code,
            "client_id":     config["client_id"],
            "client_secret": config["client_secret"],
            "redirect_uri":  redirect_uri,
            "grant_type":    "authorization_code",
        }
    )

    token_data = token_response.json()

    if "error" in token_data:
        raise Exception(f"Token error: {token_data['error']} - {token_data.get('error_description', '')}")

    creds = Credentials(
        token=token_data["access_token"],
        refresh_token=token_data.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=config["client_id"],
        client_secret=config["client_secret"],
        scopes=SCOPES
    )

    return build('gmail', 'v1', credentials=creds)
def clean_email_body(text):
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove extra blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()
def get_unread_emails(service, max_results=10):
    
    results  = service.users().messages().list(
        userId='me', labelIds=['INBOX'], q='is:unread', maxResults=max_results
    ).execute()
    messages = results.get('messages', [])
    emails   = []

    for msg in messages:
        msg_data = service.users().messages().get(
            userId='me', id=msg['id'], format='full'
        ).execute()

        headers = msg_data['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender  = next((h['value'] for h in headers if h['name'] == 'From'),    'Unknown')

        body    = ""
        payload = msg_data['payload']
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
                        break
        elif 'body' in payload and payload['body'].get('data'):
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')

        emails.append({
            'id':      msg['id'],
            'subject': subject,
            'sender':  sender,
            'body':    clean_email_body(body)   # ← wrap with clean_email_body
        })

    return emails

def send_email_html(service, to, subject, body, signature, original_sender):
    linkedin_line = f'<a href="{signature["linkedin"]}" style="color:#4A90E2;">LinkedIn</a>' if signature.get("linkedin") else ""
    phone_line    = f'<span>{signature["phone"]}</span>'                                      if signature.get("phone")    else ""
    company_line  = (
        f'<span style="color:#555;">{signature["title"]} | {signature["company"]}</span>'
        if signature.get("company") else
        f'<span style="color:#555;">{signature["title"]}</span>'
    )

    html = f"""
    <html>
    <body style="font-family:Arial,sans-serif; font-size:15px; color:#222;
                 max-width:650px; margin:auto; padding:24px;">
        <p>Dear {original_sender},</p>
        <div style="line-height:1.7; margin-bottom:28px;">
            {body.replace(chr(10), '<br>')}
        </div>
        <div style="border-top:2px solid #4A90E2; padding-top:14px; margin-top:24px; color:#333;">
            <p style="margin:0; font-size:16px; font-weight:bold; color:#222;">{signature['name']}</p>
            <p style="margin:4px 0; font-size:13px;">{company_line}</p>
            {"<p style='margin:4px 0;font-size:13px;'>" + phone_line    + "</p>" if phone_line    else ""}
            {"<p style='margin:4px 0;font-size:13px;'>" + linkedin_line + "</p>" if linkedin_line else ""}
        </div>
    </body>
    </html>
    """

    msg            = MIMEMultipart('alternative')
    msg['To']      = to
    msg['Subject'] = "Re: " + subject
    msg.attach(MIMEText(html, 'html'))

    raw    = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    result = service.users().messages().send(
        userId='me', body={'raw': raw}
    ).execute()
    return result