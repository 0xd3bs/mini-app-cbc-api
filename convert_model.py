import logging
import re
from pathlib import Path
from xgboost import XGBRegressor
import onnxmltools
from onnxmltools.convert.common.data_types import FloatTensorType

# --- Configuration ---
BASE_DIR = Path(__file__).resolve().parent
ETH_MODEL_PATH_JSON = BASE_DIR / "trained_models" / "model_eth.json"
ETH_MODEL_PATH_ONNX = BASE_DIR / "trained_models" / "model_eth.onnx"
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def sanitize_feature_names(model):
    """
    Sanitizes the feature names of an XGBoost model to be compliant with ONNX conversion.
    Replaces custom names with the standard 'f0', 'f1', 'f2', etc.
    """
    if hasattr(model, 'get_booster'):
        booster = model.get_booster()
        if hasattr(booster, 'feature_names') and booster.feature_names is not None:
            logging.info(f"Original feature names: {booster.feature_names}")
            # Create a mapping from old names to new 'f#' names
            sanitized_names = [f'f{i}' for i in range(len(booster.feature_names))]
            # Apply the new names
            booster.feature_names = sanitized_names
            logging.info(f"Sanitized feature names: {booster.feature_names}")
    return model

def convert_model_to_onnx():
    """
    Loads the XGBoost model, sanitizes its feature names, converts it to ONNX, and saves it.
    """
    logging.info("Starting model conversion to ONNX using onnxmltools...")

    # 1. Load the existing XGBoost model
    try:
        model = XGBRegressor()
        model.load_model(ETH_MODEL_PATH_JSON)
        logging.info("Successfully loaded XGBoost model from JSON.")
    except Exception as e:
        logging.critical(f"Failed to load XGBoost model. Aborting conversion. Error: {e}")
        return

    # 2. Sanitize feature names
    model = sanitize_feature_names(model)

    # 3. Define the input signature for the ONNX model
    n_features = 3 # f0, f1, f2 (previously return_lag_1, etc.)
    initial_type = [('float_input', FloatTensorType([None, n_features]))]
    logging.info(f"Defined ONNX input signature with {n_features} features.")

    # 4. Convert the model to ONNX format
    try:
        onnx_model = onnxmltools.convert_xgboost(model, initial_types=initial_type, target_opset=12)
        logging.info("Model successfully converted to ONNX format.")
    except Exception as e:
        logging.critical(f"Failed during onnxmltools conversion. Error: {e}", exc_info=True)
        return

    # 5. Save the ONNX model to a file
    try:
        with open(ETH_MODEL_PATH_ONNX, "wb") as f:
            f.write(onnx_model.SerializeToString())
        logging.info(f"ONNX model saved successfully to: {ETH_MODEL_PATH_ONNX}")
    except Exception as e:
        logging.critical(f"Failed to save the ONNX model file. Error: {e}")

if __name__ == "__main__":
    convert_model_to_onnx()
