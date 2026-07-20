import requests
from database import SessionLocal
from models import Job

def scrape_jobs():
    url = "https://remoteok.com/api"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    data = response.json()

    # Pehla item legal/meta info hota hai, usko skip karo
    jobs_data = data[1:]

    db = SessionLocal()
    count = 0

    for job in jobs_data[:10]:  # pehle 10 jobs
        title = job.get("position", "Unknown")
        company = job.get("company", "Unknown")

        new_job = Job(title=title, company=company, salary=0)
        db.add(new_job)
        count += 1

    db.commit()
    db.close()
    print(f"{count} jobs saved to database!")

if __name__ == "__main__":
    scrape_jobs()