<<<<<<< HEAD
from flask import Flask, render_template_string, request, redirect, url_for, session
import secrets
import re
import sqlite3
import os
from werkzeug.utils import secure_filename
from flask import send_from_directory

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Database setup
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS candidates (name TEXT PRIMARY KEY, description TEXT, party TEXT, image TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS events (datetime TEXT, description TEXT, party TEXT)')
    conn.commit()
    conn.close()

init_db()

# In-memory storage for various functionalities
events = []
posts = []
comments = []
media_links = []
party_votes = {
    "BJP": {"votes": 0, "comments": [], "likes": [], "dislikes": [], "poster": None},
    "Congress": {"votes": 0, "comments": [], "likes": [], "dislikes": [], "poster": None},
    "JDS": {"votes": 0, "comments": [], "likes": [], "dislikes": [], "poster": None},
    "Janata Party": {"votes": 0, "comments": [], "likes": [], "dislikes": [], "poster": None},
    "Independent": {"votes": 0, "comments": [], "likes": [], "dislikes": [], "poster": None},
}

# Survey Analysis HTML
survey_analysis_html = """
<h2>Survey Analysis</h2>
<div>
    <h3>Model Accuracy Comparison</h3>
    <img src="{{ url_for('uploaded_file', filename='model_accuracy_comparison.png') }}" alt="Model Accuracy Comparison" style="max-width:100%;height:auto;">
    <p>Digital campaigns leverage advanced data analytics and machine learning models to optimize outreach and engagement...</p>
    <h3>Voter Engagement Metrics</h3>
    <img src="{{ url_for('uploaded_file', filename='voter_engagement_metrics.png') }}" alt="Voter Engagement Metrics" style="max-width:100%;height:auto;">
    <p>The second graph highlights various metrics for voter engagement...</p>
    <h3>Influence of Election Campaigns</h3>
    <img src="{{ url_for('uploaded_file', filename='influence_of_campaigns.png') }}" alt="Influence of Election Campaigns" style="max-width:100%;height:auto;">
    <p>The pie chart showing how election campaigns influence voting decisions emphasizes the significant impact of digital outreach...</p>
    <h3>Engaging Digital Content</h3>
    <img src="{{ url_for('uploaded_file', filename='engaging_digital_content.png') }}" alt="Engaging Digital Content" style="max-width:100%;height:auto;">
    <p>Understanding which types of digital content engage voters the most is critical for campaign effectiveness...</p>
    <h3>Attention Span for Political Videos</h3>
    <img src="{{ url_for('uploaded_file', filename='attention_span.png') }}" alt="Attention Span for Political Videos" style="max-width:100%;height:auto;">
    <p>The graph illustrating how long viewers typically watch political videos before losing interest sheds light on the importance of concise and impactful messaging...</p>
    <h3>Preferences for Political Ads</h3>
    <img src="{{ url_for('uploaded_file', filename='preferences_for_ads.png') }}" alt="Preferences for Political Ads" style="max-width:100%;height:auto;">
    <p>The breakdown of preferred political ad types shows a clear inclination towards text-based messages with strong narratives...</p>
    <h3>Engagement through Ad Types</h3>
    <img src="{{ url_for('uploaded_file', filename='engagement_through_ads.png') }}" alt="Engagement through Ad Types" style="max-width:100%;height:auto;">
    <p>The pie chart that explores what type of ad would encourage more engagement reveals that voters are drawn to ads that are fun, lighthearted...</p>
    <h3>Effectiveness of Political Ads</h3>
    <img src="{{ url_for('uploaded_file', filename='effectiveness_of_ads.png') }}" alt="Effectiveness of Political Ads" style="max-width:100%;height:auto;">
    <p>The final graphic, which assesses what makes a political ad effective, highlights the importance of humor combined with serious messaging...</p>
    <p>In conclusion, digital campaigns are pivotal in reinforcing democratic values by enhancing voter engagement, informing the electorate, and fostering a responsive political environment...</p>
</div>
"""

# Base HTML structure with animated background images
base_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Digital Election Campaign</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            margin: 0;
            padding: 0;
            overflow-y: scroll;
            height: 100vh;
            position: relative;
        }
        #background {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            animation: slide 60s linear infinite;
            background-size: cover;
        }
        @keyframes slide {
            0% { background-image: url('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQZsWdPvzP6P2l2UroOFjnh8xsWHGwot-DT6g&s'); }
            20% { background-image: url('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ0l8Kj2hjSfD_NQ9BgwLBOAe6Cfy7C1THMtg&s'); }
            40% { background-image: url('https://www.shutterstock.com/image-vector/illustration-handshake-showing-indiaamerica-relationship-260nw-246507976.jpg'); }
            60% { background-image: url('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTmqWlrQvJbwamGxshWlvdijS9Oo61--RUApw&s'); }
            100% { background-image: url('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQZsWdPvzP6P2l2UroOFjnh8xsWHGwot-DT6g&s'); }
        }
        #logo {
            position: fixed;
            top: 40px;
            left: 10px;
            width: 80px;
            height: auto;
        }
        #welcome {
            font-size: 36px;
            font-weight: bold;
            color: blue;
            white-space: nowrap;
            overflow: hidden;
            position: relative;
            animation: marquee 15s linear infinite;
        }
        @keyframes marquee {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }
        nav {
            position: fixed;
            top: 20%;
            left: 10px;
            background: linear-gradient(to right, #ff9933, #ffffff, #138808);
            border-radius: 5px;
            padding: 20px;
            display: none;
            flex-direction: column;
        }
        nav a {
            margin: 10px 0;
            text-decoration: none;
            color: black;
            font-weight: bold;
            font-size: 22px;
            padding: 10px 15px;
            border-radius: 5px;
            transition: background 0.3s;
        }
        nav a:hover { background: deepskyblue; }
        button.toggle-nav {
            position: fixed;
            top: 10px;
            left: 10px;
            background: transparent;
            border: none;
            cursor: pointer;
        }
        button.toggle-nav img { width: 40px; height: auto; }
        main {
            margin-top: 50px;
            padding: 20px;
            display: inline-block;
            max-width: 1300px;
            background: #f9f9f9;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        h2 {
            margin-top: 20px;
            font-size: 28px;
            color: darkblue;
        }
        input[type="text"], input[type="password"], input[type="url"], input[type="date"], input[type="file"], textarea {
            width: calc(100% - 22px);
            padding: 15px;
            font-size: 18px;
            margin: 10px 0;
            border: 2px solid #ccc;
            border-radius: 5px;
        }
        button {
            padding: 15px 20px;
            font-size: 18px;
            background-color: blue;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover { background-color: darkblue; }
        #login-container {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        #login-form {
            background-color: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            width: 400px;
        }
        footer {
            position: absolute;
            bottom: 0;
            width: 100%;
            background-color: lightgray;
            text-align: center;
            padding: 10px;
        }
        .horizontally {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-around;
            margin: 20px 0;
        }
        .box {
            border: 1px solid #ccc;
            border-radius: 5px;
            padding: 20px;
            margin: 10px;
            width: calc(30% - 20px);
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .analytics-box {
            border: 1px solid #ccc;
            border-radius: 5px;
            padding: 40px;
            margin: 10px;
            width: calc(45% - 20px);
            display: flex;
            flex-direction: column;
            align-items: center;
            height: 250px;
        }
        .button-group {
            display: flex;
            justify-content: space-between;
            width: 100%;
        }
        #side-images {
            position: fixed;
            top: 10%;
            right: 10px;
            width: 300px;
            height: 80%;
            overflow: hidden;
        }
        #side-images img {
            width: 100%;
            display: block;
            animation: scroll 3s linear infinite;
        }
        @keyframes scroll {
            0% { transform: translateY(0); }
            100% { transform: translateY(-100%); }
        }
    </style>
    <script>
        function toggleNav() {
            const nav = document.querySelector('nav');
            nav.style.display = nav.style.display === 'flex' ? 'none' : 'flex';
        }
        function showPoster(party) {
            const posters = document.querySelectorAll('.poster');
            posters.forEach(p => p.style.display = 'none');
            if (party) {
                document.getElementById(party + '-poster').style.display = 'block';
            }
        }
    </script>
