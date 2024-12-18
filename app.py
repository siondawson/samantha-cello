import os
from samantha_cello import app

if __name__ == "__main__":
    environment = os.getenv("ENVIRONMENT", "production")
    debug_mode = environment == "development"

    app.run(
        host=os.getenv("IP", "0.0.0.0"),
        port=int(os.getenv("PORT", 5000)),
        debug=debug_mode
    )