Adaptive Multi-Agent Data Science Copilot

An end-to-end automated machine learning platform that transforms uploaded datasets into complete AI-powered data science workflows. The platform automatically profiles data, detects machine learning tasks, builds preprocessing pipelines, trains and optimizes models, evaluates performance, generates explainability insights, tracks experiments, and creates executive-level AI reports.

Built as an enterprise-grade AutoML copilot for industrial and academic use cases, the system emphasizes scalability, robustness, automation, explainability, and intelligent AI-agent collaboration. 

Overview

Modern machine learning workflows often require extensive manual effort for:

* Understanding dataset quality
* Detecting the appropriate ML task
* Designing preprocessing pipelines
* Selecting suitable models
* Hyperparameter optimization
* Benchmarking algorithms
* Explaining predictions
* Generating reports

This platform automates the complete lifecycle using a collaborative multi-agent AI architecture combined with a traditional ML execution engine.

AI agents operate only on dataset metadata for privacy-aware reasoning, while the backend ML engine processes actual data securely for training and evaluation. 

Core Features

* Automated dataset upload and validation
* Intelligent metadata extraction using pandas and NumPy
* Multi-agent orchestration using CrewAI and Gemini
* Automatic detection of:

  * Classification
  * Regression
  * Clustering
  * Forecasting tasks
* Dynamic preprocessing pipelines using scikit-learn
* Model training with:

  * scikit-learn
  * XGBoost
  * statsmodels
* Hyperparameter tuning using Optuna
* Benchmarking with task-specific evaluation metrics
* SHAP-based explainability
* AI-generated executive reports
* Real-time workflow monitoring through WebSockets
* Experiment tracking using MLflow
* Workflow memory using ChromaDB
* Downloadable trained models in `.pkl` format
* Docker-based deployment support

System Workflow

1. User uploads a dataset through the dashboard
2. Backend creates a unique job session
3. Data profiler extracts metadata and statistics
4. AI agents analyze dataset structure and quality
5. Task detection identifies the ML problem type
6. Workflow planner creates preprocessing strategies
7. Model strategist selects suitable algorithms
8. ML engine preprocesses and trains models
9. Optuna performs hyperparameter optimization
10. Evaluation agent benchmarks performance
11. SHAP generates explainability insights
12. Report agent creates executive summaries
13. MLflow logs experiments and metrics
14. ChromaDB stores workflow memory
15. Best-performing model is exported for download

AI Agent Architecture

Data Agent
Analyzes dataset quality, missing values, imbalance, and metadata summaries.

Task Agent
Automatically detects classification, regression, clustering, or forecasting tasks.

Workflow Agent
Plans preprocessing steps and execution flow.

Model Strategist Agent
Chooses suitable ML algorithms based on dataset characteristics.

Optimization Agent
Interprets Optuna tuning results and optimization performance.

Evaluation Agent
Explains model benchmarking and validation results.

Explainability Agent
Converts SHAP outputs into understandable insights.

Report Agent
Generates final AI-assisted executive reports.

Technology Stack

Frontend

* Next.js 14
* React 18
* Tailwind CSS
* Framer Motion
* Recharts

Backend

* FastAPI
* Asyncio
* WebSockets

AI Layer

* CrewAI
* Gemini
* LiteLLM

Machine Learning

* scikit-learn
* XGBoost
* statsmodels

Optimization

* Optuna

Explainability

* SHAP

Tracking and Memory

* MLflow
* ChromaDB

Deployment

* Docker Compose

Project Structure

```text
backend/
├── agents/
├── memory/
├── ml/
├── routers/
├── tracking/
├── config.py
├── main.py
├── pipeline_executor.py
├── requirements.txt
└── Dockerfile

frontend/
├── app/
├── components/
├── package.json
└── Dockerfile

data/
models/
deliverables/
docker-compose.yml
.env
README.md
```

Environment Configuration

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
MLFLOW_TRACKING_URI=http://localhost:5000
CHROMA_HOST=localhost
CHROMA_PORT=8000
ALLOWED_ORIGINS=http://localhost:3000
```

Docker Deployment

Start all services:

```bash
docker-compose up --build
```

Stop services:

```bash
docker-compose down
```

Remove volumes:

```bash
docker-compose down -v
```

Local Development Setup

Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

macOS/Linux activation:

```bash
source .venv/bin/activate
```

Frontend

```bash
cd frontend
npm install
npm run dev
```

MLflow

```bash
mlflow server --host 0.0.0.0 --port 5000
```

Application URLs

Frontend Dashboard
`http://localhost:3000`

Backend API
`http://localhost:8000`

Backend Health Endpoint
`http://localhost:8000/health`

MLflow Dashboard
`http://localhost:5000`

ChromaDB Service
`http://localhost:8001`

API Endpoints

Health Check

```http
GET /health
```

Upload Dataset

```http
POST /api/upload
```

Get Job Status

```http
GET /api/status/{job_id}
```

Get Results

```http
GET /api/results/{job_id}
```

Download Best Model

```http
GET /api/download/{job_id}
```

WebSocket Updates

```text
ws://localhost:8000/ws/{job_id}
```

Supported Dataset Types

* CSV
* Excel
* JSON
* Parquet

Supported Features

* Numerical features
* Categorical features
* Datetime features
* Auto-detected target columns
* Missing value handling
* Class imbalance detection
* Time-series dataset support

Supported Models

Classification

* Logistic Regression
* Random Forest
* XGBoost

Regression

* Linear Regression
* Random Forest Regressor
* XGBoost Regressor

Clustering

* KMeans
* DBSCAN

Forecasting

* ARIMA
* Exponential Smoothing

Evaluation Metrics

Classification

* Accuracy
* Balanced Accuracy
* Precision
* Recall
* F1 Score
* MCC
* ROC-AUC
* Confusion Matrix

Regression

* RMSE
* MAE
* R² Score

Clustering

* Silhouette Score
* Cluster Analysis

Forecasting

* AIC
* BIC
* Forecast Outputs

Expected Outputs

The pipeline automatically generates:

* Dataset summary
* Metadata analysis
* Data quality insights
* ML task detection
* Preprocessing workflow
* Model benchmarking
* Hyperparameter optimization results
* Explainability reports
* AI-generated executive reports
* Downloadable trained models

Experiment Tracking and Workflow Memory

MLflow stores:

* Metrics
* Experiments
* Parameters
* Model versions

ChromaDB stores:

* Workflow memory
* Agent reasoning summaries
* Historical execution context

Troubleshooting

Docker Issues

```bash
docker-compose up --build
```

Frontend Cannot Reach Backend

Verify:

```text
http://localhost:8000
```

Gemini API Errors

Ensure `.env` contains:

```env
GEMINI_API_KEY=your_api_key
```

Unsupported File Types

Accepted extensions:

```text
.csv
.xlsx
.json
.parquet
```

Minority Class Warning

If a classification dataset contains extremely small minority classes, train/test validation may become unreliable. Increase samples for minority classes or merge rare categories for better results.

Evaluation Criteria Coverage

Innovation and Originality
Uses collaborative multi-agent AI orchestration with metadata-based reasoning.

Technical Implementation
Integrates FastAPI, Next.js, CrewAI, Gemini, Optuna, SHAP, MLflow, and ChromaDB into a unified intelligent AutoML ecosystem.

Industrial Relevance
Supports automated, explainable, reproducible machine learning workflows with downloadable models and enterprise-ready reporting.

Scalability and Robustness
Features modular services, Docker deployment, asynchronous execution, WebSocket monitoring, workflow memory, and experiment tracking.



