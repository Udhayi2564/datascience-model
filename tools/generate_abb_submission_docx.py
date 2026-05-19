from __future__ import annotations

import html
import os
import zipfile
from pathlib import Path


OUT = Path("deliverables/ABB_AutoML_Copilot_Submission.docx")


def t(text: str) -> str:
    return html.escape(text, quote=False)


def p(text: str = "", style: str | None = None) -> str:
    ppr = f"<w:pPr><w:pStyle w:val=\"{style}\"/></w:pPr>" if style else ""
    return f"<w:p>{ppr}<w:r><w:t>{t(text)}</w:t></w:r></w:p>"


def bullet(text: str) -> str:
    return (
        "<w:p><w:pPr><w:pStyle w:val=\"ListParagraph\"/>"
        "<w:numPr><w:ilvl w:val=\"0\"/><w:numId w:val=\"1\"/></w:numPr></w:pPr>"
        f"<w:r><w:t>{t(text)}</w:t></w:r></w:p>"
    )


def page_break() -> str:
    return "<w:p><w:r><w:br w:type=\"page\"/></w:r></w:p>"


def table(headers: list[str], rows: list[list[str]]) -> str:
    def cell(text: str, bold: bool = False) -> str:
        rpr = "<w:rPr><w:b/></w:rPr>" if bold else ""
        return (
            "<w:tc><w:tcPr><w:tcW w:w=\"2400\" w:type=\"dxa\"/></w:tcPr>"
            f"<w:p><w:r>{rpr}<w:t>{t(text)}</w:t></w:r></w:p></w:tc>"
        )

    out = [
        "<w:tbl>",
        "<w:tblPr><w:tblStyle w:val=\"TableGrid\"/><w:tblW w:w=\"0\" w:type=\"auto\"/>"
        "<w:tblLook w:val=\"04A0\" w:firstRow=\"1\" w:lastRow=\"0\" w:firstColumn=\"1\" "
        "w:lastColumn=\"0\" w:noHBand=\"0\" w:noVBand=\"1\"/></w:tblPr>",
        "<w:tblGrid>",
    ]
    for _ in headers:
        out.append("<w:gridCol w:w=\"2400\"/>")
    out.append("</w:tblGrid>")
    out.append("<w:tr>" + "".join(cell(h, True) for h in headers) + "</w:tr>")
    for row in rows:
        out.append("<w:tr>" + "".join(cell(c) for c in row) + "</w:tr>")
    out.append("</w:tbl>")
    return "".join(out)


def architecture_diagram() -> str:
    diagram = """+----------------------+
|      User Upload     |
| CSV / Excel / JSON   |
| Parquet Dataset      |
+----------+-----------+
           |
           v
+----------------------+
|   Frontend Dashboard |
| Next.js + React UI   |
+----------+-----------+
           |
           v
+----------------------+
|    FastAPI Backend   |
| Upload API + Job API |
| WebSocket Updates    |
+----------+-----------+
           |
           v
+----------------------+
|    Data Profiler     |
| pandas + NumPy       |
| Metadata Extraction  |
+----------+-----------+
           |
           v
+----------------------+
| Metadata-Only AI     |
| CrewAI + Gemini      |
| Agent Reasoning      |
+----------+-----------+
           |
           v
+----------------------+
| Specialized Agents   |
| Data Agent           |
| Task Agent           |
| Workflow Agent       |
| Model Strategist     |
| Optimization Agent   |
| Evaluation Agent     |
| Explainability Agent |
| Report Agent         |
+----------+-----------+
           |
           v
+----------------------+
|   ML Processing      |
| Preprocessing        |
| Model Training       |
| Hyperparameter Tune  |
| Benchmarking         |
+----------+-----------+
           |
           v
+----------------------+
| Explainability Layer |
| SHAP Feature Impact  |
| AI Interpretation    |
+----------+-----------+
           |
           v
+----------------------+
| Tracking and Memory  |
| MLflow + ChromaDB    |
+----------+-----------+
           |
           v
+----------------------+
|    Final Output      |
| Best Model Download  |
| Metrics Dashboard    |
| Executive AI Report  |
+----------------------+"""
    lines = []
    for line in diagram.splitlines():
        lines.append(
            "<w:p><w:r><w:rPr><w:rFonts w:ascii=\"Courier New\" w:hAnsi=\"Courier New\"/>"
            f"<w:sz w:val=\"18\"/></w:rPr><w:t xml:space=\"preserve\">{t(line)}</w:t></w:r></w:p>"
        )
    return "".join(lines)


