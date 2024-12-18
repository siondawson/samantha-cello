import os
from flask import Flask
from flask_sitemap import Sitemap

# Initialize the Flask app
app = Flask(__name__)

# Check if `env.py` exists for environment variables
if os.path.exists("env.py"):
    import env  # noqa

# Set the secret key from environment variables
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default_secret_key")

# Get the environment
environment = os.getenv("ENVIRONMENT", "production")

# Set the scheme based on environment
scheme = 'https' if environment == 'production' else 'http'
domain = os.getenv('DOMAIN', 'samanthacello.com' if environment == 'production' else 'localhost:5000')

# Configure the app
app.config.update(
    SERVER_NAME=domain,
    PREFERRED_URL_SCHEME=scheme,
    # Add these Sitemap specific configurations
    SITEMAP_INCLUDE_RULES_WITHOUT_PARAMS=True,
    SITEMAP_URL_SCHEME=scheme
)

# Initialize Flask-Sitemap
sitemap = Sitemap(app=app)

# Register routes from routes.py
from samantha_cello import routes  # noqa
