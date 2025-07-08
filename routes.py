from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from schemas.base_model import Register
from utils.security import hash_password

router = APIRouter()


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# GET all users
@router.get("/")
def root():
    return {"message": "success"}


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
