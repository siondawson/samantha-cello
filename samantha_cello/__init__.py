import os
from flask import Flask
from flask_sitemap import Sitemap

# Check if `env.py` exists for environment variables
if os.path.exists("env.py"):
    import env  # noqa

# Initialize the Flask app
app = Flask(__name__)

# Set the preferred URL scheme to HTTPS
app.config['PREFERRED_URL_SCHEME'] = 'https'

# Set the secret key from environment variables
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default_secret_key")

# Initialize Flask-Sitemap
sitemap = Sitemap(app=app)

# Register routes from routes.py
from samantha_cello import routes  # noqa
