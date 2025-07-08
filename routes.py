import os
import shutil

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import and_
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, Jobs
from schemas.base_model import Register, LoginRequest, JobRequest
from utils.common import parse_resume
from utils.security import hash_password, create_access_token, verify_access_token

router = APIRouter()


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload  # or query DB again with email


@router.get("/")
def root():
    return {"message": "success"}


@router.post("/login")
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(and_(User.email == login_data.email, User.is_active == True)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.password != hash_password(login_data.password):
        raise HTTPException(status_code=404, detail="Invalid Credentials")

    token = create_access_token(data={"sub": user.email, "id": user.id, "user_type": user.user_type})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "user_type": user.user_type
        }
    }


@router.post("/register/recruiter")
def register_recruiter(register: Register, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == register.email).first()
    if user:
        raise HTTPException(status_code=404, detail="Email already registered")

    new_user = User(
        name=register.name,
        email=register.email,
        password=hash_password(register.password),
        user_type="RECRUITER"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Recruiter registered successfully", "data": {"id": new_user.id, "email": new_user.email}}


@router.post("/register/candidate")
def register_candidate(register: Register, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == register.email).first()
    if user:
        raise HTTPException(status_code=404, detail="Email already registered")

    new_user = User(
        name=register.name,
        email=register.email,
        password=hash_password(register.password),
        user_type="CANDIDATE"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Candidate registered successfully", "data": {"id": new_user.id, "email": new_user.email}}


@router.post("/jobs")
def jobs(job_request: JobRequest, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["user_type"] == "RECRUITER":
        new_job = Jobs(
            title=job_request.title,
            description=job_request.description,
            company_name=job_request.company_name,
            pincode=job_request.pincode,
            city=job_request.city,
            country=job_request.country,
            recruiter_id=current_user["id"])
        db.add(new_job)
        db.commit()
        db.refresh(new_job)
        return {"message": "Job added successfully", "data": {"id": new_job.id, "title": new_job.title}}
    else:
        raise HTTPException(status_code=401, detail="You are not allowed to add jobs")


@router.get("/jobs")
def jobs(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["user_type"] == "RECRUITER":
        jobs_list = db.query(Jobs).filter(Jobs.recruiter_id == current_user["id"]).all()
    else:
        jobs_list = db.query(Jobs).all()
    return {"message": "Jobs list", "data": jobs_list}


@router.get("/jobs/{job_id}")
def jobs_add(job_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["user_type"] == "RECRUITER":
        job = db.query(Jobs).filter(Jobs.recruiter_id == current_user["id"]).first()
        jobs_list = {
            "title": job.title,
            "description": job.description,
            "company_name": job.company_name,
            "applicants": [],
        }
        for applicant in job.applicants:
            jobs_list["applicants"].append({"id": applicant.id, "email": applicant.email})
    else:
        jobs_list = db.query(Jobs).filter(Jobs.id == job_id).all()
    return {"message": "Jobs details", "data": jobs_list}


@router.post("/jobs/{job_id}/apply")
def jobs_apply(job_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["user_type"] == "RECRUITER":
        raise HTTPException(status_code=401, detail="You are not allowed to apply jobs")
    job = db.query(Jobs).filter(Jobs.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    candidate = db.query(User).filter(User.id == current_user["id"]).first()
    if candidate in job.applicants:
        raise HTTPException(status_code=400, detail="Candidate has already applied to this job")
    job.applicants.append(candidate)
    db.commit()
    return {"message": "Job applied successfully", "data": {"id": job.id, "title": job.title}}


@router.get("/applied/jobs")
def applied_jobs(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["user_type"] == "RECRUITER":
        raise HTTPException(status_code=401, detail="You are not allowed to see jobs")
    user = db.query(User).filter(User.id == current_user["id"]).first()
    return {"message": "Applied Jobs", "data": {"id": user.id, "applied": user.applied_jobs}}


@router.post("/upload/pdf")
async def upload_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...),
                     current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Generate unique filename
    file_id = f"{current_user['id']}.pdf"
    file_path = os.path.join("uploads/pdfs", file_id)

    # Save file to disk
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    background_tasks.add_task(parse_resume, file_path, current_user["id"], db)
    return {"message": "PDF uploaded successfully", "filename": file_id}
