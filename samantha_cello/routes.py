from flask import Flask, render_template, url_for, request, make_response
import os
import json
from datetime import datetime
from samantha_cello import app, sitemap




# Environment variables for email
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# JSONBin.io config
JSONBIN_API_KEY = os.getenv('JSONBIN_API_KEY')
JSONBIN_BIN_ID = os.getenv('JSONBIN_BIN_ID')
JSONBIN_URL = f'https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}'

# Headers for JSONBin requests
jsonbin_headers = {
    'Content-Type': 'application/json',
    'X-Master-Key': JSONBIN_API_KEY
}

# google recaptcha
SITE_KEY = '6LeCmZ8qAAAAAMO_tZXZNbBT_kTIuJ30ZF8MxsRF'
RECAPTCHA_SECRET_KEY = os.getenv('RECAPTCHA_SECRET_KEY')


def get_canonical_url():
    return url_for(request.endpoint, **request.view_args, _external=True)


@app.route('/')
def home():
    """
    Render the home page of the Samantha Cello website.
    This function loads various data from JSON files to populate the home page with dynamic content,
    including meta tags, gallery images, and testimonials. It then renders the 'index.html' template with
    this data, providing a consistent user experience.

    """
    # Load meta tag data from JSON
    with open('samantha_cello/static/json/meta_tags.json', 'r') as f:
        meta_tags = json.load(f)
    # Extract data for the "home" page
    meta_data = meta_tags.get("home", {})
    title = meta_data.get("title", "Default Title")
    meta_description = meta_data.get("meta_description", "Default Meta Description")
    
    # Load gallery data from JSON
    with open('samantha_cello/static/json/gallery.json', 'r') as f:
        gallery_data = json.load(f)
    
    # Load testimonials from JSON
    with open('samantha_cello/static/json/testimonials.json', 'r') as f:
        testimonials = json.load(f)
    
    # Generate the canonical URL
    canonical_url = get_canonical_url()
    
    return render_template(
        'index.html',
        gallery_data=gallery_data,  # Pass gallery data (src and alt)
        testimonials=testimonials,  # Pass testimonials data
        title=title,
        meta_description=meta_description,
        canonical_url=canonical_url
    )




@app.route('/about/')
def about():
    """A route to return the about page. Gallery data fetched from a json file."""
    # Load meta tag data from JSON
    with open('samantha_cello/static/json/meta_tags.json', 'r') as f:
        meta_tags = json.load(f)

    # Extract data for the "about" page
    meta_data = meta_tags.get("about", {})
    title = meta_data.get("title", "Default Title")
    meta_description = meta_data.get("meta_description", "Default Meta Description")

    # Load about data from JSON
    with open('samantha_cello/static/json/about.json') as f:
        about_data = json.load(f)

    # Generate the canonical URL
    canonical_url = get_canonical_url()

    return render_template(
        'about.html', about_data=about_data, 
        title=title, meta_description=meta_description, canonical_url=canonical_url
    )



@app.route('/repertoire/')
def repertoire():
    """Render the repertoire page with pre-calculated statistics and data from JSON files."""
    # Load meta tag data from JSON
    with open('samantha_cello/static/json/meta_tags.json', 'r') as f:
        meta_tags = json.load(f)

    # Load repertoire data
    with open('samantha_cello/static/json/repertoire.json') as f:
        songs = json.load(f)

    # Load videos for showreels
    with open('samantha_cello/static/json/videos.json') as f:
        videos = json.load(f)
        showreels = [v for v in videos if 'showreel' in v['pageSlug']]

    # Calculate stats
    stats = {
        'total_songs': len(songs),
        'genres': len(set(song['genre'] for song in songs)),
        'videos': len([song for song in songs if song['hasVideo']]),
        'popular_genres': ['Classical', 'Pop', 'Film']  # Customize as needed
    }

    genre_order = ['Pop', 'Classical', 'Rock', 'Film', 'Bollywood', 'Jazz', 'Musical', 'Country']

    meta_data = meta_tags.get("repertoire", {})
    title = meta_data.get("title", "Default Title")
    meta_description = meta_data.get("meta_description", "Default Meta Description")
    # Generate the canonical URL
    canonical_url = get_canonical_url()

    return render_template(
        'repertoire.html',
        songs=songs,
        showreels=showreels,
        genre_order=genre_order,
        stats=stats,
        title=title,
        meta_description=meta_description,
        canonical_url=canonical_url
    )



@app.route('/faq/')
def faq():
    """Render the FAQ page with data from JSON files."""
    # Load meta tag data from JSON
    with open('samantha_cello/static/json/meta_tags.json', 'r') as f:
        meta_tags = json.load(f)
    
    # Extract data for the "faqs" page
    meta_data = meta_tags.get("faqs", {})
    title = meta_data.get("title", "Default Title")
    meta_description = meta_data.get("meta_description", "Default Meta Description")
    
    # Load FAQ data from JSON
    json_path = os.path.join(app.root_path, 'static/json/faq.json')
    with open(json_path) as f:
        faq_data = json.load(f)

    # Generate the canonical URL
    canonical_url = get_canonical_url()

    return render_template(
        'faq.html',
        faqs=faq_data,
        title=title,
        meta_description=meta_description,
        canonical_url=canonical_url
    )


@app.route('/testimonials/')
def testimonials():
    """Render the testimonials page."""
    with open('samantha_cello/static/json/testimonials.json', 'r') as f:
        testimonials = json.load(f)
    return render_template('testimonials.html', testimonials=testimonials)