</head>
<body>
    <img id="logo" src="https://pbs.twimg.com/profile_images/1593492061172379648/a4Qlm8SH_200x200.jpg" alt="Logo">
    <div id="background"></div>
    {% if 'username' in session %}
    <header>
        <div id="welcome">Welcome to Digital Election Campaign Platform</div>
        <button class="toggle-nav" onclick="toggleNav()">
            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQsxsJ-suwBm5udSxF8BHCyTcyz5A3yl35UbQ&s" alt="Home Icon">
        </button>
        <nav>
            <a href="/">Home</a>
            <a href="/live">Live Streaming</a>
            <a href="/candidate">Candidate Profiles</a>
            <a href="/interaction">Voter Interaction</a>
            <a href="/analytics">Data Analytics</a>
            <a href="/calendar">Election Calendar</a>
            <a href="/media">Media Integration</a>
            <a href="/survey-analysis">Survey Analysis</a>
            <a href="/logout">Logout</a>
        </nav>
    </header>
    {% endif %}
    <main>
        {{ content|safe }}
    </main>
    <div id="side-images">
        {% for image in images %}
        <img src="{{ url_for('uploaded_file', filename=image) }}" alt="Screenshot">
        {% endfor %}
    </div>
    <footer>
        <p></p>
    </footer>
</body>
</html>
"""

# Registration HTML
registration_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Register</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(120deg, #84fab0, #8fd3f4);
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        #register-container {
            background: #fff;
            border-radius: 10px;
            padding: 40px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
            width: 400px;
        }
        #register-container h2 {
            text-align: center;
            color: #333;
            margin-bottom: 20px;
        }
        #register-container form {
            display: flex;
            flex-direction: column;
        }
        #register-container input {
            padding: 12px;
            margin: 10px 0;
            border: 1px solid #ccc;
            border-radius: 5px;
            font-size: 16px;
        }
        #register-container button {
            padding: 12px;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            transition: background 0.3s;
        }
        #register-container button:hover { background: #45a049; }
        #register-container p {
            text-align: center;
            margin-top: 15px;
            font-size: 14px;
        }
        #register-container p a {
            color: #007BFF;
            text-decoration: none;
        }
        #register-container p a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div id="register-container">
        <h2>Create Your Account</h2>
        <form method="post" action="/register">
            <input type="text" name="username" placeholder="Enter your username" required>
            <input type="password" name="password" placeholder="Enter your password" required>
            <button type="submit">Register</button>
        </form>
        <p>Already have an account? <a href="/login">Login here</a></p>
    </div>
</body>
</html>
"""

# Forgot Password HTML
forgot_password_html = """
<div id="login-container">
    <div id="login-form">
        <form method="post" action="/reset-password">
            <h2>Forgot Password</h2>
            <input type="email" id="email" name="email" placeholder="Enter your email" required>
            <button type="submit">Send Reset Link</button>
        </form>
    </div>
</div>
"""

# Password Reset HTML
reset_password_html = """
<div id="login-container">
    <div id="login-form">
        <form method="post" action="/change-password">
            <h2>Reset Password</h2>
            <input type="password" id="new-password" name="new-password" placeholder="New Password" required>
            <button type="submit">Reset Password</button>
        </form>
    </div>
</div>
"""

# Login HTML
login_html = """
<div id="login-container">
    <div id="login-form">
        <form method="post" action="/login">
            <h2>Login to Access the Platform</h2>
            <input type="text" id="username" name="username" placeholder="Username" required>
            <div style="position: relative;">
                <input type="password" id="password" name="password" placeholder="Password" required>
                <img id="password-eye" src="https://img.icons8.com/ios-filled/50/000000/invisible.png" style="position: absolute; top: 50%; right: 10px; transform: translateY(-50%);" onclick="togglePasswordVisibility()">
            </div>
            <button type="submit">Login</button>
            <p><a href="/register">Don't have an account? Register here</a></p>
            <p><a href="/forgot-password">Forgot Password?</a></p>
        </form>
    </div>
</div>
"""

# Updated Home Page HTML
home_html = """
<h2>Welcome to the Digital Election Campaign Platform</h2>
<div style="overflow: hidden;">
    <marquee behavior="scroll" direction="left">
        <span>Latest Updates:</span>
        {% for post in posts %}
            <span>{{ post }} &nbsp;&nbsp;&nbsp;</span>
        {% endfor %}
    </marquee>
</div>
<h2>Candidate Profiles</h2>
<div class="horizontally">
    {% for candidate in candidates %}
    <div class="box">
        <h3>{{ candidate['name'] }}</h3>
        <p>{{ candidate['description'] }}</p>
        <p>Party:{{ candidate['party'] }}</p>
        python

Run

Copy
        {{ candidate['party'] }}</p>
        <img src="{{ url_for('static', filename='uploads/' + candidate['image']) }}" alt="Profile Image" style="width:100px;height:100px;">
    </div>
    {% endfor %}
</div>
<h2>Upcoming Events</h2>
<ul>
    {% for event in events %}
        <li>{{ event }}</li>
    {% endfor %}
</ul>
"""

