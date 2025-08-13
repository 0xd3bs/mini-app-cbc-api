from app.services.loader import get_model
from app.services.data_fetcher import get_data_coinbase
from app.utils.logger import get_logger

logger = get_logger(__name__)

def get_prediction_values() -> dict:
    """
    Orchestrates the data fetching and prediction process using the ONNX model.
    """
    onnx_session = get_model()
    if not onnx_session:
        logger.error("ONNX ETH model is not loaded. Cannot make a prediction.")
        raise ValueError("Model not available")

    # get_data_coinbase now returns a numpy array or None
    input_data = get_data_coinbase('ETH')
    
    if input_data is None or input_data.size == 0:
        logger.warning("Could not retrieve valid data for ETH. Aborting prediction.")
        raise ValueError("Invalid or empty data for ETH")

    try:
        # The data is already a numpy array of the correct type and shape
        input_name = onnx_session.get_inputs()[0].name
        prediction_result = onnx_session.run(None, {input_name: input_data})
        
        eth_pred = float(prediction_result[0][0])
        trend = 'positive' if eth_pred >= 0 else 'negative'
        
        return {"trend": trend, "value": eth_pred}
        
    except Exception as e:
        logger.error(f"Error during ONNX model prediction: {e}", exc_info=True)
        raise
