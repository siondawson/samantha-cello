# not used. kept for reference only. old flask code.

@app.route('/enquiries', methods=['GET', 'POST'])
def enquiries():
    if request.method == 'POST':
        if request.form['password'] == ADMIN_PASSWORD:
            session['authenticated'] = True

    if session.get('authenticated'):
        try:
            response = requests.get(JSONBIN_URL, headers=jsonbin_headers)
            enquiries = response.json().get('record', []) if response.status_code == 200 else []
        except Exception as e:
            print(f"Error accessing JSONBin: {e}")
            enquiries = []

        for enquiry in enquiries:
            original_date = datetime.fromisoformat(enquiry['submitted_at'])
            enquiry['submitted_at'] = original_date.strftime('%d/%m/%y %H:%M')

        return render_template('enquiries.html', enquiries=enquiries)
    
    
    return render_template('enquiries.html')


@app.route('/update/<int:enquiry_index>', methods=['POST'])
def update_enquiry(enquiry_index):
    try:
        response = requests.get(JSONBIN_URL, headers=jsonbin_headers)
        enquiries = response.json().get('record', []) if response.status_code == 200 else []
    except Exception as e:
        print(f"Error retrieving enquiries: {e}")
        return "An error occurred", 500

    enquiries[enquiry_index]['converted'] = not enquiries[enquiry_index]['converted']

    try:
        response = requests.put(JSONBIN_URL, headers=jsonbin_headers, json=enquiries)
        if response.status_code != 200:
            print(f"Failed to update enquiry: {response.status_code}")
            return "An error occurred", 500
    except Exception as e:
        print(f"Error updating enquiry: {e}")
        return "An error occurred", 500

    return redirect('/enquiries')


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect('/enquiries')


@app.route("/env")
def show_environment():
    environment = os.getenv("ENVIRONMENT", "production")
    return f"Current environment: {environment}"



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
                <video:thumbnail_loc>{url_for('static', filename=video['thumbnailUrl'][7:], _external=True)}</video:thumbnail_loc>
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

