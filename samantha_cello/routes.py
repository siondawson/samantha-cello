from flask import render_template, request, redirect, session
import os
import json
import random
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from samantha_cello import app  # Import app from __init__.py

# Environment variables for email
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

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

        os.makedirs('samantha_cello/static/json', exist_ok=True)

        try:
            with open('samantha_cello/static/json/enquiries.json', 'r') as file:
                enquiries = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            enquiries = []

        enquiries.append(enquiry)

        with open('samantha_cello/static/json/enquiries.json', 'w') as file:
            json.dump(enquiries, file, indent=4)

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
        try:
            with open('samantha_cello/static/json/enquiries.json', 'r') as file:
                enquiries = json.load(file)
        except (FileNotFoundError, JSONDecodeError):
            enquiries = []

        for enquiry in enquiries:
            original_date = datetime.fromisoformat(enquiry['submitted_at'])
            enquiry['submitted_at'] = original_date.strftime('%d/%m/%y %H:%M')

        return render_template('enquiries.html', enquiries=enquiries)

    return render_template('enquiries.html')

@app.route('/update/<int:index>', methods=['POST'])
def update_enquiry(index):
    try:
        with open('samantha_cello/static/json/enquiries.json', 'r') as file:
            enquiries = json.load(file)
    except (FileNotFoundError, JSONDecodeError):
        return "Error loading enquiries.", 404

    if 0 <= index < len(enquiries):
        enquiries[index]['converted'] = not enquiries[index]['converted']

        with open('samantha_cello/static/json/enquiries.json', 'w') as file:
            json.dump(enquiries, file, indent=4)

    return redirect('/enquiries')

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect('/enquiries')
