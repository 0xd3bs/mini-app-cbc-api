# Trend Prediction API

This is a robust and scalable API built with Python and FastAPI, designed to serve trend predictions from pre-trained machine learning models. The application has been refactored into a modular architecture, optimized for container-based deployments on platforms like Google Cloud Run, and includes a comprehensive suite of automated tests.

It currently supports the `eth` model but can be easily extended to support more.

## Features

- **Modular Architecture**: Code is organized by feature (`services`, `models`, `utils`) for better maintainability and scalability.
- **Multi-Model Support**: Capable of loading and serving predictions from multiple models.
- **Configuration via Environment Variables**: Uses `pydantic-settings` for safe and easy configuration.
- **Structured Logging**: Includes a middleware that adds a unique request ID to every log entry for better traceability.
- **Automated Tests**: A full test suite using `pytest` ensures reliability and simplifies future development.
- **Cloud Run Ready**: Includes a `Procfile` configured with `gunicorn` for production-ready deployments.
- **Automatic API Documentation**: Leverages FastAPI to generate interactive API documentation (via Swagger UI and ReDoc).

## Tech Stack

- **Python 3.12+**
- **FastAPI**: For building the API.
- **Gunicorn**: As the production-grade WSGI server.
- **Uvicorn**: As the ASGI worker for Gunicorn.
- **Pydantic**: For data validation and settings management.
- **ONNX Runtime**: For running optimized ML models.
- **Pytest**: For automated testing.

## Getting Started

### Prerequisites

- Python 3.12 or higher.
- A virtual environment tool like `venv` or `uv`.

### Installation

1.  Clone the repository.
2.  Create and activate a virtual environment. For example, using `venv`:
    ```bash
    uv venv
    ```
3.  Install the required dependencies:
    ```bash
    uv pip install -r requirements.txt
    ```

### Environment Cleanup

If you need to reset your local dependencies and start from a clean state, you can completely remove the virtual environment directory:

```bash
rm -rf .venv
```

After running this command, you can follow the installation steps again to recreate the environment.

### Running the Development Server

To run the API locally with auto-reload enabled, use the following command:

```bash
uv run uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`. You can access the interactive documentation at `http://127.0.0.1:8000/docs`.

## Testing

This project uses `pytest` for automated testing. To run the test suite, execute the following command from the root directory:

```bash
uv run python -m pytest
```

This will discover and run all tests located in the `tests/` directory, ensuring that all endpoints and services behave as expected.

## API Endpoints

### 1. Health Check

- **Endpoint**: `GET /`
- **Description**: Returns a status message to confirm that the API is running correctly.
- **Success Response (200 OK)**:
  ```json
  {
    "status": "ok"
  }
  ```

### 2. Get Prediction

- **Endpoint**: `POST /prediction`
- **Description**: Performs a trend prediction using a specified model and input data.
- **Request Body**:
  ```json
  {
    "model_name": "eth",
    "data": [50000.1, 51000.2, 50500.3, 52000.4, 51500.5]
  }
  ```
  - `model_name` (str): The name of the model to use (e.g., `eth`).
  - `data` (list[float]): A list of 5 numerical values for the prediction.

- **Success Response (200 OK)**:
  ```json
  {
    "prediction": 1
  }
  ```
  *(Note: `1` typically represents a positive trend, `0` a negative one)*

- **Error Response (404 Not Found)**:
  ```json
  {
    "detail": "Model 'your_model_name' not found."
  }
  ```

## Deployment

This project is configured for deployment on container-based platforms like Google Cloud Run or Heroku via the included `Procfile`.

The `Procfile` specifies the command to start the production server:
`web: gunicorn -k uvicorn.workers.UvicornWorker --bind :$PORT --workers 1 --threads 8 --timeout 0 app.main:app`

This command runs the application using `gunicorn` with `uvicorn` workers, which is the recommended setup for running FastAPI in production.
