import logging
from contextlib import asynccontextmanager
from typing import Optional
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from xgboost import XGBRegressor
import ccxt

# --- Constants and Configuration ---
BASE_DIR = Path(__file__).resolve().parent
ETH_MODEL_PATH = BASE_DIR / "trained_models" / "model_eth.json"

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- ML Model Storage ---
# This dictionary will hold the models loaded at startup.
ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Asynchronous context manager to handle application startup and shutdown events.
    Loads the machine learning model into memory.
    """
    logging.info("Application startup: Loading ML models...")
    try:
        model = XGBRegressor()
        model.load_model(ETH_MODEL_PATH)
        ml_models["eth_model"] = model
        logging.info("ETH model loaded successfully.")
    except Exception as e:
        logging.critical(f"Failed to load ETH model on startup. API will not be able to make predictions. Error: {e}")
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

# --- Data Fetching and Prediction Logic ---
def get_data_coinbase(ticker: str) -> pd.DataFrame:
    """
    Fetches and prepares the last 4 days of OHLCV data for a given ticker from Coinbase.
    """
    exchange = ccxt.coinbase()
    symbol = f"{ticker}/USD"
    timeframe = "1d"
    lags = [1, 2, 3]
    end_date = pd.Timestamp.utcnow().normalize()
    start_date = end_date - pd.Timedelta(days=4)
    
    try:
        since = exchange.parse8601(f'{start_date.strftime("%Y-%m-%d")}T00:00:00Z')
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since)
        
        if not ohlcv:
            logging.warning(f"No data returned from Coinbase for {ticker}")
            return pd.DataFrame()

        df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        df.set_index("timestamp", inplace=True)
        df = df.loc[start_date:end_date]
        
        if df.empty:
            logging.warning(f"Data for {ticker} is empty after date filtering.")
            return pd.DataFrame()

        df["close_pct_change"] = df["close"].pct_change()
        for lag in lags:
            df[f"return_lag_{lag}"] = df["close_pct_change"].shift(lag)
        
        # Return only the last row with features needed for prediction
        return df[[col for col in df.columns if "lag" in col]].tail(1)
        
    except Exception as e:
        logging.error(f"Error fetching data for {ticker} from Coinbase: {e}", exc_info=True)
        # Re-raise the exception to be caught by the endpoint's central error handler
        raise

def get_prediction_values() -> dict:
    """
    Orchestrates the data fetching and prediction process.
    """
    model = ml_models.get("eth_model")
    if not model:
        logging.error("ETH model is not loaded. Cannot make a prediction.")
        raise ValueError("Model not available")

    datos_eth = get_data_coinbase('ETH')
    
    if datos_eth.empty or datos_eth.dropna().empty:
        logging.warning("Could not retrieve valid data for ETH. Aborting prediction.")
        raise ValueError("Invalid or empty data for ETH")

    try:
        eth_pred = float(model.predict(datos_eth.dropna()))
        trend = 'positive' if eth_pred >= 0 else 'negative'
        
        return {"trend": trend, "value": eth_pred}
        
    except Exception as e:
        logging.error(f"Error during model prediction: {e}", exc_info=True)
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
            return {"prediction": "positive", "tokenToBuy": "ETH"}
        else:
            return {"prediction": "negative", "tokenToBuy": None}

    except Exception as e:
        # Centralized error logging for any failure in the prediction pipeline
        logging.error(f"An error occurred in the prediction endpoint: {e}", exc_info=True)
        # Return the default negative response as per requirements
        return {"prediction": "negative", "tokenToBuy": None}

@app.get("/")
def read_root():
    """
    Root endpoint to check if the API is running.
    """
    return {"status": "Prediction API is running"}

