from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Any
import pandas as pd
import sqlite3
import json
from datetime import datetime
import os
from pathlib import Path

# Create data directory if it doesn't exist
Path("data").mkdir(exist_ok=True)

app = FastAPI(title="Free Will Survey API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/", StaticFiles(directory=".", html=True), name="static")

# Database configuration
DB_PATH = "data/survey_responses.db"
CSV_PATH = "data/survey_responses.csv"

# Create tables if they don't exist
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create responses table
    c.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            responses TEXT,
            scores TEXT,
            metadata TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

# Pydantic models for request validation
class SurveyData(BaseModel):
    responses: Dict[str, int]
    scores: Dict[str, float]
    metadata: Dict[str, Any]

@app.post("/api/survey/submit")
async def submit_survey(data: SurveyData):
    try:
        # Connect to database
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Insert data
        c.execute('''
            INSERT INTO responses (timestamp, responses, scores, metadata)
            VALUES (?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            json.dumps(data.responses),
            json.dumps(data.scores),
            json.dumps(data.metadata)
        ))
        
        conn.commit()
        
        # Update CSV file
        update_csv()
        
        return {"status": "success", "message": "Survey response recorded"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        conn.close()

def update_csv():
    """Update the CSV file with all responses for easy analysis"""
    conn = sqlite3.connect(DB_PATH)
    
    # Get all responses
    query = "SELECT * FROM responses"
    df = pd.read_sql_query(query, conn)
    
    # Parse JSON columns
    df['responses'] = df['responses'].apply(json.loads)
    df['scores'] = df['scores'].apply(json.loads)
    df['metadata'] = df['metadata'].apply(json.loads)
    
    # Normalize the JSON columns
    responses_df = pd.json_normalize(df['responses'].tolist())
    scores_df = pd.json_normalize(df['scores'].tolist())
    metadata_df = pd.json_normalize(df['metadata'].tolist())
    
    # Combine all dataframes
    final_df = pd.concat([
        df[['id', 'timestamp']],
        responses_df.add_prefix('response_'),
        scores_df.add_prefix('score_'),
        metadata_df.add_prefix('metadata_')
    ], axis=1)
    
    # Save to CSV
    final_df.to_csv(CSV_PATH, index=False)
    
    conn.close()

@app.get("/api/survey/stats")
async def get_survey_stats():
    """Get basic statistics about the survey responses"""
    try:
        if not os.path.exists(CSV_PATH):
            return {
                "total_responses": 0,
                "average_scores": {},
                "latest_response": None
            }
        
        df = pd.read_csv(CSV_PATH)
        
        score_columns = [col for col in df.columns if col.startswith('score_')]
        average_scores = df[score_columns].mean().to_dict()
        
        return {
            "total_responses": len(df),
            "average_scores": average_scores,
            "latest_response": df['timestamp'].max()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 