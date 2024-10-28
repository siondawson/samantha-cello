from flask import Flask, request, render_template, redirect, session
import json
from json import JSONDecodeError
from datetime import datetime
from env import ADMIN_PASSWORD, SECRET_KEY  # Import from env.py

app = Flask(__name__)
app.secret_key = SECRET_KEY  # Set the secret key for session management


@app.route('/')
def home():
    return render_template('index.html')


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


@app.route('/gallery')
def gallery():
    return render_template('gallery.html')  # Create this template


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
