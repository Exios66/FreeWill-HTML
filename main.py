from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Any
from db_utils import db_manager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Pydantic models for request validation
class SurveyData(BaseModel):
    responses: Dict[str, int]
    scores: Dict[str, float]
    metadata: Dict[str, Any]

@app.post("/api/survey/submit")
async def submit_survey(data: SurveyData):
    """Submit a new survey response."""
    try:
        response_id = db_manager.insert_response(data.dict())
        return {
            "status": "success",
            "message": "Survey response recorded",
            "response_id": response_id
        }
    except Exception as e:
        logger.error(f"Error submitting survey: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/survey/stats")
async def get_survey_stats():
    """Get enhanced statistics about survey responses."""
    try:
        return db_manager.get_statistics()
    except Exception as e:
        logger.error(f"Error retrieving statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/survey/response/{response_id}")
async def get_survey_response(response_id: int):
    """Retrieve a specific survey response."""
    try:
        response = db_manager.get_response(response_id)
        if not response:
            raise HTTPException(status_code=404, detail="Response not found")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving response {response_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/survey/backup")
async def create_backup():
    """Create a backup of the database and CSV."""
    try:
        backup_path = db_manager.backup_database()
        return {
            "status": "success",
            "message": "Backup created successfully",
            "backup_path": str(backup_path)
        }
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 