# Candidate Profile Page HTML (Updated)
candidate_profile_html = """
<h2>Candidate Profiles</h2>
<div class="horizontally">
    {% for candidate in candidates %}
    <div class="box">
        <h3>{{ candidate['name'] }}</h3>
        <p>{{ candidate['description'] }}</p>
        <p>Party: {{ candidate['party'] }}</p>
        <img src="{{ url_for('static', filename='uploads/' + candidate['image']) }}" alt="Profile Image" style="width:100px;height:100px;">
        <div class="button-group">
            <form method="post" action="/edit-candidate/{{ candidate['name'] }}">
                <button type="submit">Edit</button>
            </form>
            <form method="post" action="/delete-candidate" style="display:inline;">
                <input type="hidden" name="candidate_name" value="{{ candidate['name'] }}">
                <button type="submit">Delete</button>
            </form>
        </div>
    </div>
    {% endfor %}
</div>
<form method="post" action="/create-candidate" enctype="multipart/form-data">
    <h3>Create Candidate Profile</h3>
    <input type="text" name="candidate_name" placeholder="Candidate Name" required>
    <textarea name="candidate_description" placeholder="Candidate Description" required></textarea>
    <select name="party" required>
        <option value="">Select Party</option>
        <option value="BJP">BJP</option>
        <option value="Congress">Congress</option>
        <option value="JDS">JDS</option>
        <option value="Janata Party">Janata Party</option>
        <option value="Independent">Independent</option>
    </select>
    <input type="file" name="profile_image" accept=".pdf, .jpeg, .jpg, .png" required>
    <button type="submit">Create Profile</button>
</form>
"""

# Voter Interaction Page HTML (Updated)
interaction_html = """
<h2>Voter Interaction</h2>
<div class="horizontally">
    <div class="box">
        <h3>Comments</h3>
        <ul>
            {% for comment in comments %}
                <li>{{ comment }}</li>
            {% endfor %}
        </ul>
        <form method="post" action="/interaction">
            <input type="text" id="comment" name="comment" placeholder="Leave a comment" required>
            <select name="party" onchange="showPoster(this.value)" required>
                <option value="">Select Party</option>
                {% for party in party_votes %}
                    <option value="{{ party }}">{{ party }}</option>
                {% endfor %}
            </select>
            <button type="submit">Submit</button>
        </form>
        <div id="posters">
            {% for party in party_votes %}
            <div class="poster" id="{{ party }}-poster" style="display:none;">
                <h4>{{ party }}</h4>
                {% if party_votes[party]["poster"] %}
                    <img src="{{ url_for('static', filename='uploads/' + party_votes[party]["poster"]) }}" alt="{{ party }} Poster" style="width:300px;height:300px;">
                {% endif %}
            </div>
            {% endfor %}
        </div>
    </div>
</div>
<h3>Like/Dislike</h3>
<form method="post" action="/like-dislike">
    <p>Select a Party to Like/Dislike:</p>
    <select name="party" required>
        {% for party in party_votes %}
            <option value="{{ party }}">{{ party }}</option>
        {% endfor %}
    </select>
    <div class="button-group">
        <button type="submit" name="action" value="like">Like</button>
        <button type="submit" name="action" value="dislike">Dislike</button>
    </div>
</form>
"""

# Data Analytics HTML (Updated)
analytics_html = """
<h2>Data Analytics</h2>
<div style="display: flex; justify-content: center; flex-wrap: wrap;">
    <div class="analytics-box">
        <h3>User Engagement Metrics</h3>
        <p>Total Posts: {{ total_posts }}</p>
        <p>Total Comments: {{ total_comments }}</p>
        <p>Total Likes: {{ total_likes }}</p>
        <p>Total Dislikes: {{ total_dislikes }}</p>
    </div>
    <div class="analytics-box">
        <h3>Party Engagement Metrics</h3>
        <ul>
            {% for party, info in party_votes.items() %}
                <li>{{ party }}: {{ info.comments|length }} comments, {{ info.likes|length }} likes, {{ info.dislikes|length }} dislikes</li>
            {% endfor %}
        </ul>
    </div>
</div>
"""

# Calendar HTML (Updated)
calendar_html = """
<h2>Election Calendar</h2>
<div class="box">
    <p>All upcoming election events and important dates will be listed here.</p>
    <ul>
        {% for event in events %}
            <li>{{ event }}</li>
        {% endfor %}
    </ul>
    <form method="post" action="/add-event">
        <input type="datetime-local" id="event-datetime" name="event-datetime" required>
        <input type="text" id="event-description" name="event-description" placeholder="Event Description" required>
        <select id="party" name="party" required>
            <option value="">Select Party</option>
            <option value="BJP">BJP</option>
            <option value="Congress">Congress</option>
            <option value="JDS">JDS</option>
            <option value="Janata Party">Janata Party</option>
            <option value="Independent">Independent</option>
        </select>
        <button type="submit">Add Event</button>
    </form>
</div>
"""

# Live Streaming Placeholder Page with Media Link
live_streaming_html = """
<h2>Live Streaming</h2>
<div class="box">
    <p>Watch live election coverage and events here.</p>
    {% for media in media_links %}
        <p><a href="{{ media.link }}" target="_blank">{{ media.link }}</a></p>
    {% endfor %}
    <iframe width="560" height="315" src="https://www.youtube.com/embed/live_stream?channel=YOUR_CHANNEL_ID" frameborder="0" allowfullscreen></iframe>
</div>
"""

# Media Integration HTML (Updated)
media_html = """
<h2>Media Integration</h2>
<div class="box">
    <p>Select a Party for Media Integration:</p>
    <form method="post" action="/add-media">
        <select name="party" required>
            <option value="BJP">BJP</option>
            <option value="Congress">Congress</option>
            <option value="JDS">JDS</option>
            <option value="Janata Party">Janata Party</option>
            <option value="Independent">Independent</option>
        </select>
        <input type="url" id="media-link" name="media-link" placeholder="Embed Media Link" required>
        <button type="submit">Add Media</button>
    </form>
    <h3>Upload Campaign Poster</h3>
    <form method="post" action="/upload-poster" enctype="multipart/form-data">
        <select name="party" required>
            <option value="BJP">BJP</option>
            <option value="Congress">Congress</option>
            <option value="JDS">JDS</option>
            <option value="Janata Party">Janata Party</option>
            <option value="Independent">Independent</option>
        </select>
        <input type="file" name="poster" accept="image/*" required>
        <button type="submit">Upload Poster</button>
    </form>
</div>
"""

