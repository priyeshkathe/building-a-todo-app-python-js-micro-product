# Part 1: Hello Flask

## What You Will Learn
- How to create a Flask application
- How to create routes (URLs)
- How to render HTML templates

## Files in This Part
```
part-1-hello-flask/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── templates/
│   ├── index.html      # Home page
│   ├── about.html      # About page
│   └── contact.html    # Contact page
```

## How to Run
```bash
cd part-1-hello-flask
pip install -r requirements.txt
python app.py
```
Open: http://127.0.0.1:5000

## Key Concepts

### 1. Creating Flask App
```python
from flask import Flask
app = Flask(__name__)
```

### 2. Creating Routes
```python
@app.route('/')
def home():
    return render_template('index.html')
```

### 3. Running the Server
```python
app.run(debug=True)
```

## Next Part
In Part 2, we will add a database to store data permanently.
