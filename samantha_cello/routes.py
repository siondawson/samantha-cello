from flask import render_template, request, redirect, session
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
    title = "Samantha Cello | Solo Cello Music for Weddings and Events | Cardiff"
    meta_description = (
        "Welcome to Samantha Cello's website, your premier choice for wedding music "
        "in Cardiff, South Wales. Specialising in enchanting cello performances, available "
        "for events across the UK, including London and surrounding areas. Book now for a "
        "magical musical experience!"
    )

    gallery_dir = 'samantha_cello/static/images/gallery/'
    image_paths = [
        img for img in os.listdir(gallery_dir)
        if img.endswith(('.png', '.jpg', '.jpeg', '.webp'))
    ]
    random.shuffle(image_paths)

    # Load reviews from JSON
    with open('samantha_cello/static/json/reviews.json', 'r') as f:
        reviews = json.load(f)

    return render_template(
        'index.html', image_paths=image_paths, reviews=reviews, 
        title=title, meta_description=meta_description
    )


@app.route('/about')
def about():
    title = "About | Samantha Cello | Solo Cello Music for Weddings and Events"
    meta_description = (
        "Welcome to Samantha Cello's website, your premier choice for wedding music in "
        "Cardiff, South Wales. Specialising in enchanting cello performances, available "
        "for events across the UK, including London and surrounding areas. Book now for "
        "a magical musical experience!"
    )
    with open('samantha_cello/static/json/about.json') as f:
        about_data = json.load(f)

    return render_template(
        'about.html', about_data=about_data, 
        title=title, meta_description=meta_description
    )


@app.route('/repertoire')
def repertoire():
    title = "Repertoire | Samantha Cello | Solo Cello Music for Weddings and Events"
    meta_description = (
        "Discover the enchanting repertoire of Samantha Cello, your premier wedding musician "
        "based in Cardiff, South Wales. Browse through our diverse selection of pieces, perfect "
        "for any occasion, including weddings and events across the UK. Book now to bring beautiful "
        "music to your special day!"
    )
    with open('samantha_cello/static/json/repertoire.json') as f:
        songs = json.load(f)

    return render_template(
        'repertoire.html', songs=songs, 
        title=title, meta_description=meta_description
    )


@app.route('/faq')
def faq():
    title = "Faqs | Samantha Cello | Solo Cello Music for Weddings and Events"
    meta_description = (
        "Have questions about hiring Samantha Cello for your wedding or event in Cardiff, South Wales? "
        "Explore our FAQ page for answers to common inquiries about performance details, booking processes, "
        "and more. Get all the information you need to ensure a magical musical experience!"
    )
    json_path = os.path.join(app.root_path, 'static/json/faq.json')
    with open(json_path) as f:
        faq_data = json.load(f)

    return render_template(
        'faq.html', faqs=faq_data, 
        title=title, meta_description=meta_description
    )


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    title = "Contact | Samantha Cello | Solo Cello Music for Weddings and Events"
    meta_description = (
        "Get in touch with Samantha Cello for exceptional wedding music services in Cardiff and beyond. "
        "Fill out our contact form for a free, no-obligation quote, and let us bring the perfect sound to your special day!"
    )

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone'] or None
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

        # Email handling
        sender_email = GMAIL_ADDRESS
        receiver_email = GMAIL_ADDRESS
        password = GMAIL_APP_PASSWORD
        subject = "New Contact Form Submission"
        body = f"""
        <html><body><h2>New Contact Form Submission from {name}</h2>
        <p><strong>Name:</strong> {name}</p>
        <p><strong>Email:</strong> {email}</p>
        <p><strong>Phone:</strong> {phone if phone else 'None'}</p>
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

        # Retrieve and update enquiries from JSONBin
        try:
            response = requests.get(JSONBIN_URL, headers=jsonbin_headers)
            enquiries = response.json().get('record', []) if response.status_code == 200 else []
        except Exception as e:
            print(f"Error retrieving enquiries: {e}")
            return "An error occurred", 500

        enquiries.append(enquiry)

        try:
            response = requests.put(JSONBIN_URL, headers=jsonbin_headers, json=enquiries)
            if response.status_code != 200:
                print(f"Failed to save enquiry: {response.status_code}")
                return "An error occurred", 500
        except Exception as e:
            print(f"Error saving enquiry: {e}")
            return "An error occurred", 500

        message = "Thank you, your message has been received."
        return render_template(
            'contact.html', message=message, 
            enquiry=enquiry, title=title, meta_description=meta_description
        )

    return render_template('contact.html', title=title, meta_description=meta_description)


@app.route('/enquiries', methods=['GET', 'POST'])
def enquiries():
    if request.method == 'POST':
        if request.form['password'] == ADMIN_PASSWORD:
            session['authenticated'] = True

    if session.get('authenticated'):
        try:
            response = requests.get(JSONBIN_URL, headers=jsonbin_headers)
            enquiries = response.json().get('record', []) if response.status_code == 200 else []
        except Exception as e:
            print(f"Error accessing JSONBin: {e}")
            enquiries = []

        for enquiry in enquiries:
            original_date = datetime.fromisoformat(enquiry['submitted_at'])
            enquiry['submitted_at'] = original_date.strftime('%d/%m/%y %H:%M')

        return render_template('enquiries.html', enquiries=enquiries)

    return render_template('enquiries.html')


@app.route('/update/<int:enquiry_index>', methods=['POST'])
def update_enquiry(enquiry_index):
    try:
        response = requests.get(JSONBIN_URL, headers=jsonbin_headers)
        enquiries = response.json().get('record', []) if response.status_code == 200 else []
    except Exception as e:
        print(f"Error retrieving enquiries: {e}")
        return "An error occurred", 500

    enquiries[enquiry_index]['converted'] = not enquiries[enquiry_index]['converted']

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


@app.route("/env")
def show_environment():
    environment = os.getenv("ENVIRONMENT", "production")
    return f"Current environment: {environment}"