# Password strength validation
def is_password_strong(password):
    return (len(password) >= 6 and re.search(r'[A-Z]', password) and
            re.search(r'[a-z]', password) and re.search(r'[0-9]', password) and
            re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

# Function to save a candidate to the database
def save_candidate_to_db(candidate):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('INSERT INTO candidates (name, description, party, image) VALUES (?, ?, ?, ?)',
              (candidate['name'], candidate['description'], candidate['party'], candidate['image']))
    conn.commit()
    conn.close()

# Function to fetch all candidates from the database
def fetch_candidates_from_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM candidates')
    candidates = c.fetchall()
    conn.close()
    return [{'name': name, 'description': description, 'party': party, 'image': image} for name, description, party, image in candidates]

# Route for Home
@app.route('/')
def home():
    if 'username' in session:
        candidates = fetch_candidates_from_db()  # Fetch candidates from DB
        content = render_template_string(home_html, posts=posts, candidates=candidates, events=events)
        return render_template_string(base_html, content=content)
    return redirect(url_for('login'))

# Function to list images from the specified directory
def list_images():
    image_folder = "/home/ubuntu/Desktop/Project"
    return [f for f in os.listdir(image_folder) if allowed_file(f)]

# Allowed file types
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'jpeg', 'jpg', 'png', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/create-candidate', methods=['POST'])
def create_candidate():
    if request.method == 'POST':
        candidate_name = request.form['candidate_name']
        candidate_description = request.form['candidate_description']
        party = request.form['party']
        profile_image = request.files['profile_image']

        # Ensure the directory exists
        upload_dir = os.path.join(app.root_path, 'static', 'uploads')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # Save the image file
        if profile_image and allowed_file(profile_image.filename):
            filename = secure_filename(profile_image.filename)
            filepath = os.path.join(upload_dir, filename)
            profile_image.save(filepath)

            candidate = {
                "name": candidate_name,
                "description": candidate_description,
                "party": party,
                "image": filename
            }
            save_candidate_to_db(candidate)  # Save candidate to DB
            return redirect(url_for('candidate'))
        else:
            return "Invalid file type. Allowed: jpeg, jpg, png, pdf", 400

@app.route('/candidate', methods=['GET'])
def candidate():
    candidates = fetch_candidates_from_db()  # Fetch candidates from DB
    content = render_template_string(candidate_profile_html, candidates=candidates)
    return render_template_string(base_html, content=content)

@app.route('/edit-candidate/<candidate_name>', methods=['GET', 'POST'])
def edit_candidate(candidate_name):
    if request.method == 'POST':
        candidate_description = request.form.get('candidate_description')
        candidate_party = request.form.get('party')

        # Update candidate in the database
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('UPDATE candidates SET description = ?, party = ? WHERE name = ?', (candidate_description, candidate_party, candidate_name))
        conn.commit()
        profile_image = request.files.get('profile_image')
        if profile_image and allowed_file(profile_image.filename):
            filename = secure_filename(profile_image.filename)
            filepath = os.path.join('static/uploads', filename)
            profile_image.save(filepath)
            c.execute('UPDATE candidates SET image = ? WHERE name = ?', (filename, candidate_name))
            conn.commit()

        conn.close()
        return redirect(url_for('candidate'))

    candidate = next((c for c in fetch_candidates_from_db() if c['name'] == candidate_name), None)
    content = render_template_string("""
    <h2>Edit Candidate</h2>
    <form method="post" action="/edit-candidate/{{ candidate['name'] }}" enctype="multipart/form-data">
        <input type="text" name="candidate_name" value="{{ candidate['name'] }}" readonly required>
        <textarea name="candidate_description" placeholder="Candidate Description" required>{{ candidate['description'] }}</textarea>
        <select name="party" required>
            <option value="{{ candidate['party'] }}">{{ candidate['party'] }}</option>
            <option value="BJP">BJP</option>
            <option value="Congress">Congress</option>
            <option value="JDS">JDS</option>
            <option value="Janata Party">Janata Party</option>
            <option value="Independent">Independent</option>
        </select>
        <input type="file" name="profile_image" accept=".pdf, .jpeg, .jpg, .png">
        <button type="submit">Update Profile</button>
    </form>
    """, candidate=candidate)
    return render_template_string(base_html, content=content)

@app.route('/delete-candidate', methods=['POST'])
def delete_candidate():
    candidate_name = request.form['candidate_name']
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('DELETE FROM candidates WHERE name = ?', (candidate_name,))
    conn.commit()
    conn.close()
    return redirect(url_for('candidate'))

@app.route('/upload-poster', methods=['POST'])
def upload_poster():
    party = request.form['party']
    poster = request.files['poster']
    if poster and allowed_file(poster.filename):
        filename = secure_filename(poster.filename)
        filepath = os.path.join('static/uploads', filename)
        poster.save(filepath)
        party_votes[party]["poster"] = filename
        return "Poster uploaded successfully."
    return "Invalid file type."

@app.route('/interaction', methods=['GET', 'POST'])
def interaction():
    if request.method == 'POST':
        comment = request.form['comment']
        party = request.form['party']
        comments.append(comment)
        party_votes[party]["comments"].append(comment)
        return redirect(url_for('interaction'))

    content = render_template_string(interaction_html, comments=comments, party_votes=party_votes)
    return render_template_string(base_html, content=content)

@app.route('/analytics')
def analytics():
    total_posts = len(posts)
    total_comments = len(comments)
    total_likes = sum(len(info["likes"]) for info in party_votes.values())
    total_dislikes = sum(len(info["dislikes"]) for info in party_votes.values())

    content = render_template_string(analytics_html, total_posts=total_posts, total_comments=total_comments, total_likes=total_likes, total_dislikes=total_dislikes, party_votes=party_votes)
    return render_template_string(base_html, content=content)

@app.route('/calendar')
def calendar():
    content = render_template_string(calendar_html, events=events)
    return render_template_string(base_html, content=content)

@app.route('/live')
def live_streaming():
    content = render_template_string(live_streaming_html, media_links=media_links)
    return render_template_string(base_html, content=content)

@app.route('/media', methods=['GET', 'POST'])
def media():
    if request.method == 'POST':
        media_link = request.form['media-link']
        party = request.form['party']
        media_links.append({"link": media_link, "party": party})
        return redirect(url_for('media'))

    content = render_template_string(media_html, media_links=media_links)
    return render_template_string(base_html, content=content)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template_string(registration_html)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if is_password_strong(password):
            try:
                conn = sqlite3.connect('users.db')
                c = conn.cursor()
                c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
                conn.commit()
                conn.close()
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                return "Username already exists!"
        else:
            return "Password is not strong enough!"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return "Invalid username or password!"
    content = render_template_string(login_html)
    return render_template_string(base_html, content=content)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('/home/ubuntu/Desktop/Project', filename)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        return "Reset link sent to your email."
    content = render_template_string(forgot_password_html)
    return render_template_string(base_html, content=content)

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        new_password = request.form['new-password']
        return "Password has been reset."
    content = render_template_string(reset_password_html)
    return render_template_string(base_html, content=content)

@app.route('/add-event', methods=['POST'])
def add_event():
    event_datetime = request.form['event-datetime']
    event_description = request.form['event-description']
    party = request.form['party']
    events.append(f"{event_datetime}: {event_description} for {party}")
    return redirect(url_for('calendar')) 
@app.route('/add-media', methods=['POST'])
def add_media():
    media_link = request.form['media-link']
    party = request.form['party']
    media_links.append({"link": media_link, "party": party}) 
    return redirect(url_for('media'))


@app.route('/vote', methods=['POST'])
def vote():
    party = request.form['party']
    party_votes[party]["votes"] += 1
    return redirect(url_for('interaction'))

@app.route('/like-dislike', methods=['POST'])
def like_dislike():
    party = request.form['party']
    action = request.form['action']
    if action == "like":
        party_votes[party]["likes"].append(session['username'])
    else:
        party_votes[party]["dislikes"].append(session['username'])
    return redirect(url_for('interaction'))

@app.route('/survey-analysis')
def survey_analysis():
    content = render_template_string(survey_analysis_html)
    return render_template_string(base_html, content=content)

if __name__ == '__main__':
=======
from flask import Flask, render_template_string, request, redirect, url_for, session
import secrets
import re
import sqlite3
import os
from werkzeug.utils import secure_filename
from flask import send_from_directory

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Database setup
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS candidates (name TEXT PRIMARY KEY, description TEXT, party TEXT, image TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS events (datetime TEXT, description TEXT, party TEXT)')
    conn.commit()
    conn.close()

init_db()

# In-memory storage for various functionalities
events = []
posts = []
comments = []
media_links = []
party_votes = {
    "BJP": {"votes": 0, "comments": [], "likes": [], "dislikes": [], "poster": None},
    "Congress": {"votes": 0, "comments": [], "likes": [], "dislikes": [], "poster": None},
    "JDS": {"votes": 0, "comments": [], "likes": [], "dislikes": [], "poster": None},
    "Janata Party": {"votes": 0, "comments": [], "likes": [], "dislikes": [], "poster": None},
    "Independent": {"votes": 0, "comments": [], "likes": [], "dislikes": [], "poster": None},
}

# Survey Analysis HTML
survey_analysis_html = """
<h2>Survey Analysis</h2>
<div>
    <h3>Model Accuracy Comparison</h3>
    <img src="{{ url_for('uploaded_file', filename='model_accuracy_comparison.png') }}" alt="Model Accuracy Comparison" style="max-width:100%;height:auto;">
    <p>Digital campaigns leverage advanced data analytics and machine learning models to optimize outreach and engagement...</p>
    <h3>Voter Engagement Metrics</h3>
    <img src="{{ url_for('uploaded_file', filename='voter_engagement_metrics.png') }}" alt="Voter Engagement Metrics" style="max-width:100%;height:auto;">
    <p>The second graph highlights various metrics for voter engagement...</p>
    <h3>Influence of Election Campaigns</h3>
    <img src="{{ url_for('uploaded_file', filename='influence_of_campaigns.png') }}" alt="Influence of Election Campaigns" style="max-width:100%;height:auto;">
    <p>The pie chart showing how election campaigns influence voting decisions emphasizes the significant impact of digital outreach...</p>
    <h3>Engaging Digital Content</h3>
    <img src="{{ url_for('uploaded_file', filename='engaging_digital_content.png') }}" alt="Engaging Digital Content" style="max-width:100%;height:auto;">
    <p>Understanding which types of digital content engage voters the most is critical for campaign effectiveness...</p>
    <h3>Attention Span for Political Videos</h3>
    <img src="{{ url_for('uploaded_file', filename='attention_span.png') }}" alt="Attention Span for Political Videos" style="max-width:100%;height:auto;">
    <p>The graph illustrating how long viewers typically watch political videos before losing interest sheds light on the importance of concise and impactful messaging...</p>
    <h3>Preferences for Political Ads</h3>
    <img src="{{ url_for('uploaded_file', filename='preferences_for_ads.png') }}" alt="Preferences for Political Ads" style="max-width:100%;height:auto;">
    <p>The breakdown of preferred political ad types shows a clear inclination towards text-based messages with strong narratives...</p>
    <h3>Engagement through Ad Types</h3>
    <img src="{{ url_for('uploaded_file', filename='engagement_through_ads.png') }}" alt="Engagement through Ad Types" style="max-width:100%;height:auto;">
    <p>The pie chart that explores what type of ad would encourage more engagement reveals that voters are drawn to ads that are fun, lighthearted...</p>
    <h3>Effectiveness of Political Ads</h3>
    <img src="{{ url_for('uploaded_file', filename='effectiveness_of_ads.png') }}" alt="Effectiveness of Political Ads" style="max-width:100%;height:auto;">
    <p>The final graphic, which assesses what makes a political ad effective, highlights the importance of humor combined with serious messaging...</p>
    <p>In conclusion, digital campaigns are pivotal in reinforcing democratic values by enhancing voter engagement, informing the electorate, and fostering a responsive political environment...</p>
</div>
"""

# Base HTML structure with animated background images
base_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Digital Election Campaign</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            margin: 0;
            padding: 0;
            overflow-y: scroll;
            height: 100vh;
            position: relative;
        }
        #background {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            animation: slide 60s linear infinite;
            background-size: cover;
        }
        @keyframes slide {
            0% { background-image: url('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQZsWdPvzP6P2l2UroOFjnh8xsWHGwot-DT6g&s'); }
            20% { background-image: url('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ0l8Kj2hjSfD_NQ9BgwLBOAe6Cfy7C1THMtg&s'); }
            40% { background-image: url('https://www.shutterstock.com/image-vector/illustration-handshake-showing-indiaamerica-relationship-260nw-246507976.jpg'); }
            60% { background-image: url('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTmqWlrQvJbwamGxshWlvdijS9Oo61--RUApw&s'); }
            100% { background-image: url('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQZsWdPvzP6P2l2UroOFjnh8xsWHGwot-DT6g&s'); }
        }
        #logo {
            position: fixed;
            top: 40px;
            left: 10px;
            width: 80px;
            height: auto;
        }
        #welcome {
            font-size: 36px;
            font-weight: bold;
            color: blue;
            white-space: nowrap;
            overflow: hidden;
            position: relative;
            animation: marquee 15s linear infinite;
        }
        @keyframes marquee {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }
        nav {
            position: fixed;
            top: 20%;
            left: 10px;
            background: linear-gradient(to right, #ff9933, #ffffff, #138808);
            border-radius: 5px;
            padding: 20px;
            display: none;
            flex-direction: column;
        }
        nav a {
            margin: 10px 0;
            text-decoration: none;
            color: black;
            font-weight: bold;
            font-size: 22px;
            padding: 10px 15px;
            border-radius: 5px;
            transition: background 0.3s;
        }
        nav a:hover { background: deepskyblue; }
        button.toggle-nav {
            position: fixed;
            top: 10px;
            left: 10px;
            background: transparent;
            border: none;
            cursor: pointer;
        }
        button.toggle-nav img { width: 40px; height: auto; }
        main {
            margin-top: 50px;
            padding: 20px;
            display: inline-block;
            max-width: 1300px;
            background: #f9f9f9;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        h2 {
            margin-top: 20px;
            font-size: 28px;
            color: darkblue;
        }
        input[type="text"], input[type="password"], input[type="url"], input[type="date"], input[type="file"], textarea {
            width: calc(100% - 22px);
            padding: 15px;
            font-size: 18px;
            margin: 10px 0;
            border: 2px solid #ccc;
            border-radius: 5px;
        }
        button {
            padding: 15px 20px;
            font-size: 18px;
            background-color: blue;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover { background-color: darkblue; }
        #login-container {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        #login-form {
            background-color: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            width: 400px;
        }
        footer {
            position: absolute;
            bottom: 0;
            width: 100%;
            background-color: lightgray;
            text-align: center;
            padding: 10px;
        }
        .horizontally {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-around;
            margin: 20px 0;
        }
        .box {
            border: 1px solid #ccc;
            border-radius: 5px;
            padding: 20px;
            margin: 10px;
            width: calc(30% - 20px);
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .analytics-box {
            border: 1px solid #ccc;
            border-radius: 5px;
            padding: 40px;
            margin: 10px;
            width: calc(45% - 20px);
            display: flex;
            flex-direction: column;
            align-items: center;
            height: 250px;
        }
        .button-group {
            display: flex;
            justify-content: space-between;
            width: 100%;
        }
        #side-images {
            position: fixed;
            top: 10%;
            right: 10px;
            width: 300px;
            height: 80%;
            overflow: hidden;
        }
        #side-images img {
            width: 100%;
            display: block;
            animation: scroll 3s linear infinite;
        }
        @keyframes scroll {
            0% { transform: translateY(0); }
            100% { transform: translateY(-100%); }
        }
    </style>
    <script>
        function toggleNav() {
            const nav = document.querySelector('nav');
            nav.style.display = nav.style.display === 'flex' ? 'none' : 'flex';
        }
        function showPoster(party) {
            const posters = document.querySelectorAll('.poster');
            posters.forEach(p => p.style.display = 'none');
            if (party) {
                document.getElementById(party + '-poster').style.display = 'block';
            }
        }
    </script>
