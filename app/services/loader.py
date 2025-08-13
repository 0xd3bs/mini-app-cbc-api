import onnxruntime as rt
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

ml_models = {}

def load_model():
    """
    Loads the ONNX machine learning model into memory.
    """
    logger.info("Application startup: Loading ONNX ML models...")
    try:
        # Use ONNX Runtime to load the model
        sess = rt.InferenceSession(settings.eth_model_path)
        ml_models["eth_model"] = sess
        logger.info("ONNX ETH model loaded successfully.")
    except Exception as e:
        logger.critical(f"Failed to load ONNX ETH model on startup. API will not be able to make predictions. Error: {e}")
        ml_models["eth_model"] = None

def get_model():
    """
    Returns the loaded ONNX model.
    """
    return ml_models.get("eth_model")
