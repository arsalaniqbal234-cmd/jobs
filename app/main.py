from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import requests

from database import engine, get_db, Base
from models import Job as JobModel


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://jobsi-ten.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


Base.metadata.create_all(bind=engine)


@app.get("/")
async def root():
    return {"message": "Hello Arsalan, API is working!"}


@app.get("/about")
async def about():
    return {
        "creator": "Arsalan",
        "project": "Week 1 Full Stack App"
    }


@app.get("/user/{user_id}")
async def get_user(user_id: int):
    return {
        "user_id": user_id,
        "message": f"Showing profile for user {user_id}"
    }


@app.get("/search")
async def search(keyword: str, limit: int = 10, db: Session = Depends(get_db)):
    results = (
        db.query(JobModel)
        .filter(
            (JobModel.title.ilike(f"%{keyword}%")) |
            (JobModel.company.ilike(f"%{keyword}%"))
        )
        .limit(limit)
        .all()
    )
    return results


class JobCreate(BaseModel):
    title: str
    company: str
    salary: int


@app.post("/jobs")
async def create_job(
    job: JobCreate,
    db: Session = Depends(get_db)
):
    new_job = JobModel(
        title=job.title,
        company=job.company,
        salary=job.salary
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return new_job


@app.post("/scrape")
async def scrape_jobs(db: Session = Depends(get_db)):
    url = "https://remoteok.com/api"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    data = response.json()

    jobs_data = data[1:]

    added_count = 0
    skipped_count = 0

    for job in jobs_data[:20]:
        source_id = str(job.get("id"))
        title = job.get("position", "Unknown")
        company = job.get("company", "Unknown")
        job_url = job.get("url", "")

        existing = db.query(JobModel).filter(JobModel.source_id == source_id).first()

        if existing:
            skipped_count += 1
            continue

        new_job = JobModel(
            source_id=source_id,
            title=title,
            company=company,
            salary=0,
            url=job_url
        )
        db.add(new_job)
        added_count += 1

    db.commit()
    return {
        "message": f"{added_count} new jobs added, {skipped_count} duplicates skipped"
    }
    


@app.get("/jobs")
async def get_jobs(
    db: Session = Depends(get_db)
):

    jobs = db.query(JobModel).all()

    return jobs





@app.get("/jobs/{job_id}")
async def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(JobModel).filter(JobModel.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job