</head>
<body>
    <img id="logo" src="https://pbs.twimg.com/profile_images/1593492061172379648/a4Qlm8SH_200x200.jpg" alt="Logo">
    <div id="background"></div>
    {% if 'username' in session %}
    <header>
        <div id="welcome">Welcome to Digital Election Campaign Platform</div>
        <button class="toggle-nav" onclick="toggleNav()">
            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQsxsJ-suwBm5udSxF8BHCyTcyz5A3yl35UbQ&s" alt="Home Icon">
        </button>
        <nav>
            <a href="/">Home</a>
            <a href="/live">Live Streaming</a>
            <a href="/candidate">Candidate Profiles</a>
            <a href="/interaction">Voter Interaction</a>
            <a href="/analytics">Data Analytics</a>
            <a href="/calendar">Election Calendar</a>
            <a href="/media">Media Integration</a>
            <a href="/survey-analysis">Survey Analysis</a>
            <a href="/logout">Logout</a>
        </nav>
    </header>
    {% endif %}
    <main>
        {{ content|safe }}
    </main>
    <div id="side-images">
        {% for image in images %}
        <img src="{{ url_for('uploaded_file', filename=image) }}" alt="Screenshot">
        {% endfor %}
    </div>
    <footer>
        <p></p>
    </footer>
