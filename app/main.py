from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import engine, get_db, Base
from models import Job as JobModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-frontend.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


@app.get("/")
async def root():
    return {"message": "Hello Arsalan, API is working!"}


@app.get("/about")
async def about():
    return {"creator": "Arsalan", "project": "Week 1 Full Stack App"}


@app.get("/user/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id, "message": f"Showing profile for user {user_id}"}


@app.get("/search")
async def search(keyword: str, limit: int = 10):
    return {"keyword": keyword, "limit": limit}


class JobCreate(BaseModel):
    title: str
    company: str
    salary: int


@app.post("/jobs")
async def create_job(job: JobCreate, db: Session = Depends(get_db)):
    new_job = JobModel(title=job.title, company=job.company, salary=job.salary)
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job


@app.get("/jobs")
async def get_jobs(db: Session = Depends(get_db)):
    jobs = db.query(JobModel).all()
    return jobs