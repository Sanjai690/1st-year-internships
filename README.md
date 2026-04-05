# Career Navigator Assistant

A chatbot that suggests career paths based on your skills and interests.

## Installation

1. Install Flask:
   ```bash
   pip install flask
   ```

2. Run the app:
   ```bash
   python app.py
   ```

3. Open your browser to `http://localhost:5000`

## How to Use

Enter your skills or interests (e.g., "coding", "data", "design") and the chatbot will suggest matching careers.

## Project Files

- `app.py` - Flask backend
- `careers.csv` - Skill-to-career mappings
- `templates/index.html` - Web interface

## Add New Skills

Edit `careers.csv` and add rows like:
```csv
skill,career
your_skill,Career Name
```

## Features

- Matches skills to careers
- Recognizes greetings and exit commands
- Real-time recommendations
- Clean, modern interface
