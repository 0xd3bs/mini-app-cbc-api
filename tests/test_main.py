import pytest
from fastapi.testclient import TestClient
from app.main import app
from pytest_mock import MockerFixture

# Use a TestClient to make requests to the FastAPI app
client = TestClient(app)

def test_read_root():
    """
    Test the root endpoint to ensure it's running.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "Prediction API is running"}

def test_prediction_positive_trend(mocker: MockerFixture):
    """
    Test the /prediction endpoint with a mocked positive trend.
    """
    # Mock the function that contains the core logic
    mock_result = {"trend": "positive", "value": 0.05}
    mocker.patch('app.main.get_prediction_values', return_value=mock_result)
    
    response = client.post("/prediction")
    
    assert response.status_code == 200
    data = response.json()
    assert data["prediction"] == "positive"
    assert data["tokenToBuy"] == "ETH"
    assert data["value"] == 0.05

def test_prediction_negative_trend(mocker: MockerFixture):
    """
    Test the /prediction endpoint with a mocked negative trend.
    """
    # Mock the function for a negative scenario
    mock_result = {"trend": "negative", "value": -0.02}
    mocker.patch('app.main.get_prediction_values', return_value=mock_result)
    
    response = client.post("/prediction")
    
    assert response.status_code == 200
    data = response.json()
    assert data["prediction"] == "negative"
    assert data["tokenToBuy"] == "ETH"
    assert data["value"] == -0.02

def test_prediction_error_handling(mocker: MockerFixture):
    """
    Test the centralized error handling for the /prediction endpoint.
    """
    # Mock the function to raise an exception
    mocker.patch('app.main.get_prediction_values', side_effect=Exception("Test error"))
    
    response = client.post("/prediction")
    
    assert response.status_code == 200  # The endpoint itself handles the error and returns a 200
    data = response.json()
    assert data["prediction"] == "error"
    assert data["tokenToBuy"] is None
    assert data["value"] is None

