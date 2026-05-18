from fastapi import APIRouter, HTTPException
from pipeline_executor import jobs

router = APIRouter()


@router.get("/status/{job_id}")
async def get_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    job = jobs[job_id]
    return {
        "job_id": job_id,
        "status": job.get("status", "unknown"),
        "updates": job.get("updates", []),
        "created_at": job.get("created_at"),
    }


@router.get("/results/{job_id}")
async def get_results(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    job = jobs[job_id]
    if job.get("status") != "completed":
        raise HTTPException(status_code=202, detail="Pipeline still running")
    return job.get("results", {})
