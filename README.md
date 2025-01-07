# FreeWill-HTML Survey Application

A comprehensive web-based survey application for conducting free will belief assessments, built with FastAPI and SQLite.

## Overview

This application provides a modern, responsive web interface for conducting surveys related to free will beliefs. It includes:

- A dynamic HTML-based survey interface
- RESTful API backend for data collection
- Automatic data storage in both SQLite and CSV formats
- Real-time statistics calculation
- Cross-platform compatibility

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Data Storage](#data-storage)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (for version control)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/FreeWill-HTML.git
cd FreeWill-HTML
```

2. Create and activate a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Initialize the database:

```bash
python init_db.py
```

## Project Structure

```
FreeWill-HTML/
├── main.py              # FastAPI application server
├── init_db.py           # Database initialization script
├── index.html           # Main survey interface
├── requirements.txt     # Python dependencies
├── data/               # Data directory (created on init)
│   ├── survey_responses.db  # SQLite database
│   └── survey_responses.csv # CSV export of responses
└── README.md           # This documentation
```

## Configuration

The application uses several configuration settings that can be modified:

- Database location: `data/survey_responses.db`
- CSV export location: `data/survey_responses.csv`
- Server host: `0.0.0.0` (default)
- Server port: `8000` (default)

## Usage

1. Start the server:

```bash
python main.py
```

2. Access the application:

- Web interface: `http://localhost:8000`
- API documentation: `http://localhost:8000/docs`

## API Documentation

### Endpoints

#### POST /api/survey/submit

Submit a new survey response.

Request body:

```json
{
    "responses": {
        "question_id": integer_value,
        ...
    },
    "scores": {
        "category": float_value,
        ...
    },
    "metadata": {
        "key": value,
        ...
    }
}
```

#### GET /api/survey/stats

Retrieve survey statistics.

Response:

```json
{
    "total_responses": integer,
    "average_scores": {
        "category": float,
        ...
    },
    "latest_response": timestamp
}
```

## Data Storage

### Database Schema

The SQLite database (`data/survey_responses.db`) contains the following structure:

```sql
CREATE TABLE responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    responses TEXT NOT NULL,
    scores TEXT NOT NULL,
    metadata TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### CSV Export

The application automatically maintains a CSV export (`data/survey_responses.csv`) with the following columns:

- id
- timestamp
- response_* (question responses)
- score_* (category scores)
- metadata_* (additional information)

## Development

### Adding New Questions

1. Update the survey interface in `index.html`
2. Ensure the question IDs match the expected format in the API
3. Update any scoring calculations as needed

### Modifying Data Collection

1. Update the `SurveyData` model in `main.py`
2. Modify the database schema in `init_db.py`
3. Update the CSV export function in `main.py`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Future Expansion

### Planned Features

- User authentication system
- Advanced analytics dashboard
- Multiple survey templates
- Internationalization support
- Export to additional formats

### Technical Roadmap

1. Implement user authentication
2. Add database migrations
3. Create admin interface
4. Enhance data visualization
5. Add API rate limiting
6. Implement caching

### Integration Possibilities

- LMS (Learning Management Systems)
- Research platforms
- Data analysis tools
- External authentication providers

For more information or support, please open an issue on the GitHub repository.
