from flask_frozen import Freezer
from samantha_cello import app
import json
import os

# Set the destination for the frozen static files directly to the /docs directory
app.config['FREEZER_DESTINATION'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'docs')

# Set the base URL to match your GitHub Pages URL structure
app.config['FREEZER_BASE_URL'] = '/'


freezer = Freezer(app)

@freezer.register_generator
def video_page():
    """Generate URLs for each video page."""
    json_path = os.path.join(app.root_path, 'static/json/videos.json')
    try:
        with open(json_path, 'r') as file:
            videos = json.load(file)
            for video in videos:
                yield {'slug': video['pageSlug']}
    except FileNotFoundError:
        pass

if __name__ == '__main__':
    freezer.freeze()
