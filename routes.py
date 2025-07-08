from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import and_
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, Jobs
from schemas.base_model import Register, LoginRequest, JobRequest
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
def jobs_add(job_request: JobRequest, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
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
def jobs_add(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    jobs_list = db.query(Jobs).filter(Jobs.recruiter_id == current_user["id"]).all()
    return {"message": "Job added successfully", "data": jobs_list}
