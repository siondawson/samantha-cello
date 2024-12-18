import os
from samantha_cello import app

if __name__ == "__main__":
    environment = os.getenv("ENVIRONMENT", "production")
    debug_mode = environment == "development"

    # Clear the SERVER_NAME when running directly
    if debug_mode:
        app.config['SERVER_NAME'] = None

    app.run(
        host=os.getenv("IP", "0.0.0.0"),
        port=int(os.getenv("PORT", 5000)),
        debug=debug_mode
    )