@app.route('/contact/')
def contact():
    """Render the contact page."""
    # Load meta tag data from JSON
    with open('samantha_cello/static/json/meta_tags.json', 'r') as f:
        meta_tags = json.load(f)
    
    meta_data = meta_tags.get("contact", {})
    title = meta_data.get("title", "Default Title")
    meta_description = meta_data.get("meta_description", "Default Meta Description")

    # Generate the canonical URL
    canonical_url = get_canonical_url()

    return render_template(
        'contact.html',
        title=title,
        meta_description=meta_description,
        canonical_url=canonical_url,
        site_key=SITE_KEY  # Only needed if you're keeping reCAPTCHA for JavaScript validation
    )


@app.route('/videos/')
def all_videos():
    """Display all videos."""
    json_path = os.path.join(app.root_path, 'static/json/videos.json')
    try:
        with open(json_path, 'r') as file:
            videos = json.load(file)
    except FileNotFoundError:
        videos = []

    title = "Videos | Samantha Cello | Performances and Concerts"
    meta_description = (
        "Explore a curated selection of performances by Samantha Cello. "
        "Watch videos of enchanting cello music from weddings, events, and concerts."
    )

    # Generate the canonical URL
    canonical_url = get_canonical_url()

    return render_template(
        'videos.html',
        videos=videos,
        title=title,
        meta_description=meta_description,
        canonical_url=canonical_url
    )




@app.route('/videos/<slug>/')
def video_page(slug):
    """Display a single video based on its slug."""
    json_path = os.path.join(app.root_path, 'static/json/videos.json')
    try:
        with open(json_path, 'r') as file:
            videos = json.load(file)
    except FileNotFoundError:
        return "Videos data not found", 404

    # Find the requested video by slug
    video = next((v for v in videos if v['pageSlug'] == slug), None)
    if not video:
        return "Video not found", 404

    # Get related videos (excluding the current one)
    related_videos = [v for v in videos if v['id'] != video['id']]

    # Title and meta description
    title = video['pageTitle']
    meta_description = video['metaDescription']

    # Generate the canonical URL
    canonical_url = get_canonical_url()

    return render_template(
        'video_page.html',
        video=video,
        related_videos=related_videos,
        title=title,
        meta_description=meta_description,
        canonical_url=canonical_url
    )



@app.route('/robots.txt')
def robots():
    """Serve robots.txt with proper headers"""
    # Get the current domain
    domain = request.host_url.rstrip('/')
    
    # Define robots.txt content
    robots_content = f"""User-agent: *
Disallow: /enquiries/
Disallow: /update/
Disallow: /logout/

# Sitemaps
Sitemap: {domain}/sitemap.xml
Sitemap: {domain}/video-sitemap.xml"""
    
    # Create response with proper headers
    response = make_response(robots_content)
    response.headers["Content-Type"] = "text/plain"
    response.headers["X-Content-Type-Options"] = "nosniff"  # Security header to prevent MIME-type sniffing
    response.headers["Cache-Control"] = "public, max-age=43200"  # Cache for 12 hours
    
    return response


# Error handler for 404
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@sitemap.register_generator
def sitemap_urls():
    """Generate sitemap URLs with priorities and change frequencies"""
    # Get current date for lastmod
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    # Static routes with their properties
    routes = {
        'home': {'priority': 1.0, 'changefreq': 'weekly'},
        'about': {'priority': 0.8, 'changefreq': 'monthly'},
        'repertoire': {'priority': 0.8, 'changefreq': 'monthly'},
        'faq': {'priority': 0.7, 'changefreq': 'monthly'},
        'contact': {'priority': 0.7, 'changefreq': 'monthly'},
        'all_videos': {'priority': 0.8, 'changefreq': 'weekly'}
    }
    
    # Generate static routes
    for endpoint, properties in routes.items():
        yield (endpoint, 
               {},  # Empty dict for no parameters
               current_date,  # lastmod
               properties['changefreq'],  # changefreq
               properties['priority'])  # priority
    
    # Load and yield video pages
    try:
        videos_path = os.path.join(app.root_path, 'static', 'json', 'videos.json')
        if os.path.exists(videos_path):
            with open(videos_path) as f:
                videos = json.load(f)
            for video in videos:
                yield ('video_page', 
                       {'slug': video['pageSlug']},  # URL parameters
                       current_date,  # lastmod
                       'monthly',  # changefreq
                       0.7)  # priority
    except Exception as e:
        app.logger.error(f"Error generating video URLs for sitemap: {str(e)}")


@app.route('/video-sitemap.xml')
def video_sitemap():
    """Generate video sitemap XML."""
    json_path = os.path.join(app.root_path, 'static/json/videos.json')
    try:
        with open(json_path, 'r') as file:
            videos = json.load(file)
    except FileNotFoundError:
        return "Videos data not found", 404

    xml = '''<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
            xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">'''
    
    for video in videos:
        # Clean description - remove any XML-invalid characters
        clean_description = video['description'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        clean_title = video['title'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        xml += f'''
        <url>
            <loc>{url_for('video_page', slug=video['pageSlug'], _external=True)}</loc>
            <video:video>
                <video:thumbnail_loc>{url_for('static', filename=video['thumbnailFilename'][7:], _external=True)}</video:thumbnail_loc>
                <video:title>{clean_title}</video:title>
                <video:description>{clean_description}</video:description>
                <video:content_loc>{video['contentUrl']}</video:content_loc>
                <video:player_loc>{video['embedUrl']}</video:player_loc>
                <video:publication_date>{video['uploadDate']}</video:publication_date>
                <video:family_friendly>yes</video:family_friendly>
                <video:tag>{', '.join(video['tags'])}</video:tag>
            </video:video>
        </url>'''
    
    xml += '</urlset>'
    
    response = make_response(xml)
    response.headers['Content-Type'] = 'application/xml'
    return response