def build_body() -> str:
    parts: list[str] = []

    parts += [
        p("ADAPTIVE MULTI-AGENT DATA SCIENCE COPILOT", "Title"),
        p("PAGE 1: INPUTS CONSIDERED", "Heading1"),
        p("PROBLEM STATEMENT", "Heading2"),
        p("Design and develop an adaptive data science platform that can automatically analyze user datasets, identify the suitable machine learning task, generate a workflow, train models, evaluate performance, explain results, and produce a professional AI-driven report."),
        p("PROBLEM UNDERSTANDING", "Heading2"),
        p("Modern industries generate large and complex datasets. Preparing these datasets for machine learning usually requires manual effort in data cleaning, preprocessing, model selection, hyperparameter tuning, evaluation, and reporting."),
        p("The proposed system, Adaptive Multi-Agent Data Science Copilot, solves this problem by using multiple specialized AI agents and an automated ML engine. The platform allows users to upload a dataset and receive a complete machine learning workflow with minimum manual intervention."),
        p("A major advantage of this system is that the AI agents work only with metadata, not raw user data. This improves privacy while still allowing intelligent decision-making."),
        p("INPUTS CONSIDERED", "Heading2"),
    ]
    parts.append(
        table(
            ["Input Category", "User Data Considered", "Metadata Extracted", "Purpose"],
            [
                ["Structured Dataset", "CSV, Excel, JSON, or Parquet file uploaded by the user", "File type, upload ID, storage path", "Starts the automated ML workflow"],
                ["Rows and Columns", "Complete tabular records", "Number of rows and columns", "Understands dataset size and complexity"],
                ["Numerical Features", "Integer and decimal columns", "Mean, standard deviation, min, max, skewness", "Used for statistical analysis and model training"],
                ["Categorical Features", "Text, category, label, or boolean columns", "Unique values, category count, missing percentage", "Used for encoding and classification analysis"],
                ["Datetime Features", "Date, time, timestamp, month, year columns", "Date detection, frequency, time steps", "Used to detect forecasting tasks"],
                ["Target Column", "Output column such as class, label, price, sales, churn, fraud, revenue", "Suggested target, target type, number of classes", "Helps detect supervised ML task"],
                ["Data Quality Indicators", "Missing values, duplicate rows, imbalance", "Missing percentage, duplicate count, imbalance ratio", "Used for preprocessing decisions"],
                ["Feature Statistics", "Distribution of selected columns", "Feature-level summary", "Helps AI agents understand data without seeing raw records"],
                ["Time-Series Pattern", "Sequential timestamp-based records", "Frequency, missing timestamps, time-series type", "Used for forecasting model selection"],
                ["Model Output Data", "Trained model and metrics", "Best model, scores, model path", "Used for reporting and model download"],
            ],
        )
    )
    parts += [
        p("KEY INNOVATION", "Heading2"),
        p("The project uses a multi-agent AI system for automated data science workflow generation. Each AI agent performs a specific role such as data analysis, task detection, workflow planning, model selection, optimization, evaluation, explainability, and report generation."),
        p("This transforms a traditional manual machine learning pipeline into an intelligent, adaptive, and privacy-aware AutoML platform."),
        p("TECHNOLOGIES USED", "Heading2"),
        p("React, Next.js, Tailwind CSS, FastAPI, WebSockets, CrewAI, Gemini, pandas, NumPy, scikit-learn, XGBoost, Optuna, SHAP, statsmodels, MLflow, ChromaDB, and Docker Compose."),
        page_break(),
        p("PAGES 2-4: PROCESS TO BE FOLLOWED", "Heading1"),
        p("1. PROPOSED ENTERPRISE SYSTEM ARCHITECTURE", "Heading2"),
        p("The proposed architecture follows a modular enterprise-grade AI engineering design. It integrates frontend dashboard, FastAPI backend, multi-agent AI orchestration, metadata-based reasoning, automated ML processing, hyperparameter optimization, explainable AI, experiment tracking, workflow memory, and model export."),
        p("SYSTEM WORKFLOW ARCHITECTURE", "Heading2"),
        architecture_diagram(),
        p("ARCHITECTURE EXPLANATION", "Heading2"),
        p("Frontend Layer", "Heading3"),
        p("The frontend is developed using Next.js and React. It provides dataset upload, workflow monitoring, AI agent status updates, model performance visualization, explainability charts, and final report display."),
        p("Backend Layer", "Heading3"),
        p("The FastAPI backend manages file upload, pipeline execution, API communication, WebSocket updates, model download, and job status tracking. It runs the complete workflow asynchronously so that long-running ML tasks can be monitored in real time."),
        p("Data Profiling Layer", "Heading3"),
        p("The uploaded dataset is analyzed using pandas and NumPy. The profiler extracts only metadata such as row count, column count, data types, missing values, duplicate rows, suggested target column, and time-series indicators."),
        p("AI Agent Layer", "Heading3"),
        p("CrewAI coordinates specialized agents powered by Gemini. These agents reason on metadata and make decisions about data quality, task type, workflow plan, model strategy, optimization results, evaluation summary, explainability, and final reporting."),
        page_break(),
        p("MULTI-AGENT AI WORKFLOW", "Heading2"),
        p("The platform uses collaborative AI agents to automate the complete data science lifecycle. Each agent has a specific responsibility and contributes to the final workflow."),
    ]
    parts.append(
        table(
            ["AI Agent", "Responsibility"],
            [
                ["Data Agent", "Analyzes dataset metadata and identifies data quality issues"],
                ["Task Agent", "Detects classification, regression, clustering, or forecasting task"],
                ["Workflow Agent", "Plans preprocessing and workflow steps"],
                ["Model Strategist Agent", "Selects suitable machine learning models"],
                ["Optimization Agent", "Analyzes Optuna hyperparameter tuning results"],
                ["Evaluation Agent", "Benchmarks models and explains performance"],
                ["Explainability Agent", "Interprets SHAP feature importance"],
                ["Report Agent", "Generates the final executive AI report"],
            ],
        )
    )
    parts += [
        p("WORKFLOW EXECUTION PIPELINE", "Heading2"),
        bullet("The user uploads a dataset through the frontend dashboard."),
        bullet("The backend stores the dataset and starts a pipeline job."),
        bullet("The Data Profiler extracts metadata from the dataset."),
        bullet("The Data Agent analyzes data quality."),
        bullet("The Task Agent detects the ML task type."),
        bullet("The Workflow Agent creates the preprocessing plan."),
        bullet("The Model Strategist selects suitable algorithms."),
        bullet("The preprocessing engine prepares the data for training."),
        bullet("Multiple models are trained using scikit-learn, XGBoost, or statsmodels."),
        bullet("Optuna performs hyperparameter optimization."),
        bullet("The Evaluation Agent benchmarks model performance."),
        bullet("The best model is selected based on the primary metric."),
        bullet("SHAP explainability identifies important features."),
        bullet("MLflow logs experiment results and ChromaDB stores workflow memory."),
        bullet("The Report Agent generates the final AI report."),
        bullet("The best model is saved and made available for download."),
        page_break(),
        p("SUPPORTED MACHINE LEARNING TASKS", "Heading2"),
    ]
    parts.append(
        table(
            ["Task Type", "Models Used", "Evaluation Metrics"],
            [
                ["Classification", "Logistic Regression, Random Forest, XGBoost", "Accuracy, Precision, Recall, F1-score, ROC-AUC"],
                ["Regression", "Linear Regression, Random Forest Regressor, XGBoost Regressor", "RMSE, MAE, R2 Score"],
                ["Clustering", "KMeans, DBSCAN", "Number of clusters, Silhouette Score"],
                ["Forecasting", "ARIMA, Exponential Smoothing", "AIC, BIC, Forecast Values"],
            ],
        )
    )
    parts += [
        p("SCALABILITY AND ROBUSTNESS", "Heading2"),
        p("The system is designed with a modular architecture where the frontend, backend, AI agents, ML engine, tracking layer, and storage layer are separated. This makes the platform easier to scale, maintain, and extend."),
        p("The backend uses asynchronous execution and WebSocket-based real-time updates, allowing users to monitor long-running ML workflows without blocking the interface."),
        p("Docker Compose support makes deployment consistent across different environments. MLflow improves experiment tracking, and ChromaDB provides workflow memory for future reuse."),
        page_break(),
        p("PAGE 5: EXPECTED OUTPUT", "Heading1"),
        p("EXPECTED OUTPUT OF THE PROJECT", "Heading2"),
        p("The expected output is a complete automated data science workflow delivered through an interactive and professional web dashboard."),
        p("1. INTELLIGENT DASHBOARD OUTPUT", "Heading2"),
        bullet("Dataset upload option"),
        bullet("Real-time workflow status"),
        bullet("AI agent progress logs"),
        bullet("Model training status"),
        bullet("Benchmarking charts"),
        bullet("SHAP explainability visualization"),
        bullet("Final AI report"),
        bullet("Best model download option"),
        p("2. DATASET INTELLIGENCE OUTPUT", "Heading2"),
    ]
    parts.append(
        table(
            ["Output Field", "Example"],
            [
                ["Total Rows", "Based on uploaded dataset"],
                ["Total Columns", "Based on uploaded dataset"],
                ["Numerical Features", "Detected automatically"],
                ["Categorical Features", "Detected automatically"],
                ["Missing Values", "Percentage calculated by profiler"],
                ["Duplicate Rows", "Count detected by profiler"],
                ["Suggested Target", "Automatically identified"],
                ["Detected Task", "Classification / Regression / Clustering / Forecasting"],
            ],
        )
    )
    parts += [
        p("3. AI AGENT COLLABORATION OUTPUT", "Heading2"),
        p("The AI agents automatically perform data quality analysis, task detection, workflow planning, model selection, optimization analysis, model evaluation explanation, SHAP interpretation, and final report generation."),
        p("4. MODEL BENCHMARKING OUTPUT", "Heading2"),
    ]
    parts.append(
        table(
            ["Model", "Metric Score", "Result"],
            [
                ["Logistic Regression", "Task-specific score", "Baseline model"],
                ["Random Forest", "Task-specific score", "Strong ensemble model"],
                ["XGBoost", "Task-specific score", "High-performance model"],
                ["Optimized Model", "Best score after tuning", "Selected best model"],
            ],
        )
    )
    parts += [
        p("5. SELECTED BEST MODEL", "Heading2"),
        p("The system selects the best-performing model based on the primary evaluation metric. The selected model is saved as a downloadable .pkl file."),
        p("6. EXPLAINABLE AI OUTPUT", "Heading2"),
        p("The SHAP explainability module provides feature importance ranking, model behavior explanation, prediction transparency, business-friendly interpretation, and trustworthy AI insights."),
        p("7. EXECUTIVE AI REPORT", "Heading2"),
        p("The final AI report includes dataset overview, data quality findings, detected ML task, workflow plan, model selection details, optimization summary, model comparison, best model recommendation, explainability insights, and final conclusion."),
        p("FINAL CONCLUSION", "Heading2"),
        p("The Adaptive Multi-Agent Data Science Copilot is an innovative and industrially relevant project that automates the complete machine learning lifecycle. It combines multi-agent AI reasoning, automated ML processing, real-time workflow monitoring, explainable AI, experiment tracking, and model export."),
    ]
    parts.append(
        table(
            ["Evaluation Criteria", "How It Is Satisfied"],
            [
                ["Innovation and Originality", "Uses collaborative AI agents and metadata-only reasoning for automated data science"],
                ["Technical Implementation", "Built with FastAPI, Next.js, CrewAI, Gemini, scikit-learn, XGBoost, Optuna, SHAP, MLflow, and ChromaDB"],
                ["Industrial Relevance", "Supports privacy-aware, explainable, and reusable ML workflows for enterprise use"],
                ["Scalability and Robustness", "Modular architecture, async backend, Docker support, tracking, and workflow memory"],
            ],
        )
    )
    parts.append(p("Overall, the system reduces manual effort, improves productivity, and provides a scalable foundation for enterprise data science automation."))
    return "".join(parts)


