from flask import Flask, request, render_template, redirect, session
import json
import os
import random
from json import JSONDecodeError
from datetime import datetime

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables based on the environment
if os.getenv('FLASK_ENV') == 'development':
    from env import ADMIN_PASSWORD, SECRET_KEY, GMAIL_ADDRESS, GMAIL_APP_PASSWORD
else:
    # In production, retrieve these from the environment
    SECRET_KEY = os.getenv('SECRET_KEY')
    GMAIL_ADDRESS = os.getenv('GMAIL_ADDRESS')
    GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')

# Ensure required variables are set
if not all([SECRET_KEY, GMAIL_ADDRESS, GMAIL_APP_PASSWORD]):
    raise ValueError("Missing environment variables. Please set SECRET_KEY, GMAIL_ADDRESS, and GMAIL_APP_PASSWORD.")


app = Flask(__name__)
app.secret_key = SECRET_KEY  # Set the secret key for session management


@app.route('/')
def home():
    # Directory containing gallery images
    gallery_dir = 'static/images/gallery/'
    
    # Get list of image paths
    image_paths = [os.path.join(gallery_dir, img) for img in os.listdir(gallery_dir) if img.endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    
    # Shuffle the list of image paths
    random.shuffle(image_paths)
    
    return render_template('index.html', image_paths=image_paths)


@app.route('/about')
def about():
    with open('static/json/about.json') as f:
        about_data = json.load(f)  # This will be a list of dictionaries
    return render_template('about.html', about_data=about_data)


@app.route('/repertoire')
def repertoire():
    return render_template('repertoire.html')  # Create this template


@app.route('/faq')
def faq():
    # Specify the correct path for the JSON file in the static folder
    json_path = os.path.join(app.root_path, 'static/json/faq.json')
    with open(json_path) as f:
        faq_data = json.load(f)
    return render_template('faq.html', faqs=faq_data)


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        message = request.form['message']
        
        # Get current date and time
        submitted_at = datetime.now().isoformat()  # ISO format (e.g., '2024-10-28T15:30:00')

        # Create an enquiry dictionary
        enquiry = {
            'name': name,
            'email': email,
            'phone': phone,
            'message': message,
            'submitted_at': submitted_at,  # Add the date and time here
            'converted': False  # Default value for the converted field
        }

       # Email setup
        sender_email = GMAIL_ADDRESS  # Your Gmail address from env.py
        receiver_email = GMAIL_ADDRESS  # Change this to another address if needed
        password = GMAIL_APP_PASSWORD 

        subject = "New Contact Form Submission"
        # Create an HTML body
        body = f"""
        <html>
            <body>
                <h2>New Contact Form Submission from {name}</h2>
                <p><strong>Name:</strong> {name}</p>
                <p><strong>Email:</strong> {email}</p>
                <p><strong>Phone:</strong> {phone}</p>
                <p><strong>Message:</strong></p>
                <p>{message}</p>
            </body>
        </html>
        """

        # Create the email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg['Reply-To'] = email  # Set the Reply-To header to the email from the form
        msg.attach(MIMEText(body, 'html'))  # Change 'plain' to 'html'

        # Send the email
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection
                server.login(sender_email, password)
                server.send_message(msg)
            print("Email sent successfully!")
        except Exception as e:
            print(f"Error sending email: {e}")


        # Ensure the directory exists
        os.makedirs('static/json', exist_ok=True)

        # Load existing enquiries
        try:
            with open('static/json/enquiries.json', 'r') as file:
                enquiries = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            enquiries = []

        # Append the new enquiry
        enquiries.append(enquiry)

        # Save the updated list back to the JSON file
        with open('static/json/enquiries.json', 'w') as file:
            json.dump(enquiries, file, indent=4)

        message = "Thank you, your message has been received."
        
        # Pass the message and enquiry details back to the template
        return render_template('contact.html', message=message, enquiry=enquiry)

    return render_template('contact.html')



@app.route('/enquiries', methods=['GET', 'POST'])
def enquiries():
    if request.method == 'POST':
        password = request.form['password']
        if password == ADMIN_PASSWORD:
            session['authenticated'] = True  # Set the session variable

    # Check if the user is authenticated
    if 'authenticated' in session and session['authenticated']:
        # Load the enquiries
        try:
            with open('static/json/enquiries.json', 'r') as file:
                enquiries = json.load(file)
        except (FileNotFoundError, JSONDecodeError):
            enquiries = []

        # Format the date and time
        for enquiry in enquiries:
            original_date = datetime.fromisoformat(enquiry['submitted_at'])
            enquiry['submitted_at'] = original_date.strftime('%d/%m/%y %H:%M')

        # Render the template with enquiries
        return render_template('enquiries.html', enquiries=enquiries)

    # If the user is not authenticated, show the password form
    return render_template('enquiries.html')


@app.route('/update/<int:index>', methods=['POST'])
def update_enquiry(index):
    # Load existing enquiries
    try:
        with open('static/json/enquiries.json', 'r') as file:
            enquiries = json.load(file)
    except (FileNotFoundError, JSONDecodeError):
        return "Error loading enquiries.", 404

    # Check if the index is valid
    if 0 <= index < len(enquiries):
        # Toggle the converted status
        enquiries[index]['converted'] = not enquiries[index]['converted']

        # Save the updated list back to the JSON file
        with open('static/json/enquiries.json', 'w') as file:
            json.dump(enquiries, file, indent=4)

    # Return to the same page to reflect the changes
    return redirect('/enquiries')  # Redirect to the enquiries page


@app.route('/logout', methods=['POST'])
def logout():
    # Clear the session
    session.clear()
    return redirect('/enquiries')  # Redirect to the enquiries page




if __name__ == '__main__':
    app.run(debug=True)
