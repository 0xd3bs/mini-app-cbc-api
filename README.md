# Python Mock Prediction API

This is a simple mock API built with Python and FastAPI. It's designed to simulate a prediction endpoint and is ready for deployment on Vercel.

## Features

- Health check endpoint to verify service status.
- Mock prediction endpoint that returns randomized outcomes.
- CORS enabled for all origins, allowing it to be consumed by any frontend application.
- Pre-configured for easy deployment on Vercel.

## Tech Stack

- **Python 3.12+**
- **FastAPI**: For building the API.
- **Uvicorn**: As the ASGI server.
- **uv**: For environment and package management.

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
- **Description**: Simulates a prediction process. It introduces an artificial delay of 1.5 seconds and returns one of two possible outcomes.
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
