# =============================================================================
# Part 1: Hello Flask
# =============================================================================
# This is the simplest Flask application.
# We will learn:
#   1. How to create a Flask app
#   2. How to create routes (URLs)
#   3. How to render HTML templates
# =============================================================================

from flask import Flask, render_template

# Create the Flask application
app = Flask(__name__)


# =============================================================================
# ROUTES
# =============================================================================
# A route connects a URL to a Python function.
# When user visits the URL, Flask runs the function.

@app.route('/')
def home():
    """Home page - the main landing page"""
    return render_template('index.html')


@app.route('/about')
def about():
    """About page - information about the app"""
    return render_template('about.html')


@app.route('/contact')
def contact():
    """Contact page - contact information"""
    return render_template('contact.html')


# =============================================================================
# RUN THE SERVER
# =============================================================================
if __name__ == '__main__':
    print("\n" + "="*50)
    print("  Part 1: Hello Flask")
    print("  Open: http://127.0.0.1:5000")
    print("="*50 + "\n")
    app.run(debug=True)


# ============================================
# SELF-STUDY QUESTIONS
# ============================================
# 1. What does @app.route('/') mean?
# 2. What is the purpose of render_template()?
# 3. What happens if you visit a URL that has no route?
# 4. What does debug=True do?
#
# ============================================
# ACTIVITIES - Try These!
# ============================================
# Activity 1: Add a new page
#   - Create a new route @app.route('/services')
#   - Create templates/services.html file
#   - Add a link to it from index.html
#
# Activity 2: Change the port
#   - Change app.run(debug=True) to app.run(debug=True, port=8080)
#   - Open http://127.0.0.1:8080 in browser
#
# Activity 3: Return plain text instead of HTML
#   - Create a route that returns just a string: return "Hello World"
#   - See how it looks different from render_template()
#
# Activity 4: Dynamic route
#   - Create route: @app.route('/hello/<name>')
#   - Function: def hello(name): return f"Hello, {name}!"
#   - Visit: http://127.0.0.1:5000/hello/YourName
# ============================================
