from typing import Optional
import numpy as np
import ccxt
from app.utils.logger import get_logger

logger = get_logger(__name__)

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
            logger.warning(f"Not enough data from Coinbase for {ticker} (need at least 4 days, got {len(ohlcv)})")
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
            logger.warning(f"Not enough percentage changes to create lags (need 3, got {len(pct_changes)})")
            return None

        # The model expects features [lag_1, lag_2, lag_3].
        # lag_1 is the most recent change (yesterday's), which is pct_changes[-1].
        features = [pct_changes[-1], pct_changes[-2], pct_changes[-3]]
        
        # Return as a numpy array, reshaped for the model (1 sample, 3 features)
        return np.array(features, dtype=np.float32).reshape(1, -1)
        
    except Exception as e:
        logger.error(f"Error fetching data for {ticker} from Coinbase: {e}", exc_info=True)
        raise
