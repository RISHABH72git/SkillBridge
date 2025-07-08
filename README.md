# 🧠 Resume Parser & Job Portal API (FastAPI + Bedrock + MySQL)

A full-featured backend system built using **FastAPI** for handling recruiter-candidate job workflows, with smart resume parsing using **Amazon Bedrock** (Claude/LLM), **MySQL** for persistence, and **JWT** authentication.

---

## 🚀 Features

- ✅ User registration: Recruiter / Candidate
- ✅ JWT-based login and secure session
- ✅ Recruiters can post jobs
- ✅ Candidates can apply to jobs
- ✅ Resume upload with PDF validation
- ✅ Background parsing of resumes using Amazon Bedrock LLM
- ✅ Parsed resume saved as structured JSON
- ✅ View all jobs with applicants
- ✅ RESTful APIs with FastAPI

---

## 🧱 Tech Stack

| Layer      | Tech                             |
|------------|----------------------------------|
| Backend    | FastAPI                          |
| Database   | MySQL with SQLAlchemy ORM        |
| Auth       | JWT (Password Flow)       |
| Resume     | PyMuPDF, Claude via Amazon Bedrock |
| Storage    | Local file system for PDF uploads |
