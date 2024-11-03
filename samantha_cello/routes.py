from flask import render_template, request, redirect, session, jsonify
import os
import json
import requests
import random
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from samantha_cello import app  # Import app from __init__.py

# Environment variables for email
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
# JSONBin.io config
JSONBIN_API_KEY = os.getenv('JSONBIN_API_KEY')
JSONBIN_BIN_ID = os.getenv('JSONBIN_BIN_ID')
JSONBIN_URL = f'https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}'


# Headers for JSONBin requests
jsonbin_headers = {
    'Content-Type': 'application/json',
    'X-Master-Key': JSONBIN_API_KEY
}

@app.route('/')
def home():
    gallery_dir = 'samantha_cello/static/images/gallery/'
    # Get only the filenames
    image_paths = [img for img in os.listdir(gallery_dir) if img.endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    random.shuffle(image_paths)
    print(image_paths)
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
        sender_email = os.getenv('GMAIL_ADDRESS')
        receiver_email = os.getenv('GMAIL_ADDRESS')
        password = os.getenv('GMAIL_APP_PASSWORD')
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

        # Retrieve existing enquiries from JSONBin
        try:
            response = requests.get(JSONBIN_URL, headers=jsonbin_headers)
            if response.status_code == 200:
                enquiries = response.json()['record']
            else:
                enquiries = []
                print(f"Failed to retrieve enquiries: {response.status_code}")
        except Exception as e:
            print(f"Error retrieving enquiries: {e}")
            return "An error occurred", 500

        # Append the new enquiry
        enquiries.append(enquiry)

        # Save the updated enquiries back to JSONBin
        try:
            response = requests.put(JSONBIN_URL, headers=jsonbin_headers, json=enquiries)
            if response.status_code != 200:
                print(f"Failed to save enquiry: {response.status_code}")
                return "An error occurred", 500
        except Exception as e:
            print(f"Error saving enquiry: {e}")
            return "An error occurred", 500

        message = "Thank you, your message has been received."
        return render_template('contact.html', message=message, enquiry=enquiry)

    return render_template('contact.html')


@app.route('/enquiries', methods=['GET', 'POST'])
def enquiries():
    if request.method == 'POST':
        password = request.form['password']
        if password == os.getenv('ADMIN_PASSWORD'):
            session['authenticated'] = True

    if 'authenticated' in session and session['authenticated']:
        try:
            response = requests.get(JSONBIN_URL, headers=jsonbin_headers)
            if response.status_code == 200:
                enquiries = response.json()['record']
            else:
                print(f"Failed to retrieve enquiries: {response.status_code}")
                enquiries = []
        except Exception as e:
            print(f"Error accessing JSONBin: {e}")
            enquiries = []

        # Format dates for display
        for enquiry in enquiries:
            original_date = datetime.fromisoformat(enquiry['submitted_at'])
            enquiry['submitted_at'] = original_date.strftime('%d/%m/%y %H:%M')

        return render_template('enquiries.html', enquiries=enquiries)

    return render_template('enquiries.html')


@app.route('/update/<int:enquiry_index>', methods=['POST'])
def update_enquiry(enquiry_index):
    try:
        response = requests.get(JSONBIN_URL, headers=jsonbin_headers)
        if response.status_code == 200:
            enquiries = response.json()['record']
        else:
            print(f"Failed to retrieve enquiries: {response.status_code}")
            return "An error occurred", 500
    except Exception as e:
        print(f"Error retrieving enquiries: {e}")
        return "An error occurred", 500

    # Toggle the converted status
    enquiries[enquiry_index]['converted'] = not enquiries[enquiry_index]['converted']

    # Save the updated enquiries back to JSONBin
    try:
        response = requests.put(JSONBIN_URL, headers=jsonbin_headers, json=enquiries)
        if response.status_code != 200:
            print(f"Failed to update enquiry: {response.status_code}")
            return "An error occurred", 500
    except Exception as e:
        print(f"Error updating enquiry: {e}")
        return "An error occurred", 500

    return redirect('/enquiries')


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect('/enquiries')
