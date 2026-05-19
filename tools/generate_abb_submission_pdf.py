from __future__ import annotations

import os
from dataclasses import dataclass


PAGE_W = 595
PAGE_H = 842
MARGIN = 42


def esc(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def wrap_text(text: str, max_chars: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        if len(current) + len(word) + (1 if current else 0) <= max_chars:
            current = f"{current} {word}".strip()
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


@dataclass
class Page:
    number: int
    title: str
    subtitle: str
    commands: list[str]


class SimplePdf:
    def __init__(self) -> None:
        self.pages: list[Page] = []

    def new_page(self, title: str, subtitle: str) -> Page:
        page = Page(len(self.pages) + 1, title, subtitle, [])
        self.pages.append(page)
        self._header(page)
        return page

    def _header(self, p: Page) -> None:
        c = p.commands
        c.append("0.05 0.16 0.29 rg")
        c.append(f"0 {PAGE_H - 72} {PAGE_W} 72 re f")
        c.append("1 1 1 rg")
        self.text(p, MARGIN, PAGE_H - 34, "Adaptive Multi-Agent Data Science Copilot", 15, "B")
        self.text(p, MARGIN, PAGE_H - 55, p.subtitle, 9, "R")
        self.text(p, PAGE_W - 92, PAGE_H - 34, f"Page {p.number}/5", 9, "B")
        c.append("0 0 0 rg")

    def _footer(self, p: Page) -> None:
        p.commands.append("0.70 0.74 0.78 RG")
        p.commands.append(f"{MARGIN} 32 {PAGE_W - 2 * MARGIN} 0.5 re f")
        p.commands.append("0.35 0.39 0.43 rg")
        self.text(p, MARGIN, 20, "ABB Project Submission | Maximum file size target: below 5 MB", 8, "R")
        self.text(p, PAGE_W - 130, 20, "Generated from project documentation", 8, "R")

    def text(self, p: Page, x: float, y: float, s: str, size: int = 10, font: str = "R") -> None:
        font_name = "F2" if font == "B" else "F1"
        p.commands.append(f"BT /{font_name} {size} Tf {x:.2f} {y:.2f} Td ({esc(s)}) Tj ET")

    def paragraph(
        self,
        p: Page,
        x: float,
        y: float,
        text: str,
        max_chars: int = 86,
        size: int = 9,
        leading: int = 13,
        font: str = "R",
    ) -> float:
        for line in wrap_text(text, max_chars):
            self.text(p, x, y, line, size, font)
            y -= leading
        return y

    def heading(self, p: Page, x: float, y: float, text: str) -> float:
        p.commands.append("0.82 0.09 0.10 rg")
        self.text(p, x, y, text, 13, "B")
        p.commands.append("0 0 0 rg")
        return y - 20

    def bullet(self, p: Page, x: float, y: float, text: str, max_chars: int = 82) -> float:
        lines = wrap_text(text, max_chars)
        self.text(p, x, y, "-", 9, "B")
        self.text(p, x + 12, y, lines[0], 9, "R")
        y -= 13
        for line in lines[1:]:
            self.text(p, x + 12, y, line, 9, "R")
            y -= 13
        return y

    def table(self, p: Page, x: float, y: float, widths: list[int], headers: list[str], rows: list[list[str]], row_h: int = 34) -> float:
        total_w = sum(widths)
        h = 28
        p.commands.append("0.05 0.16 0.29 rg")
        p.commands.append(f"{x} {y - h} {total_w} {h} re f")
        tx = x
        for i, head in enumerate(headers):
            self.text(p, tx + 5, y - 18, head, 7, "B")
            tx += widths[i]
        y -= h
        p.commands.append("0 0 0 rg")
        for idx, row in enumerate(rows):
            if idx % 2 == 0:
                p.commands.append("0.96 0.97 0.98 rg")
            else:
                p.commands.append("1 1 1 rg")
            p.commands.append(f"{x} {y - row_h} {total_w} {row_h} re f")
            p.commands.append("0 0 0 rg")
            tx = x
            for i, cell in enumerate(row):
                max_chars = max(9, widths[i] // 5)
                lines = wrap_text(cell, max_chars)[:3]
                ty = y - 11
                for line in lines:
                    self.text(p, tx + 5, ty, line, 6, "R")
                    ty -= 9
                tx += widths[i]
            p.commands.append("0.78 0.82 0.86 RG")
            tx = x
            for w in widths:
                p.commands.append(f"{tx} {y - row_h} 0.4 {row_h} re f")
                tx += w
            p.commands.append(f"{x} {y - row_h} {total_w} 0.4 re f")
            y -= row_h
        return y

    def architecture(self, p: Page, x: float, y: float) -> None:
        boxes = [
            ("User Upload", "CSV, Excel, JSON, Parquet"),
            ("Frontend Dashboard", "Next.js + React"),
            ("FastAPI Backend", "Upload API, Jobs, WebSockets"),
            ("Data Profiler", "pandas/numpy metadata extraction"),
            ("Metadata-Only Agents", "CrewAI + Gemini reasoning"),
            ("ML Processing", "Preprocess, train, tune, evaluate"),
            ("Explainability", "SHAP feature impact"),
            ("Tracking and Memory", "MLflow + ChromaDB"),
            ("Final Output", "Best model, metrics, AI report"),
        ]
        box_w = 250
        box_h = 38
        gap = 12
        for i, (title, sub) in enumerate(boxes):
            by = y - i * (box_h + gap)
            p.commands.append("0.96 0.98 1.00 rg")
            p.commands.append(f"{x} {by - box_h} {box_w} {box_h} re f")
            p.commands.append("0.05 0.16 0.29 RG")
            p.commands.append(f"{x} {by - box_h} {box_w} {box_h} re S")
            p.commands.append("0.05 0.16 0.29 rg")
            self.text(p, x + 10, by - 14, title, 9, "B")
            p.commands.append("0.22 0.27 0.32 rg")
            self.text(p, x + 10, by - 29, sub, 7, "R")
            if i < len(boxes) - 1:
                cx = x + box_w / 2
                p.commands.append("0.82 0.09 0.10 RG")
                p.commands.append(f"{cx} {by - box_h} m {cx} {by - box_h - gap + 3} l S")
                p.commands.append(f"{cx - 3} {by - box_h - gap + 6} m {cx} {by - box_h - gap + 2} l {cx + 3} {by - box_h - gap + 6} l S")
        p.commands.append("0 0 0 rg")

    def save(self, path: str) -> None:
        for page in self.pages:
            self._footer(page)

        objects: list[bytes] = []

        def add(obj: str | bytes) -> int:
            if isinstance(obj, str):
                obj = obj.encode("latin-1")
            objects.append(obj)
            return len(objects)

        font_r = add("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
        font_b = add("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
        page_obj_ids: list[int] = []
        content_ids: list[int] = []
        for page in self.pages:
            stream = "\n".join(page.commands).encode("latin-1")
            content_ids.append(add(b"<< /Length " + str(len(stream)).encode("latin-1") + b" >>\nstream\n" + stream + b"\nendstream"))
            page_obj_ids.append(0)

        pages_id_placeholder = len(objects) + len(self.pages) + 1
        for i, _ in enumerate(self.pages):
            page_obj_ids[i] = add(
                f"<< /Type /Page /Parent {pages_id_placeholder} 0 R /MediaBox [0 0 {PAGE_W} {PAGE_H}] "
                f"/Resources << /Font << /F1 {font_r} 0 R /F2 {font_b} 0 R >> >> "
                f"/Contents {content_ids[i]} 0 R >>"
            )

        kids = " ".join(f"{pid} 0 R" for pid in page_obj_ids)
        pages_id = add(f"<< /Type /Pages /Kids [{kids}] /Count {len(self.pages)} >>")
        catalog_id = add(f"<< /Type /Catalog /Pages {pages_id} 0 R >>")

        out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = [0]
        for idx, obj in enumerate(objects, start=1):
            offsets.append(len(out))
            out.extend(f"{idx} 0 obj\n".encode("latin-1"))
            out.extend(obj)
            out.extend(b"\nendobj\n")
        xref = len(out)
        out.extend(f"xref\n0 {len(objects) + 1}\n".encode("latin-1"))
        out.extend(b"0000000000 65535 f \n")
        for off in offsets[1:]:
            out.extend(f"{off:010d} 00000 n \n".encode("latin-1"))
        out.extend(
            f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode("latin-1")
        )

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as fh:
            fh.write(out)


def build_pdf(path: str) -> None:
    pdf = SimplePdf()

    p = pdf.new_page("Inputs Considered", "Page 1: Inputs considered")
    y = PAGE_H - 100
    y = pdf.heading(p, MARGIN, y, "Project Overview")
    y = pdf.paragraph(
        p,
        MARGIN,
        y,
        "This project is an Adaptive Multi-Agent Data Science Copilot built for the ABB assignment. It behaves like a practical AutoML assistant: the user uploads a dataset, the platform studies it, plans the machine learning workflow, trains suitable models, explains the results, and prepares an executive summary.",
        92,
        9,
    )
    y -= 8
    y = pdf.heading(p, MARGIN, y, "User Data and Metadata Considered")
    rows = [
        ["Dataset file", "CSV, Excel, JSON, or Parquet uploaded by the user", "File type, upload ID, storage path", "Starts the AutoML workflow"],
        ["Rows and columns", "Complete tabular records", "Row count and column count", "Estimates dataset size"],
        ["Numerical features", "Integer or decimal columns", "Mean, std, min, max, skewness, missing percent", "Supports training and analysis"],
        ["Categorical features", "Text, category, boolean, or label columns", "Unique values, category count, missing percent", "Used for encoding and task understanding"],
        ["Datetime features", "Date, time, timestamp, month, or year columns", "Date detection, frequency, time steps, missing timestamps", "Identifies forecasting use cases"],
        ["Target column", "Output such as target, label, class, price, sales, churn, fraud", "Suggested target, data type, number of classes", "Chooses supervised learning task"],
        ["Data quality", "Missing values and duplicate rows", "Missing percentage and duplicate count", "Plans cleaning strategy"],
        ["Class distribution", "Distribution of output labels", "Class count and imbalance ratio", "Detects classification risk"],
        ["Feature statistics", "Behavior of selected columns", "Compact feature summary", "Lets agents reason without raw data"],
        ["Model output", "Trained model and prediction results", "Best model name, metrics, model path", "Supports report and download"],
    ]
    pdf.table(p, MARGIN, y, [78, 142, 158, 118], ["Category", "User Data", "Metadata Extracted", "Purpose"], rows, 36)

    p = pdf.new_page("Process to Be Followed", "Page 2: Process to be followed")
    y = PAGE_H - 100
    y = pdf.heading(p, MARGIN, y, "Workflow Architecture")
    pdf.architecture(p, 58, y)
    y = PAGE_H - 110
    x2 = 340
    pdf.text(p, x2, y, "Architecture Summary", 13, "B")
    y -= 22
    y = pdf.paragraph(
        p,
        x2,
        y,
        "The system separates user experience, backend orchestration, AI reasoning, machine learning execution, explainability, and tracking. This makes the project easier to maintain and suitable for industrial workflows.",
        38,
        8,
        12,
    )
    y -= 8
    y = pdf.paragraph(
        p,
        x2,
        y,
        "A key design decision is privacy-aware reasoning: AI agents receive metadata only. Raw data remains inside the ML pipeline for preprocessing and training.",
        38,
        8,
        12,
    )
    y -= 10
    pdf.text(p, x2, y, "Evaluation Criteria Covered", 10, "B")
    y -= 16
    for item in [
        "Innovation: multi-agent AutoML workflow with AI reporting.",
        "Technical implementation: FastAPI, Next.js, CrewAI, Gemini, sklearn, XGBoost, Optuna, SHAP, MLflow, ChromaDB.",
        "Industrial relevance: supports repeatable, explainable, privacy-aware data science.",
        "Scalability: modular services, Docker setup, async jobs, WebSocket updates.",
    ]:
        y = pdf.bullet(p, x2, y, item, 36)

    p = pdf.new_page("Process to Be Followed", "Page 3: Process to be followed")
    y = PAGE_H - 100
    y = pdf.heading(p, MARGIN, y, "Step-by-Step Process")
    steps = [
        ("1. Dataset Upload and Loading", "The user uploads a dataset through the dashboard. The FastAPI backend saves the file and loads it using the correct reader for CSV, Excel, JSON, or Parquet."),
        ("2. Automated Data Profiling", "The DataProfiler studies the dataset with pandas and numpy. It extracts row count, column count, data types, missing values, duplicates, suggested target, class count, imbalance ratio, and time-series indicators."),
        ("3. Data Quality Analysis", "The DataAgent reviews metadata and identifies practical concerns such as missing values, duplicate records, class imbalance, unsuitable feature types, or weak target selection."),
        ("4. Task Detection", "The TaskAgent determines whether the problem is classification, regression, clustering, or forecasting. This decision guides model selection, preprocessing, metrics, and final reporting."),
    ]
    for title, body in steps:
        pdf.text(p, MARGIN, y, title, 11, "B")
        y -= 15
        y = pdf.paragraph(p, MARGIN + 12, y, body, 88, 9, 13)
        y -= 12
    y = pdf.heading(p, MARGIN, y, "Why This Process Is Useful")
    for item in [
        "It reduces manual effort for users who may not know every ML step.",
        "It keeps the workflow consistent across different datasets.",
        "It allows AI agents to guide decisions while proven ML libraries perform computation.",
        "It protects data privacy by passing only metadata to the LLM layer.",
    ]:
        y = pdf.bullet(p, MARGIN, y, item, 90)

    p = pdf.new_page("Process to Be Followed", "Page 4: Process to be followed")
    y = PAGE_H - 100
    y = pdf.heading(p, MARGIN, y, "Modeling, Evaluation, and Reporting")
    steps = [
        ("5. Workflow Planning", "The WorkflowAgent prepares preprocessing actions such as missing value handling, categorical encoding, numerical scaling, target preparation, and model-ready feature creation."),
        ("6. Model Selection", "The ModelStrategistAgent selects algorithms based on the detected task. Classification uses Logistic Regression, Random Forest, and XGBoost. Regression uses Linear Regression, Random Forest Regressor, and XGBoost Regressor. Clustering uses KMeans and DBSCAN. Forecasting uses ARIMA and Exponential Smoothing."),
        ("7. Training and Optimization", "The ML engine trains multiple models using scikit-learn, XGBoost, and statsmodels. Optuna is used for hyperparameter optimization so the system can improve performance beyond default settings."),
        ("8. Evaluation", "The EvaluationAgent benchmarks models with task-specific metrics. Classification uses accuracy, precision, recall, F1-score, ROC-AUC, and confusion matrix. Regression uses RMSE, MAE, and R2 score. Clustering uses silhouette score. Forecasting uses AIC, BIC, and forecast values."),
        ("9. Explainability and Final Report", "The ExplainabilityAgent uses SHAP to show feature importance and model behavior. The ReportAgent generates a business-friendly summary with data findings, model comparison, best model, explainability insights, and recommendations."),
    ]
    for title, body in steps:
        pdf.text(p, MARGIN, y, title, 10, "B")
        y -= 14
        y = pdf.paragraph(p, MARGIN + 12, y, body, 88, 8, 12)
        y -= 9
    rows = [
        ["Classification", "Accuracy, Precision, Recall, F1-score, ROC-AUC, Confusion Matrix"],
        ["Regression", "RMSE, MAE, R2 Score"],
        ["Clustering", "Number of Clusters, Silhouette Score"],
        ["Forecasting", "AIC, BIC, Forecast Values"],
    ]
    pdf.table(p, MARGIN, y, [120, 360], ["Task Type", "Evaluation Metrics"], rows, 28)

    p = pdf.new_page("Expected Output", "Page 5: Expected output")
    y = PAGE_H - 100
    y = pdf.heading(p, MARGIN, y, "Expected Output of the Project")
    y = pdf.paragraph(
        p,
        MARGIN,
        y,
        "The expected output is a complete automated data science workflow presented through a professional dashboard. The user receives model results, performance comparisons, explainability insights, and a downloadable trained model.",
        92,
        9,
    )
    y -= 8
    for title, body in [
        ("1. Interactive Dashboard", "The dashboard allows dataset upload and real-time monitoring of profiling, task detection, preprocessing, training, optimization, evaluation, explainability, and report generation."),
        ("2. Automated ML Results", "The system produces a dataset summary, data quality analysis, detected task type, preprocessing workflow, selected models, tuning results, benchmarking, and best model selection."),
        ("3. Explainable AI Insights", "SHAP-based feature importance and AI-generated interpretation help the user understand which features influence predictions."),
        ("4. Exportable Best Model", "The best-performing model is saved as a downloadable .pkl file so it can be reused, tested, or integrated into another application."),
        ("5. Executive AI Report", "The final report explains the dataset overview, ML task, data quality findings, model comparison, best model recommendation, explainability insights, and conclusion."),
    ]:
        pdf.text(p, MARGIN, y, title, 10, "B")
        y -= 14
        y = pdf.paragraph(p, MARGIN + 12, y, body, 88, 8, 12)
        y -= 8
    y = pdf.heading(p, MARGIN, y, "Scalability and Robustness")
    y = pdf.paragraph(
        p,
        MARGIN,
        y,
        "The solution is modular: frontend, backend, agents, ML engine, tracking, and memory are separated. The backend uses asynchronous execution and WebSocket updates for long-running jobs. Docker Compose supports consistent deployment. MLflow tracks experiments, while ChromaDB stores reusable workflow memory.",
        92,
        8,
        12,
    )
    y -= 8
    y = pdf.heading(p, MARGIN, y, "Conclusion")
    pdf.paragraph(
        p,
        MARGIN,
        y,
        "The Adaptive Multi-Agent Data Science Copilot combines originality, practical technical implementation, industrial usefulness, and scalable design. It reduces manual machine learning effort while keeping the workflow explainable, traceable, and privacy-aware.",
        92,
        9,
    )

    pdf.save(path)


if __name__ == "__main__":
    build_pdf(os.path.join("deliverables", "ABB_AutoML_Copilot_Submission.pdf"))
