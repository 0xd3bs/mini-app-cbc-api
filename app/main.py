from contextlib import asynccontextmanager
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.models.prediction import PredictionResponse
from app.services.loader import load_model
from app.services.predictor import get_prediction_values
from app.utils.logger import get_logger
from app.config import settings

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Asynchronous context manager to handle application startup and shutdown events.
    Loads the ONNX machine learning model into memory.
    """
    load_model()
    yield
    # --- Cleanup on shutdown ---
    logger.info("Application shutdown: Clearing ML models...")
    

# --- FastAPI App Initialization ---
app = FastAPI(lifespan=lifespan)

# --- Request ID Middleware ---
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    # You can store the request_id in a context variable if you need to access it in other places
    # from contextvars import ContextVar
    # request_id_var = ContextVar('request_id', default=None)
    # request_id_var.set(request_id)
    logger.info(f"Request ID: {request_id} - Path: {request.url.path}")
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

# --- CORS Configuration ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Exception Handler ---
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(status_code=500, content={"error": "Internal Server Error"})


# --- API Endpoints ---
@app.post("/prediction", response_model=PredictionResponse)
async def get_prediction():
    """
    Performs a prediction based on real market data.
    This endpoint has a centralized error handler to ensure it always returns
    a valid response structure, defaulting to a "negative" prediction on any failure.
    """
    try:
        result = get_prediction_values()
        
        if result["trend"] == 'positive':
            return {"prediction": "positive", "tokenToBuy": "ETH", "value": result["value"]}
        else:
            return {"prediction": "negative", "tokenToBuy": "ETH", "value": result["value"]}

    except Exception as e:
        # Centralized error logging for any failure in the prediction pipeline
        logger.error(f"An error occurred in the prediction endpoint: {e}", exc_info=True)
        # Return the default negative response as per requirements
        return {"prediction": "error", "tokenToBuy": None, "value": None}

@app.get("/")
def read_root():
    """
    Root endpoint to check if the API is running.
    """
    return {"status": "Prediction API is running"}
