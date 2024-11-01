from flask import render_template, request, redirect, session
import os
import json
import random
import dropbox
from dropbox.exceptions import AuthError, ApiError
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from samantha_cello import app  # Import app from __init__.py

# Environment variables for email
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
DROPBOX_ACCESS_TOKEN = os.getenv("DROPBOX_ACCESS_TOKEN")
dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)

@app.route('/')
def home():
    gallery_dir = 'samantha_cello/static/images/gallery/'
    image_paths = [os.path.join(gallery_dir, img) for img in os.listdir(gallery_dir) if img.endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    random.shuffle(image_paths)
    return render_template('index.html', image_paths=image_paths)

@app.route('/about')
def about():
    with open('samantha_cello/static/json/about.json') as f:
        about_data = json.load(f)
    return render_template('about.html', about_data=about_data)

@app.route('/repertoire')
def repertoire():
    with open('samantha_cello/static/json/repertoire.json') as f:
        songs = json.load(f)
    return render_template('repertoire.html', songs=songs)

@app.route('/faq')
def faq():
    json_path = os.path.join(app.root_path, 'static/json/faq.json')
    with open(json_path) as f:
        faq_data = json.load(f)
    return render_template('faq.html', faqs=faq_data)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        message = request.form['message']
        submitted_at = datetime.now().isoformat()

        enquiry = {
            'name': name,
            'email': email,
            'phone': phone,
            'message': message,
            'submitted_at': submitted_at,
            'converted': False
        }

        # Email handling (remains unchanged)
        sender_email = GMAIL_ADDRESS
        receiver_email = GMAIL_ADDRESS
        password = GMAIL_APP_PASSWORD
        subject = "New Contact Form Submission"
        body = f"""
        <html><body><h2>New Contact Form Submission from {name}</h2>
        <p><strong>Name:</strong> {name}</p>
        <p><strong>Email:</strong> {email}</p>
        <p><strong>Phone:</strong> {phone}</p>
        <p><strong>Message:</strong></p>
        <p>{message}</p></body></html>
        """

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg['Reply-To'] = email
        msg.attach(MIMEText(body, 'html'))

        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender_email, password)
                server.send_message(msg)
        except Exception as e:
            print(f"Error sending email: {e}")

        # Save enquiry to Dropbox
        try:
            # Retrieve existing enquiries from Dropbox
            _, res = dbx.files_download('/Apps/samantha_cello/enquiries.json')
            enquiries = json.loads(res.content)
        except dropbox.exceptions.HttpError as e:
            if isinstance(e, dropbox.exceptions.ApiError):
                # If the file does not exist, start with an empty list
                if e.is_path() and e.get_path().is_not_found():
                    enquiries = []
                else:
                    print(f"Error downloading file: {e}")
                    enquiries = []  # Start with an empty list on other API errors
            else:
                enquiries = []  # Start with an empty list on unexpected errors

        # Append the new enquiry
        enquiries.append(enquiry)

        # Save the updated enquiries back to Dropbox
        dbx.files_upload(json.dumps(enquiries).encode(), '/Apps/samantha_cello/enquiries.json', mode=dropbox.files.WriteMode('overwrite'))

        message = "Thank you, your message has been received."
        return render_template('contact.html', message=message, enquiry=enquiry)

    return render_template('contact.html')


@app.route('/enquiries', methods=['GET', 'POST'])
def enquiries():
    if request.method == 'POST':
        password = request.form['password']
        if password == ADMIN_PASSWORD:
            session['authenticated'] = True

    if 'authenticated' in session and session['authenticated']:
        enquiries = []

        try:
            # Attempt to download the enquiries.json file
            _, res = dbx.files_download('/Apps/samantha_cello/enquiries.json')
            enquiries = json.loads(res.content)
        except dropbox.exceptions.ApiError as e:
            if e.is_path() and e.get_path().is_not_found():
                # If the file doesn't exist, create it with an empty JSON array
                empty_json = []
                dbx.files_upload(json.dumps(empty_json).encode(), '/Apps/samantha_cello/enquiries.json')
                enquiries = []  # Initialize with an empty list
            else:
                # Handle other API errors accordingly
                return f"Error retrieving enquiries: {str(e)}", 500

        # Format the submitted_at date for display
        for enquiry in enquiries:
            original_date = datetime.fromisoformat(enquiry['submitted_at'])
            enquiry['submitted_at'] = original_date.strftime('%d/%m/%y %H:%M')

        return render_template('enquiries.html', enquiries=enquiries)

    return render_template('enquiries.html')



@app.route('/update/<int:index>', methods=['POST'])
def update_enquiry(index):
    try:
        # Download the enquiries JSON file from Dropbox
        _, response = dbx.files_download('/enquiries.json')
        enquiries = json.loads(response.content)
    except (dropbox.exceptions.HttpError, json.JSONDecodeError):
        return "Error loading enquiries.", 404

    if 0 <= index < len(enquiries):
        enquiries[index]['converted'] = not enquiries[index]['converted']

        # Upload the updated enquiries JSON file back to Dropbox
        dbx.files_upload(json.dumps(enquiries).encode('utf-8'), '/enquiries.json', mode=dropbox.files.WriteMode.overwrite)

    return redirect('/enquiries')

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect('/enquiries')
