from flask import Flask, request, render_template, json, jsonify
import os
from datetime import datetime

app = Flask(__name__)

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
            'submitted_at': submitted_at  # Add the date and time here
        }

        # Define the path for the JSON file
        json_file_path = 'static/json/enquiries.json'

        # Check if the JSON file exists; if not, create it
        if not os.path.exists(json_file_path):
            with open(json_file_path, 'w') as file:
                json.dump([], file)  # Create an empty list in the file

        # Load existing enquiries
        try:
            with open(json_file_path, 'r') as file:
                enquiries = json.load(file)
        except json.JSONDecodeError:
            enquiries = []  # Initialize to an empty list if there's a decode error

        # Append the new enquiry
        enquiries.append(enquiry)

        # Save the updated list back to the JSON file
        with open(json_file_path, 'w') as file:
            json.dump(enquiries, file, indent=4)

        message = "Thank you, your message has been received."
        
        # Pass the message and enquiry details back to the template
        return render_template('contact.html', message=message, enquiry=enquiry)

    return render_template('contact.html')


if __name__ == '__main__':
    app.run(debug=True)
