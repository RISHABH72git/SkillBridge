import json
import fitz
import boto3
from models import User
bedrock = boto3.client("bedrock-runtime")


async def parse_resume(file_path: str, user_id: str, db):
    # You can replace this with actual resume parsing logic (PDF text extraction, NLP, etc.)
    print(f"Parsing resume for user {user_id} from file: {file_path}")
    doc = fitz.open(file_path)
    text = "".join([page.get_text() for page in doc])
    prompt = await build_resume_prompt(text)
    resume_data = await parse_resume_with_bedrock(prompt)
    data = json.loads(resume_data)
    print(data)
    db.query(User).filter(User.id == user_id).update({User.resume: data})
    db.commit()


async def build_resume_prompt(resume_text: str) -> str:
    prompt = f"""You are a smart and structured resume parser.
From the resume text provided below, extract the following information and return it as a valid JSON object:

- full_name: Candidate’s full name
- email: Email address
- phone: Contact phone number
- location: City, state, or country
- education: A list of objects, each containing:
    - degree
    - institution
    - graduation_year (if available)
- work_experience: A list of objects, each containing:
    - role
    - company
    - duration (e.g., "Jan 2021 – Mar 2023")
- skills: A list of relevant skills (technical + soft)

Resume:
""{resume_text}
""

Only return a valid, well-formatted JSON. Do not include any explanation or extra text.
"""
    return prompt.strip()


async def parse_resume_with_bedrock(prompt: str) -> dict:
    response = bedrock.invoke_model(
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",
        contentType="application/json",
        accept="application/json",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 2000
        })
    )
    response_body = json.loads(response.get('body').read())
    return response_body.get('content')[0].get('text')
