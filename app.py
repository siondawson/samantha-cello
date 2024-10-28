from flask import Flask, render_template, json
import os

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

@app.route('/contact')
def contact():
    return render_template('contact.html')  # Create this template

if __name__ == '__main__':
    app.run(debug=True)