</body>
</html>
"""

# Registration HTML
registration_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Register</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(120deg, #84fab0, #8fd3f4);
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        #register-container {
            background: #fff;
            border-radius: 10px;
            padding: 40px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
            width: 400px;
        }
        #register-container h2 {
            text-align: center;
            color: #333;
            margin-bottom: 20px;
        }
        #register-container form {
            display: flex;
            flex-direction: column;
        }
        #register-container input {
            padding: 12px;
            margin: 10px 0;
            border: 1px solid #ccc;
            border-radius: 5px;
            font-size: 16px;
        }
        #register-container button {
            padding: 12px;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            transition: background 0.3s;
        }
        #register-container button:hover { background: #45a049; }
        #register-container p {
            text-align: center;
            margin-top: 15px;
            font-size: 14px;
        }
        #register-container p a {
            color: #007BFF;
            text-decoration: none;
        }
        #register-container p a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div id="register-container">
        <h2>Create Your Account</h2>
        <form method="post" action="/register">
            <input type="text" name="username" placeholder="Enter your username" required>
            <input type="password" name="password" placeholder="Enter your password" required>
            <button type="submit">Register</button>
        </form>
        <p>Already have an account? <a href="/login">Login here</a></p>
    </div>
</body>
</html>
"""

# Forgot Password HTML
forgot_password_html = """
<div id="login-container">
    <div id="login-form">
        <form method="post" action="/reset-password">
            <h2>Forgot Password</h2>
            <input type="email" id="email" name="email" placeholder="Enter your email" required>
            <button type="submit">Send Reset Link</button>
        </form>
    </div>
</div>
"""

# Password Reset HTML
reset_password_html = """
<div id="login-container">
    <div id="login-form">
        <form method="post" action="/change-password">
            <h2>Reset Password</h2>
            <input type="password" id="new-password" name="new-password" placeholder="New Password" required>
            <button type="submit">Reset Password</button>
        </form>
    </div>
</div>
"""

# Login HTML
login_html = """
<div id="login-container">
    <div id="login-form">
        <form method="post" action="/login">
            <h2>Login to Access the Platform</h2>
            <input type="text" id="username" name="username" placeholder="Username" required>
            <div style="position: relative;">
                <input type="password" id="password" name="password" placeholder="Password" required>
                <img id="password-eye" src="https://img.icons8.com/ios-filled/50/000000/invisible.png" style="position: absolute; top: 50%; right: 10px; transform: translateY(-50%);" onclick="togglePasswordVisibility()">
            </div>
            <button type="submit">Login</button>
            <p><a href="/register">Don't have an account? Register here</a></p>
            <p><a href="/forgot-password">Forgot Password?</a></p>
        </form>
    </div>
</div>
"""

# Updated Home Page HTML
home_html = """
<h2>Welcome to the Digital Election Campaign Platform</h2>
<div style="overflow: hidden;">
    <marquee behavior="scroll" direction="left">
        <span>Latest Updates:</span>
        {% for post in posts %}
            <span>{{ post }} &nbsp;&nbsp;&nbsp;</span>
        {% endfor %}
    </marquee>
</div>
<h2>Candidate Profiles</h2>
<div class="horizontally">
    {% for candidate in candidates %}
    <div class="box">
        <h3>{{ candidate['name'] }}</h3>
        <p>{{ candidate['description'] }}</p>
        <p>Party:{{ candidate['party'] }}</p>
        python

Run

Copy
        {{ candidate['party'] }}</p>
        <img src="{{ url_for('static', filename='uploads/' + candidate['image']) }}" alt="Profile Image" style="width:100px;height:100px;">
    </div>
    {% endfor %}
</div>
<h2>Upcoming Events</h2>
<ul>
    {% for event in events %}
        <li>{{ event }}</li>
    {% endfor %}
</ul>
"""

# Candidate Profile Page HTML (Updated)
candidate_profile_html = """
<h2>Candidate Profiles</h2>
<div class="horizontally">
    {% for candidate in candidates %}
    <div class="box">
        <h3>{{ candidate['name'] }}</h3>
        <p>{{ candidate['description'] }}</p>
        <p>Party: {{ candidate['party'] }}</p>
        <img src="{{ url_for('static', filename='uploads/' + candidate['image']) }}" alt="Profile Image" style="width:100px;height:100px;">
        <div class="button-group">
            <form method="post" action="/edit-candidate/{{ candidate['name'] }}">
                <button type="submit">Edit</button>
            </form>
            <form method="post" action="/delete-candidate" style="display:inline;">
                <input type="hidden" name="candidate_name" value="{{ candidate['name'] }}">
                <button type="submit">Delete</button>
            </form>
        </div>
    </div>
    {% endfor %}
</div>
<form method="post" action="/create-candidate" enctype="multipart/form-data">
    <h3>Create Candidate Profile</h3>
    <input type="text" name="candidate_name" placeholder="Candidate Name" required>
    <textarea name="candidate_description" placeholder="Candidate Description" required></textarea>
    <select name="party" required>
        <option value="">Select Party</option>
        <option value="BJP">BJP</option>
        <option value="Congress">Congress</option>
        <option value="JDS">JDS</option>
        <option value="Janata Party">Janata Party</option>
        <option value="Independent">Independent</option>
    </select>
    <input type="file" name="profile_image" accept=".pdf, .jpeg, .jpg, .png" required>
    <button type="submit">Create Profile</button>
</form>
"""

