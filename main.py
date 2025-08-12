import logging
from contextlib import asynccontextmanager
from typing import Optional
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import ccxt
import onnxruntime as rt

# --- Constants and Configuration ---
BASE_DIR = Path(__file__).resolve().parent
ETH_MODEL_PATH = BASE_DIR / "trained_models" / "model_eth.onnx"

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- ML Model Storage ---
# This dictionary will hold the models loaded at startup.
ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Asynchronous context manager to handle application startup and shutdown events.
    Loads the ONNX machine learning model into memory.
    """
    logging.info("Application startup: Loading ONNX ML models...")
    try:
        # Use ONNX Runtime to load the model
        sess = rt.InferenceSession(str(ETH_MODEL_PATH))
        ml_models["eth_model"] = sess
        logging.info("ONNX ETH model loaded successfully.")
    except Exception as e:
        logging.critical(f"Failed to load ONNX ETH model on startup. API will not be able to make predictions. Error: {e}")
        ml_models["eth_model"] = None
    
    yield
    
    # --- Cleanup on shutdown ---
    logging.info("Application shutdown: Clearing ML models...")
    ml_models.clear()

# --- FastAPI App Initialization ---
app = FastAPI(lifespan=lifespan)

# --- CORS Configuration ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Data Models ---
class PredictionResponse(BaseModel):
    prediction: str
    tokenToBuy: Optional[str] = None
    value: Optional[float] = None

# --- Data Fetching and Prediction Logic ---
def get_data_coinbase(ticker: str) -> Optional[np.ndarray]:
    """
    Fetches and prepares the last 5 days of OHLCV data for a given ticker from Coinbase
    using only standard Python libraries and numpy. Returns a numpy array ready for the model.
    """
    exchange = ccxt.coinbase()
    symbol = f"{ticker}/USD"
    timeframe = "1d"
    limit = 5  # Fetch 5 days to have enough data for 3 lags

    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        
        if not ohlcv or len(ohlcv) < 4:
            logging.warning(f"Not enough data from Coinbase for {ticker} (need at least 4 days, got {len(ohlcv)})")
            return None

        # Data is [timestamp, open, high, low, close, volume]
        # We only need the 'close' price (index 4). Data is ordered oldest to newest.
        close_prices = [candle[4] for candle in ohlcv]

        # Calculate percentage change
        pct_changes = []
        for i in range(1, len(close_prices)):
            change = (close_prices[i] - close_prices[i-1]) / close_prices[i-1]
            pct_changes.append(change)

        if len(pct_changes) < 3:
            logging.warning(f"Not enough percentage changes to create lags (need 3, got {len(pct_changes)})")
            return None

        # The model expects features [lag_1, lag_2, lag_3].
        # lag_1 is the most recent change (yesterday's), which is pct_changes[-1].
        features = [pct_changes[-1], pct_changes[-2], pct_changes[-3]]
        
        # Return as a numpy array, reshaped for the model (1 sample, 3 features)
        return np.array(features, dtype=np.float32).reshape(1, -1)
        
    except Exception as e:
        logging.error(f"Error fetching data for {ticker} from Coinbase: {e}", exc_info=True)
        raise

def get_prediction_values() -> dict:
    """
    Orchestrates the data fetching and prediction process using the ONNX model.
    """
    onnx_session = ml_models.get("eth_model")
    if not onnx_session:
        logging.error("ONNX ETH model is not loaded. Cannot make a prediction.")
        raise ValueError("Model not available")

    # get_data_coinbase now returns a numpy array or None
    input_data = get_data_coinbase('ETH')
    
    if input_data is None or input_data.size == 0:
        logging.warning("Could not retrieve valid data for ETH. Aborting prediction.")
        raise ValueError("Invalid or empty data for ETH")

    try:
        # The data is already a numpy array of the correct type and shape
        input_name = onnx_session.get_inputs()[0].name
        prediction_result = onnx_session.run(None, {input_name: input_data})
        
        eth_pred = float(prediction_result[0][0])
        trend = 'positive' if eth_pred >= 0 else 'negative'
        
        return {"trend": trend, "value": eth_pred}
        
    except Exception as e:
        logging.error(f"Error during ONNX model prediction: {e}", exc_info=True)
        raise

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
        logging.error(f"An error occurred in the prediction endpoint: {e}", exc_info=True)
        # Return the default negative response as per requirements
        return {"prediction": "error", "tokenToBuy": None, "value": None}

@app.get("/")
def read_root():
    """
    Root endpoint to check if the API is running.
    """
    return {"status": "Prediction API is running"}