def write_docx(path: Path) -> None:
    document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas"
 xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
 xmlns:o="urn:schemas-microsoft-com:office:office"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
 xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"
 xmlns:v="urn:schemas-microsoft-com:vml"
 xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing"
 xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
 xmlns:w10="urn:schemas-microsoft-com:office:word"
 xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
 xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml"
 xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup"
 xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk"
 xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml"
 xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape"
 mc:Ignorable="w14 wp14">
 <w:body>{build_body()}<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="720" w:right="720" w:bottom="720" w:left="720" w:header="708" w:footer="708" w:gutter="0"/></w:sectPr></w:body>
</w:document>"""

    styles_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
 <w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="22"/></w:rPr><w:pPr><w:spacing w:after="120"/></w:pPr></w:style>
 <w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:rPr><w:b/><w:sz w:val="36"/><w:color w:val="0B2942"/></w:rPr><w:pPr><w:jc w:val="center"/><w:spacing w:after="240"/></w:pPr></w:style>
 <w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:rPr><w:b/><w:sz w:val="30"/><w:color w:val="0B2942"/></w:rPr><w:pPr><w:spacing w:before="240" w:after="120"/></w:pPr></w:style>
 <w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:rPr><w:b/><w:sz w:val="25"/><w:color w:val="C8102E"/></w:rPr><w:pPr><w:spacing w:before="180" w:after="100"/></w:pPr></w:style>
 <w:style w:type="paragraph" w:styleId="Heading3"><w:name w:val="heading 3"/><w:basedOn w:val="Normal"/><w:rPr><w:b/><w:sz w:val="23"/><w:color w:val="333333"/></w:rPr><w:pPr><w:spacing w:before="120" w:after="80"/></w:pPr></w:style>
 <w:style w:type="paragraph" w:styleId="ListParagraph"><w:name w:val="List Paragraph"/><w:basedOn w:val="Normal"/><w:pPr><w:ind w:left="720" w:hanging="360"/></w:pPr></w:style>
 <w:style w:type="table" w:styleId="TableGrid"><w:name w:val="Table Grid"/><w:tblPr><w:tblBorders><w:top w:val="single" w:sz="4" w:color="BFBFBF"/><w:left w:val="single" w:sz="4" w:color="BFBFBF"/><w:bottom w:val="single" w:sz="4" w:color="BFBFBF"/><w:right w:val="single" w:sz="4" w:color="BFBFBF"/><w:insideH w:val="single" w:sz="4" w:color="BFBFBF"/><w:insideV w:val="single" w:sz="4" w:color="BFBFBF"/></w:tblBorders></w:tblPr></w:style>
</w:styles>"""

    numbering_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
 <w:abstractNum w:abstractNumId="0"><w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val="•"/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="720" w:hanging="360"/></w:pPr></w:lvl></w:abstractNum>
 <w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>
</w:numbering>"""

    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

    doc_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>"""

    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
 <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
 <Default Extension="xml" ContentType="application/xml"/>
 <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
 <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
 <Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>
</Types>"""

    os.makedirs(path.parent, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("word/_rels/document.xml.rels", doc_rels)
        z.writestr("word/document.xml", document_xml)
        z.writestr("word/styles.xml", styles_xml)
        z.writestr("word/numbering.xml", numbering_xml)


if __name__ == "__main__":
    write_docx(OUT)
    print(OUT)
