from flask import render_template, request, redirect, session, Response, url_for
import os
import json
import requests
import random
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from samantha_cello import app, sitemap  # Import app from __init__.py

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


def get_canonical_url():
    return url_for(request.endpoint, **request.view_args, _external=True)


@app.route('/')
def home():
    # Load meta tag data from JSON
    with open('samantha_cello/static/json/meta_tags.json', 'r') as f:
        meta_tags = json.load(f)
    
    # Extract data for the "home" page
    meta_data = meta_tags.get("home", {})
    title = meta_data.get("title", "Default Title")
    meta_description = meta_data.get("meta_description", "Default Meta Description")
    
    # Load gallery data from JSON
    with open('samantha_cello/static/json/gallery.json', 'r') as f:
        gallery_data = json.load(f)
    
    # Shuffle gallery data for randomness
    random.shuffle(gallery_data)

    # Load reviews from JSON
    with open('samantha_cello/static/json/reviews.json', 'r') as f:
        reviews = json.load(f)

    # Get canonical URL
    canonical_url = get_canonical_url()

    return render_template(
        'index.html', 
        gallery_data=gallery_data,  # Pass gallery data (src and alt)
        reviews=reviews, 
        title=title, 
        meta_description=meta_description, 
        canonical_url=canonical_url
    )



@app.route('/about')
def about():
    """A route to return the home page. Gallery data fetched from a json file."""
     # Load meta tag data from JSON
    with open('samantha_cello/static/json/meta_tags.json', 'r') as f:
        meta_tags = json.load(f)
    
    # Extract data for the "about" page
    meta_data = meta_tags.get("about", {})
    title = meta_data.get("title", "Default Title")
    meta_description = meta_data.get("meta_description", "Default Meta Description")
    with open('samantha_cello/static/json/about.json') as f:
        about_data = json.load(f)

    # Get canonical URL
    canonical_url = get_canonical_url()

    return render_template(
        'about.html', about_data=about_data, 
        title=title, meta_description=meta_description, canonical_url=canonical_url
    )


@app.route('/repertoire')
def repertoire():
     # Load meta tag data from JSON
    with open('samantha_cello/static/json/meta_tags.json', 'r') as f:
        meta_tags = json.load(f)
    
    # Extract data for the "repertoire" page
    meta_data = meta_tags.get("repertoire", {})
    title = meta_data.get("title", "Default Title")
    meta_description = meta_data.get("meta_description", "Default Meta Description")
    with open('samantha_cello/static/json/repertoire.json') as f:
        songs = json.load(f)

    
    # Get canonical URL
    canonical_url = get_canonical_url()

    return render_template(
        'repertoire.html', songs=songs, 
        title=title, meta_description=meta_description, canonical_url=canonical_url
    )


@app.route('/faq')
def faq():
     # Load meta tag data from JSON
    with open('samantha_cello/static/json/meta_tags.json', 'r') as f:
        meta_tags = json.load(f)
    
    # Extract data for the "faqs" page
    meta_data = meta_tags.get("faqs", {})
    title = meta_data.get("title", "Default Title")
    meta_description = meta_data.get("meta_description", "Default Meta Description")
    json_path = os.path.join(app.root_path, 'static/json/faq.json')
    with open(json_path) as f:
        faq_data = json.load(f)

    # Get canonical URL
    canonical_url = get_canonical_url()

    return render_template(
        'faq.html', faqs=faq_data, 
        title=title, meta_description=meta_description, canonical_url=canonical_url
    )


@app.route('/contact', methods=['GET', 'POST'])
def contact():
     # Load meta tag data from JSON
    with open('samantha_cello/static/json/meta_tags.json', 'r') as f:
        meta_tags = json.load(f)
    
    # Extract data for the "contact" page
    meta_data = meta_tags.get("contact", {})
    title = meta_data.get("title", "Default Title")
    meta_description = meta_data.get("meta_description", "Default Meta Description")

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
        # Get canonical URL
        canonical_url = get_canonical_url()
        return render_template(
            'contact.html', message=message, 
            enquiry=enquiry, title=title, meta_description=meta_description, canonical_url=canonical_url
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


@app.route('/videos')
def all_videos():
    """Display all videos."""
    json_path = os.path.join(app.root_path, 'static/json/videos.json')
    try:
        with open(json_path, 'r') as file:
            videos = json.load(file)
    except FileNotFoundError:
        videos = []

    title = "Videos | Samantha Cello | Performances and Concerts"
    meta_description = (
        "Explore a curated selection of performances by Samantha Cello. "
        "Watch videos of enchanting cello music from weddings, events, and concerts."
    )

    # Get canonical URL
    canonical_url = get_canonical_url()

    return render_template(
        'videos.html', videos=videos, 
        title=title, meta_description=meta_description, canonical_url=canonical_url
    )



@app.route('/videos/<slug>')
def video_page(slug):
    """Display a single video based on its slug."""
    json_path = os.path.join(app.root_path, 'static/json/videos.json')
    try:
        with open(json_path, 'r') as file:
            videos = json.load(file)
    except FileNotFoundError:
        return "Videos data not found", 404

    # Find the requested video by slug
    video = next((v for v in videos if v['pageSlug'] == slug), None)
    if not video:
        return "Video not found", 404

    # Get related videos (excluding the current one)
    related_videos = [v for v in videos if v['id'] != video['id']]

    # Title and meta description
    title = video['pageTitle']
    meta_description = video['metaDescription']

    # Get canonical URL
    canonical_url = get_canonical_url()

    return render_template(
        'video_page.html',
        video=video,
        related_videos=related_videos,
        title=title,
        meta_description=meta_description,
        canonical_url=canonical_url
    )


@app.route('/robots.txt')
def robots():
    return app.send_static_file('robots.txt')


# Register routes for the sitemap
@sitemap.register_generator
def sitemap_urls():
    # Static routes
    yield 'home', {}
    yield 'about', {}
    yield 'repertoire', {}
    yield 'faq', {}
    yield 'contact', {}
    yield 'all_videos', {}

    # Load the videos from the JSON file
    with open(os.path.join(app.root_path, 'static', 'json', 'videos.json')) as f:
        videos = json.load(f)

    # Loop through each video and generate its URL
    for video in videos:
        yield 'video_page', {'slug': video['pageSlug']}


@app.route('/sitemap.xml')
def sitemap():
    # This will generate the sitemap dynamically using the generator
    return Response(generate_sitemap(), mimetype='application/xml')

def generate_sitemap():
    # Create the XML structure for the sitemap
    sitemap_xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    sitemap_xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    # Call the generator function to get the dynamic URLs
    for endpoint, params in sitemap_urls():
        url = url_for(endpoint, **params, _external=True, _scheme='https')
        sitemap_xml.append(f'<url><loc>{url}</loc></url>')
    
    sitemap_xml.append('</urlset>')
    return ''.join(sitemap_xml)

def sitemap_urls():
    # This is a placeholder function. Replace it with your logic to generate URLs.
    # Example:
    return [
        ('static_page', {'page': 'index'}),
        ('static_page', {'page': 'about'}),
        # Add more pages as needed
    ]

@app.route('/<page>')
def static_page(page):
    # Example static page route
    return f"This is the {page} page."


# Error handler for 404
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


