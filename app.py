from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/repertoire')
def repertoire():
    return render_template('repertoire.html')  # Create this template

@app.route('/faq')
def faq():
    return render_template('faq.html')  # Create this template

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')  # Create this template

@app.route('/contact')
def contact():
    return render_template('contact.html')  # Create this template

if __name__ == '__main__':
    app.run(debug=True)