# Voter Interaction Page HTML (Updated)
interaction_html = """
<h2>Voter Interaction</h2>
<div class="horizontally">
    <div class="box">
        <h3>Comments</h3>
        <ul>
            {% for comment in comments %}
                <li>{{ comment }}</li>
            {% endfor %}
        </ul>
        <form method="post" action="/interaction">
            <input type="text" id="comment" name="comment" placeholder="Leave a comment" required>
            <select name="party" onchange="showPoster(this.value)" required>
                <option value="">Select Party</option>
                {% for party in party_votes %}
                    <option value="{{ party }}">{{ party }}</option>
                {% endfor %}
            </select>
            <button type="submit">Submit</button>
        </form>
        <div id="posters">
            {% for party in party_votes %}
            <div class="poster" id="{{ party }}-poster" style="display:none;">
                <h4>{{ party }}</h4>
                {% if party_votes[party]["poster"] %}
                    <img src="{{ url_for('static', filename='uploads/' + party_votes[party]["poster"]) }}" alt="{{ party }} Poster" style="width:300px;height:300px;">
                {% endif %}
            </div>
            {% endfor %}
        </div>
    </div>
</div>
<h3>Like/Dislike</h3>
<form method="post" action="/like-dislike">
    <p>Select a Party to Like/Dislike:</p>
    <select name="party" required>
        {% for party in party_votes %}
            <option value="{{ party }}">{{ party }}</option>
        {% endfor %}
    </select>
    <div class="button-group">
        <button type="submit" name="action" value="like">Like</button>
        <button type="submit" name="action" value="dislike">Dislike</button>
    </div>
</form>
"""

# Data Analytics HTML (Updated)
analytics_html = """
<h2>Data Analytics</h2>
<div style="display: flex; justify-content: center; flex-wrap: wrap;">
    <div class="analytics-box">
        <h3>User Engagement Metrics</h3>
        <p>Total Posts: {{ total_posts }}</p>
        <p>Total Comments: {{ total_comments }}</p>
        <p>Total Likes: {{ total_likes }}</p>
        <p>Total Dislikes: {{ total_dislikes }}</p>
    </div>
    <div class="analytics-box">
        <h3>Party Engagement Metrics</h3>
        <ul>
            {% for party, info in party_votes.items() %}
                <li>{{ party }}: {{ info.comments|length }} comments, {{ info.likes|length }} likes, {{ info.dislikes|length }} dislikes</li>
            {% endfor %}
        </ul>
    </div>
</div>
"""

# Calendar HTML (Updated)
calendar_html = """
<h2>Election Calendar</h2>
<div class="box">
    <p>All upcoming election events and important dates will be listed here.</p>
    <ul>
        {% for event in events %}
            <li>{{ event }}</li>
        {% endfor %}
    </ul>
    <form method="post" action="/add-event">
        <input type="datetime-local" id="event-datetime" name="event-datetime" required>
        <input type="text" id="event-description" name="event-description" placeholder="Event Description" required>
        <select id="party" name="party" required>
            <option value="">Select Party</option>
            <option value="BJP">BJP</option>
            <option value="Congress">Congress</option>
            <option value="JDS">JDS</option>
            <option value="Janata Party">Janata Party</option>
            <option value="Independent">Independent</option>
        </select>
        <button type="submit">Add Event</button>
    </form>
</div>
"""

# Live Streaming Placeholder Page with Media Link
live_streaming_html = """
<h2>Live Streaming</h2>
<div class="box">
    <p>Watch live election coverage and events here.</p>
    {% for media in media_links %}
        <p><a href="{{ media.link }}" target="_blank">{{ media.link }}</a></p>
    {% endfor %}
    <iframe width="560" height="315" src="https://www.youtube.com/embed/live_stream?channel=YOUR_CHANNEL_ID" frameborder="0" allowfullscreen></iframe>
</div>
"""

# Media Integration HTML (Updated)
media_html = """
<h2>Media Integration</h2>
<div class="box">
    <p>Select a Party for Media Integration:</p>
    <form method="post" action="/add-media">
        <select name="party" required>
            <option value="BJP">BJP</option>
            <option value="Congress">Congress</option>
            <option value="JDS">JDS</option>
            <option value="Janata Party">Janata Party</option>
            <option value="Independent">Independent</option>
        </select>
        <input type="url" id="media-link" name="media-link" placeholder="Embed Media Link" required>
        <button type="submit">Add Media</button>
    </form>
    <h3>Upload Campaign Poster</h3>
    <form method="post" action="/upload-poster" enctype="multipart/form-data">
        <select name="party" required>
            <option value="BJP">BJP</option>
            <option value="Congress">Congress</option>
            <option value="JDS">JDS</option>
            <option value="Janata Party">Janata Party</option>
            <option value="Independent">Independent</option>
        </select>
        <input type="file" name="poster" accept="image/*" required>
        <button type="submit">Upload Poster</button>
    </form>
</div>
"""

