import random
import time
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Create a FastAPI app instance
app = FastAPI()

# --- CORS Configuration ---
# Define the list of origins that are allowed to make requests to this API.
# Using "*" allows all origins, which is useful for public APIs.
# For better security, you might want to restrict this to your specific frontend domain
# e.g., origins = ["https://your-app-domain.com"]
origins = ["*"]

# Add the CORS middleware to the application.
# This will attach the necessary CORS headers to all responses.
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow specific origins
    allow_credentials=True, # Allow cookies to be included in requests
    allow_methods=["*"],    # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],    # Allow all headers
)

# --- Pydantic Data Models ---
# Define the structure of the response body.
# This ensures the API returns data in a consistent format.
class PredictionResponse(BaseModel):
    prediction: str
    tokenToBuy: Optional[str] = None

# --- API Endpoints ---
@app.post("/prediction", response_model=PredictionResponse)
async def get_prediction():
    """
    Simulates a prediction process and returns a structured response.
    This endpoint mimics the behavior of the original Next.js mock API.
    """
    # Simulate a network delay to feel more realistic
    time.sleep(1.5)

    # Simulate a random prediction result
    outcomes = [
        {"prediction": "positive", "tokenToBuy": "ETH"},
        {"prediction": "negative", "tokenToBuy": None},
    ]
    random_outcome = random.choice(outcomes)

    return random_outcome

@app.get("/")
def read_root():
    """
    Root endpoint to check if the API is running.
    """
    return {"status": "Prediction API is running"}

