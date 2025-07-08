from pydantic import BaseModel, model_validator


class Register(BaseModel):
    name: str
    email: str
    password: str
    confirm_password: str

    @model_validator(mode='after')
    def validate_password_match(self) -> 'Register':
        if self.password != self.confirm_password:
            raise ValueError("Password and confirm password do not match.")
        return self


class LoginRequest(BaseModel):
    email: str
    password: str


class JobRequest(BaseModel):
    title: str
    description: str
    company_name: str
    pincode: int
    city: str
    country: str