# Password strength validation
def is_password_strong(password):
    return (len(password) >= 6 and re.search(r'[A-Z]', password) and
            re.search(r'[a-z]', password) and re.search(r'[0-9]', password) and
            re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

# Function to save a candidate to the database
def save_candidate_to_db(candidate):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('INSERT INTO candidates (name, description, party, image) VALUES (?, ?, ?, ?)',
              (candidate['name'], candidate['description'], candidate['party'], candidate['image']))
    conn.commit()
    conn.close()

# Function to fetch all candidates from the database
def fetch_candidates_from_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM candidates')
    candidates = c.fetchall()
    conn.close()
    return [{'name': name, 'description': description, 'party': party, 'image': image} for name, description, party, image in candidates]

# Route for Home
@app.route('/')
def home():
    if 'username' in session:
        candidates = fetch_candidates_from_db()  # Fetch candidates from DB
        content = render_template_string(home_html, posts=posts, candidates=candidates, events=events)
        return render_template_string(base_html, content=content)
    return redirect(url_for('login'))

# Function to list images from the specified directory
def list_images():
    image_folder = "/home/ubuntu/Desktop/Project"
    return [f for f in os.listdir(image_folder) if allowed_file(f)]

# Allowed file types
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'jpeg', 'jpg', 'png', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/create-candidate', methods=['POST'])
def create_candidate():
    if request.method == 'POST':
        candidate_name = request.form['candidate_name']
        candidate_description = request.form['candidate_description']
        party = request.form['party']
        profile_image = request.files['profile_image']

        # Ensure the directory exists
        upload_dir = os.path.join(app.root_path, 'static', 'uploads')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # Save the image file
        if profile_image and allowed_file(profile_image.filename):
            filename = secure_filename(profile_image.filename)
            filepath = os.path.join(upload_dir, filename)
            profile_image.save(filepath)

            candidate = {
                "name": candidate_name,
                "description": candidate_description,
                "party": party,
                "image": filename
            }
            save_candidate_to_db(candidate)  # Save candidate to DB
            return redirect(url_for('candidate'))
        else:
            return "Invalid file type. Allowed: jpeg, jpg, png, pdf", 400

@app.route('/candidate', methods=['GET'])
def candidate():
    candidates = fetch_candidates_from_db()  # Fetch candidates from DB
    content = render_template_string(candidate_profile_html, candidates=candidates)
    return render_template_string(base_html, content=content)

@app.route('/edit-candidate/<candidate_name>', methods=['GET', 'POST'])
def edit_candidate(candidate_name):
    if request.method == 'POST':
        candidate_description = request.form.get('candidate_description')
        candidate_party = request.form.get('party')

        # Update candidate in the database
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('UPDATE candidates SET description = ?, party = ? WHERE name = ?', (candidate_description, candidate_party, candidate_name))
        conn.commit()
        profile_image = request.files.get('profile_image')
        if profile_image and allowed_file(profile_image.filename):
            filename = secure_filename(profile_image.filename)
            filepath = os.path.join('static/uploads', filename)
            profile_image.save(filepath)
            c.execute('UPDATE candidates SET image = ? WHERE name = ?', (filename, candidate_name))
            conn.commit()

        conn.close()
        return redirect(url_for('candidate'))

    candidate = next((c for c in fetch_candidates_from_db() if c['name'] == candidate_name), None)
    content = render_template_string("""
    <h2>Edit Candidate</h2>
    <form method="post" action="/edit-candidate/{{ candidate['name'] }}" enctype="multipart/form-data">
        <input type="text" name="candidate_name" value="{{ candidate['name'] }}" readonly required>
        <textarea name="candidate_description" placeholder="Candidate Description" required>{{ candidate['description'] }}</textarea>
        <select name="party" required>
            <option value="{{ candidate['party'] }}">{{ candidate['party'] }}</option>
            <option value="BJP">BJP</option>
            <option value="Congress">Congress</option>
            <option value="JDS">JDS</option>
            <option value="Janata Party">Janata Party</option>
            <option value="Independent">Independent</option>
        </select>
        <input type="file" name="profile_image" accept=".pdf, .jpeg, .jpg, .png">
        <button type="submit">Update Profile</button>
    </form>
    """, candidate=candidate)
    return render_template_string(base_html, content=content)

@app.route('/delete-candidate', methods=['POST'])
def delete_candidate():
    candidate_name = request.form['candidate_name']
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('DELETE FROM candidates WHERE name = ?', (candidate_name,))
    conn.commit()
    conn.close()
    return redirect(url_for('candidate'))

@app.route('/upload-poster', methods=['POST'])
def upload_poster():
    party = request.form['party']
    poster = request.files['poster']
    if poster and allowed_file(poster.filename):
        filename = secure_filename(poster.filename)
        filepath = os.path.join('static/uploads', filename)
        poster.save(filepath)
        party_votes[party]["poster"] = filename
        return "Poster uploaded successfully."
    return "Invalid file type."

@app.route('/interaction', methods=['GET', 'POST'])
def interaction():
    if request.method == 'POST':
        comment = request.form['comment']
        party = request.form['party']
        comments.append(comment)
        party_votes[party]["comments"].append(comment)
        return redirect(url_for('interaction'))

    content = render_template_string(interaction_html, comments=comments, party_votes=party_votes)
    return render_template_string(base_html, content=content)

@app.route('/analytics')
def analytics():
    total_posts = len(posts)
    total_comments = len(comments)
    total_likes = sum(len(info["likes"]) for info in party_votes.values())
    total_dislikes = sum(len(info["dislikes"]) for info in party_votes.values())

    content = render_template_string(analytics_html, total_posts=total_posts, total_comments=total_comments, total_likes=total_likes, total_dislikes=total_dislikes, party_votes=party_votes)
    return render_template_string(base_html, content=content)

@app.route('/calendar')
def calendar():
    content = render_template_string(calendar_html, events=events)
    return render_template_string(base_html, content=content)

@app.route('/live')
def live_streaming():
    content = render_template_string(live_streaming_html, media_links=media_links)
    return render_template_string(base_html, content=content)

@app.route('/media', methods=['GET', 'POST'])
def media():
    if request.method == 'POST':
        media_link = request.form['media-link']
        party = request.form['party']
        media_links.append({"link": media_link, "party": party})
        return redirect(url_for('media'))

    content = render_template_string(media_html, media_links=media_links)
    return render_template_string(base_html, content=content)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template_string(registration_html)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if is_password_strong(password):
            try:
                conn = sqlite3.connect('users.db')
                c = conn.cursor()
                c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
                conn.commit()
                conn.close()
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                return "Username already exists!"
        else:
            return "Password is not strong enough!"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return "Invalid username or password!"
    content = render_template_string(login_html)
    return render_template_string(base_html, content=content)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('/home/ubuntu/Desktop/Project', filename)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        return "Reset link sent to your email."
    content = render_template_string(forgot_password_html)
    return render_template_string(base_html, content=content)

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        new_password = request.form['new-password']
        return "Password has been reset."
    content = render_template_string(reset_password_html)
    return render_template_string(base_html, content=content)

@app.route('/add-event', methods=['POST'])
def add_event():
    event_datetime = request.form['event-datetime']
    event_description = request.form['event-description']
    party = request.form['party']
    events.append(f"{event_datetime}: {event_description} for {party}")
    return redirect(url_for('calendar')) 
@app.route('/add-media', methods=['POST'])
def add_media():
    media_link = request.form['media-link']
    party = request.form['party']
    media_links.append({"link": media_link, "party": party}) 
    return redirect(url_for('media'))


@app.route('/vote', methods=['POST'])
def vote():
    party = request.form['party']
    party_votes[party]["votes"] += 1
    return redirect(url_for('interaction'))

@app.route('/like-dislike', methods=['POST'])
def like_dislike():
    party = request.form['party']
    action = request.form['action']
    if action == "like":
        party_votes[party]["likes"].append(session['username'])
    else:
        party_votes[party]["dislikes"].append(session['username'])
    return redirect(url_for('interaction'))

@app.route('/survey-analysis')
def survey_analysis():
    content = render_template_string(survey_analysis_html)
    return render_template_string(base_html, content=content)

if __name__ == '__main__':
>>>>>>> 9a459e916bc9154caedad976b03ce99befdd41a0
    app.run(debug=True, port=5801)