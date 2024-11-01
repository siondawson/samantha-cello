import os
from flask import Flask
if os.path.exists("env.py"):
    import env  # noqa

app = Flask(__name__)

# Set the secret key from environment variables
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default_secret_key")

# Register routes from routes.py
from samantha_cello import routes  # noqa
