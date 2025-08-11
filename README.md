# Cryptocurrency Trend Prediction API

This is a simple API built with Python and FastAPI that predicts the price trend for Ethereum (ETH). It fetches real-time market data from Coinbase, processes it, and uses a pre-trained XGBoost model to generate a prediction. The project is configured for easy deployment on Vercel.

## Features

- **Real-time Predictions**: Provides trend predictions for ETH based on live market data.
- **XGBoost Model**: Utilizes a pre-trained XGBoost model for forecasting.
- **Coinbase Integration**: Fetches the latest cryptocurrency data directly from the Coinbase exchange via the `ccxt` library.
- **Health Check**: Includes a root endpoint to verify the service status.
- **CORS Enabled**: Configured with CORS middleware to allow requests from any origin.
- **Vercel Ready**: Pre-configured for seamless deployment to Vercel.

## Tech Stack

- **Python 3.12+**
- **FastAPI**: For building the API.
- **Uvicorn**: As the ASGI server.
- **uv**: For environment and package management.
- **Pandas**: For data manipulation.
- **XGBoost**: For the prediction model.
- **CCXT**: For fetching cryptocurrency data from exchanges.

## Getting Started

### Prerequisites

- Python 3.12 or higher.
- `uv` installed on your system.

### Installation

1.  Clone the repository.
2.  Create and sync the virtual environment to install the dependencies:
    ```bash
    uv sync
    ```

### Running the Development Server

To run the API locally with auto-reload enabled, use the following command:

```bash
uv run uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## API Endpoints

### 1. Health Check

- **Endpoint**: `GET /`
- **Description**: Returns a status message to confirm that the API is running correctly.
- **Success Response (200 OK)**:
  ```json
  {
    "status": "Prediction API is running"
  }
  ```

### 2. Get Prediction

- **Endpoint**: `POST /prediction`
- **Description**: Performs a prediction based on the latest ETH/USD market data from Coinbase. It uses a pre-trained XGBoost model to forecast the trend.
- **Success Response (200 OK)**:

  A positive prediction:
  ```json
  {
    "prediction": "positive",
    "tokenToBuy": "ETH"
  }
  ```

  Or a negative prediction:
  ```json
  {
    "prediction": "negative",
    "tokenToBuy": null
  }
  ```

## Deployment

This project includes a `vercel.json` file, making it ready for seamless deployment to Vercel. Simply import the Git repository into your Vercel account, and it will be deployed automatically.