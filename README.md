# Adaptive Multi-Agent Data Science Copilot

An end-to-end automated machine learning platform that turns an uploaded dataset into a complete data science workflow. The system profiles the data, detects the machine learning task, plans preprocessing, trains and optimizes models, evaluates performance, explains predictions, tracks experiments, and generates an AI-assisted final report.

This project was built as an enterprise-style AutoML copilot for the ABB assignment, with focus on innovation, technical implementation, industrial relevance, scalability, and robustness.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Workflow](#workflow)
- [AI Agents](#ai-agents)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Run with Docker](#run-with-docker)
- [Run Locally Without Docker](#run-locally-without-docker)
- [Application URLs](#application-urls)
- [API Endpoints](#api-endpoints)
- [Supported Inputs](#supported-inputs)
- [Expected Outputs](#expected-outputs)
- [Experiment Tracking and Memory](#experiment-tracking-and-memory)
- [Troubleshooting](#troubleshooting)
- [Evaluation Criteria Coverage](#evaluation-criteria-coverage)

## Overview

Modern data science workflows usually require manual effort for:

- Understanding dataset quality
- Detecting the correct ML task
- Choosing preprocessing steps
- Selecting suitable algorithms
- Tuning model parameters
- Comparing models
- Explaining predictions
- Preparing reports

This project automates that lifecycle using a multi-agent AI system and a traditional machine learning engine. The LLM-based agents reason over dataset metadata, while the ML engine performs computation on the actual data.

The important privacy design is that AI agents receive metadata summaries instead of raw user data. Raw data is used only inside the backend ML pipeline for preprocessing and model training.

## Key Features

- Automated dataset upload and processing
- Metadata extraction using pandas and NumPy
- Multi-agent workflow orchestration using CrewAI and Gemini
- Automatic task detection for classification, regression, clustering, and forecasting
- Dynamic preprocessing using scikit-learn
- Model training using scikit-learn, XGBoost, and statsmodels
- Hyperparameter tuning using Optuna
- Model benchmarking with task-specific metrics
- SHAP-based explainability
- AI-generated executive report
- Real-time workflow updates through WebSockets
- Experiment tracking with MLflow
- Workflow memory using ChromaDB
- Downloadable best model in `.pkl` format
- Docker Compose based deployment

## System Architecture
given as png 

## Workflow

1. User uploads a dataset from the dashboard.
2. Backend stores the file and creates a unique job ID.
3. Data profiler extracts dataset metadata.
4. Data Agent analyzes data quality.
5. Task Agent detects the ML task type.
6. Workflow Agent creates the preprocessing plan.
7. Model Strategist selects suitable algorithms.
8. ML engine preprocesses features and target values.
9. Models are trained according to the detected task.
10. Optuna tunes hyperparameters where applicable.
11. Evaluation Agent benchmarks model performance.
12. SHAP explains important features for supported models.
13. Report Agent generates the final AI report.
14. MLflow logs experiment results.
15. ChromaDB stores workflow memory.
16. The best model is saved for download.

## AI Agents

| Agent | Responsibility |
| --- | --- |
| Data Agent | Reviews dataset metadata and summarizes data quality |
| Task Agent | Detects classification, regression, clustering, or forecasting |
| Workflow Agent | Plans preprocessing and workflow steps |
| Model Strategist Agent | Selects suitable algorithms |
| Optimization Agent | Interprets Optuna tuning results |
| Evaluation Agent | Explains benchmark results |
| Explainability Agent | Converts SHAP output into understandable insights |
| Report Agent | Generates the final executive AI report |

## Technology Stack

| Layer | Tools |
| --- | --- |
| Frontend | Next.js 14, React 18, Tailwind CSS, Framer Motion, Recharts |
| Backend | FastAPI, Asyncio, WebSockets |
| AI Agents | CrewAI, Gemini, LiteLLM |
| Data Processing | pandas, NumPy |
| ML Training | scikit-learn, XGBoost, statsmodels |
| Optimization | Optuna |
| Explainability | SHAP |
| Tracking | MLflow |
| Memory | ChromaDB |
| Deployment | Docker Compose |

## Project Structure

```text
.
|-- backend/
|   |-- agents/              # CrewAI/Gemini agent definitions
|   |-- memory/              # ChromaDB workflow memory
|   |-- ml/                  # Profiling, preprocessing, training, tuning, evaluation, SHAP
|   |-- routers/             # FastAPI upload, status, results, websocket routes
|   |-- tracking/            # MLflow logging
|   |-- config.py            # Environment settings
|   |-- main.py              # FastAPI app entrypoint
|   |-- pipeline_executor.py # Full async AutoML orchestration
|   |-- requirements.txt
|   `-- Dockerfile
|-- frontend/
|   |-- app/                 # Next.js app routes and layout
|   |-- components/          # Dashboard, charts, upload panel, logs
|   |-- package.json
|   `-- Dockerfile
|-- data/                    # Uploaded datasets
|-- models/                  # Exported best models
|-- deliverables/            # Submission PDF/DOCX files
|-- docker-compose.yml
|-- .env
`-- README.md
```

## Prerequisites

For Docker setup:

- Docker Desktop
- A valid Gemini API key

For local setup:

- Python 3.11 recommended
- Node.js 18 or newer
- npm
- A valid Gemini API key
- Optional: MLflow and ChromaDB services if running without Docker

## Environment Setup

Create or update the `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
MLFLOW_TRACKING_URI=http://localhost:5000
CHROMA_HOST=localhost
CHROMA_PORT=8000
ALLOWED_ORIGINS=http://localhost:3000
```

Inside Docker, `docker-compose.yml` overrides the backend service values so the backend can reach MLflow and ChromaDB through container names:

```env
MLFLOW_TRACKING_URI=http://mlflow:5000
CHROMA_HOST=chromadb
CHROMA_PORT=8000
```

## Run with Docker

From the project root:

```bash
docker-compose up --build
```

To stop the platform:

```bash
docker-compose down
```

To stop and remove persisted MLflow/Chroma volumes:

```bash
docker-compose down -v
```

## Run Locally Without Docker

Docker is the recommended method because it starts the backend, frontend, MLflow, and ChromaDB together. If you want to run services manually, use the steps below.

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

For macOS/Linux activation:

```bash
source .venv/bin/activate
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### MLflow

```bash
mlflow server --host 0.0.0.0 --port 5000
```

### ChromaDB

If running locally, start ChromaDB separately or use the Docker service from `docker-compose.yml`.

## Application URLs

| Service | URL |
| --- | --- |
| Frontend Dashboard | `http://localhost:3000` |
| Backend API | `http://localhost:8000` |
| Backend Health Check | `http://localhost:8000/health` |
| MLflow UI | `http://localhost:5000` |
| ChromaDB | `http://localhost:8001` when exposed through Docker |

## API Endpoints

### Health Check

```http
GET /health
```

Response:

```json
{
  "status": "healthy",
  "service": "AutoML Copilot"
}
```

### Upload Dataset

```http
POST /api/upload
```

Form field:

```text
file=<dataset.csv|xlsx|json|parquet>
```

Response:

```json
{
  "job_id": "generated-job-id",
  "message": "Dataset uploaded. Pipeline started.",
  "filename": "dataset.csv"
}
```

### Get Job Status

```http
GET /api/status/{job_id}
```

Returns job state and workflow updates.

### Get Results

```http
GET /api/results/{job_id}
```

Returns final results after the pipeline completes. If the job is still running, the API returns a `202` response.

### Download Best Model

```http
GET /api/download/{job_id}
```

Downloads the best model as a `.pkl` file after successful completion.

### WebSocket Updates

```text
ws://localhost:8000/ws/{job_id}
```

The frontend uses this endpoint to display real-time agent and pipeline status.

## Supported Inputs

| Input Category | Description |
| --- | --- |
| Structured datasets | CSV, Excel, JSON, and Parquet |
| Numerical features | Integer and decimal columns |
| Categorical features | Text, category, boolean, and label-like columns |
| Datetime features | Date, timestamp, month, year, and similar columns |
| Target column | Auto-suggested from common names or fallback column selection |
| Data quality indicators | Missing values, duplicate records, class imbalance |
| Time-series inputs | Datetime-indexed or datetime-like datasets |

Maximum upload size is currently defined in `backend/routers/upload.py`.

## Expected Outputs

The completed pipeline can produce:

- Dataset summary and metadata
- Data quality analysis
- Detected ML task
- Preprocessing workflow
- Model selection summary
- Trained models
- Optuna optimization results
- Benchmark metrics
- Best model name
- SHAP explainability results
- AI-generated report
- Download URL for the best model

## Model Support

| Task | Models |
| --- | --- |
| Classification | Logistic Regression, Random Forest, XGBoost |
| Regression | Linear Regression, Random Forest Regressor, XGBoost Regressor |
| Clustering | KMeans, DBSCAN |
| Forecasting | ARIMA, Exponential Smoothing |

## Metrics

| Task | Metrics |
| --- | --- |
| Classification | Accuracy, balanced accuracy, F1 weighted, precision, recall, MCC, confusion matrix, ROC-AUC where applicable |
| Regression | RMSE, MAE, R2 |
| Clustering | Number of clusters, silhouette score |
| Forecasting | AIC, BIC, forecast values |

## Experiment Tracking and Memory

### MLflow

MLflow stores experiment metadata, model metrics, and optimization results. Open the MLflow UI:

```text
http://localhost:5000
```

### ChromaDB

ChromaDB stores workflow memory so that previous workflow summaries can be reused or referenced later.

When running through Docker, ChromaDB is exposed on:

```text
http://localhost:8001
```

## Troubleshooting

### Docker containers do not start

Check that Docker Desktop is running, then rebuild:

```bash
docker-compose up --build
```

### Frontend cannot reach backend

Make sure the backend is running at:

```text
http://localhost:8000
```

Also verify frontend environment values in `docker-compose.yml`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### Gemini or agent calls fail

Check that `.env` contains:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

If you are using a free Gemini tier, requests may be rate limited. The pipeline already includes short delays between agent calls to reduce rate-limit errors.

### Unsupported file type

Only these extensions are accepted:

```text
.csv, .xlsx, .json, .parquet
```

### Pipeline says task is still running

The results endpoint returns `202` until the background pipeline finishes:

```http
GET /api/results/{job_id}
```

Use the dashboard, WebSocket updates, or status endpoint:

```http
GET /api/status/{job_id}
```

### Minority class warning in classification

For classification datasets, each class should ideally have at least two samples. If a minority class has only one sample, reliable train/test splitting and cross-validation are not possible.

The trainer can still run with a fallback, but the validation metrics should be treated carefully. For stronger results, add more samples for minority classes or merge extremely rare classes.

### MLflow or ChromaDB logging fails

The pipeline treats tracking and workflow memory as best-effort steps. A model can still train and return results even if MLflow or ChromaDB is temporarily unavailable.

## Evaluation Criteria Coverage

| Criteria | How the Project Satisfies It |
| --- | --- |
| Innovation and originality | Uses multi-agent AI orchestration and metadata-only reasoning for automated data science |
| Technical implementation | Combines FastAPI, Next.js, CrewAI, Gemini, scikit-learn, XGBoost, Optuna, SHAP, MLflow, and ChromaDB |
| Industrial relevance | Supports automated, explainable, repeatable ML workflows with downloadable models and reports |
| Scalability and robustness | Modular services, Docker deployment, async backend execution, WebSocket monitoring, experiment tracking, and workflow memory |

## Notes

- Uploaded datasets are stored in `data/`.
- Exported models are stored in `models/`.
- The backend uses background tasks for pipeline execution.
- AI agents reason over metadata; ML components process the actual dataset.
- For best demo results, use datasets with enough rows per class and clear feature/target columns.
