# Nigel Assistant

Nigel Assistant is a project to explore how two WebXR enthusiasts, Rohith and Sylwester, can collaborate and build their own experience.

## Setup and Run Instructions

### Prerequisites

- Python 3.x
- pip (Python package installer)

### Setting Up the Project

#### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/nigel-assistant.git
cd nigel-assistant
```

#### 2. Create and Activate Virtual Environment

##### macOS and Ubuntu

```bash
python3 -m venv venv
source venv/bin/activate
```

##### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### 3. Install Flask

```bash
pip install Flask
```

#### 4. Create the `app.py` file

```python
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
```

#### 5. Create the `templates` directory and `index.html` file

Create a directory named `templates` in the same location as your `app.py` file, and inside this directory, create a file named `index.html` with the following content:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nigel Assistant</title>
</head>
<body>
    <h1>Welcome to Nigel Assistant</h1>
    <p>This is a battleground where Rohith and Sylwester will explore how two WebXR enthusiasts can collaborate and build their own experience.</p>
</body>
</html>
```

### Directory Structure

Ensure your directory structure looks like this:

```
nigel-assistant/
│
├── app.py
├── venv/
└── templates/
    └── index.html
```

### Running the Application

Navigate to your project directory in the terminal and run the Flask application:

```bash
python app.py
```

Visit `http://127.0.0.1:5000/` in your browser to see the template displayed.