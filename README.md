# Free Will Synthesis Survey

A web-based survey application for collecting and analyzing responses about free will beliefs, determinism, and related philosophical concepts.

## Features

- Modern, responsive UI with dark/light theme support
- Real-time form validation
- Secure data storage in SQLite database
- Automated CSV export for data analysis
- Basic statistics API endpoint
- Debug mode for development

## Setup

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
python main.py
```

The application will be available at `http://localhost:8000`

## Data Storage

Survey responses are stored in:

- SQLite database: `data/survey_responses.db`
- CSV export: `data/survey_responses.csv`

The CSV file is automatically updated with each new submission for easy data analysis.

## API Endpoints

- `POST /api/survey/submit`: Submit a new survey response
- `GET /api/survey/stats`: Get basic statistics about survey responses

## Development

To enable debug mode:

1. Open index.html
2. Set `const DEBUG = true` at the top of the script
3. Open browser console to see debug messages

## Data Analysis

The survey data is organized into several categories:

- Free Will Beliefs (7 questions)
- Randomness and Unpredictability (6 questions)
- Determinism (2 questions)
- Philosophical Concepts (2 questions)

Each response includes:

- Individual question responses (1-5 scale)
- Calculated category scores
- Metadata (timestamp, user agent, language)

## Security Notes

For production deployment:

1. Configure proper CORS settings in main.py
2. Set up proper authentication
3. Use environment variables for sensitive configurations
4. Implement rate limiting
5. Add input sanitization
