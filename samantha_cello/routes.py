from flask import render_template, request, redirect, session, jsonify
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

        # Retrieve existing enquiries from Dropbox or initialize a new list if the file doesn’t exist
        try:
            _, res = dbx.files_download('/enquiries.json')
            enquiries = json.loads(res.content)
        except dropbox.exceptions.ApiError as e:
            # If file not found, start with an empty list
            if e.error.is_path() and e.error.get_path().is_not_found():
                enquiries = []
            else:
                print(f"Error downloading file: {e}")
                return "An error occurred", 500

        # Append the new enquiry
        enquiries.append(enquiry)

        # Save the updated enquiries back to Dropbox
        # To append to the existing file, we must overwrite the entire content
        try:
            dbx.files_upload(json.dumps(enquiries).encode(), '/enquiries.json', mode=dropbox.files.WriteMode('overwrite'))
        except Exception as e:
            print(f"Error uploading file: {e}")
            return "An error occurred", 500

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
        # Define the Dropbox path for the enquiries JSON file
        dropbox_path = '/enquiries.json'
        
        try:
            # Attempt to download the file
            print(f"Attempting to download from path: {dropbox_path}")
            _, res = dbx.files_download(dropbox_path)
            
            # Load the JSON data from the response content
            enquiries = json.loads(res.content)
            print("File found and loaded successfully.")

        except dropbox.exceptions.ApiError as e:
            # Check if the error is due to the file not being found
            if isinstance(e.error, dropbox.files.DownloadError) and e.error.is_path() and e.error.get_path().is_not_found():
                print("File not found. Creating a new enquiries.json file in Dropbox...")
                enquiries = []

                # Attempt to upload an empty JSON file to create it
                try:
                    dbx.files_upload(
                        json.dumps(enquiries).encode('utf-8'),
                        dropbox_path,
                        mode=dropbox.files.WriteMode('overwrite')
                    )
                    print("New enquiries.json file created successfully.")
                except Exception as upload_error:
                    print("Error uploading file to Dropbox:", upload_error)
                    enquiries = []
            else:
                # Log any other errors
                print("Error accessing Dropbox:", e)
                enquiries = []

        # Format dates for display
        for enquiry in enquiries:
            original_date = datetime.fromisoformat(enquiry['submitted_at'])
            enquiry['submitted_at'] = original_date.strftime('%d/%m/%y %H:%M')

        return render_template('enquiries.html', enquiries=enquiries)

    return render_template('enquiries.html')


@app.route('/update/<int:enquiry_index>', methods=['POST'])
def update_enquiry(enquiry_index):
    # Load the existing enquiries from Dropbox
    _, res = dbx.files_download('/enquiries.json')
    enquiries = json.loads(res.content)

    # Toggle the converted status
    enquiries[enquiry_index]['converted'] = not enquiries[enquiry_index]['converted']

    # Save the updated enquiries back to Dropbox
    dbx.files_upload(json.dumps(enquiries).encode(), '/enquiries.json', mode=dropbox.files.WriteMode('overwrite'))

    return redirect('/enquiries')




@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect('/enquiries')
