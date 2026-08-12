from typing import Optional

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):

    username: str
    password: str


class RegisterRequest(BaseModel):

    role: str

    full_name: str

    email: EmailStr

    mobile: Optional[str] = None

    password: str

    confirm_password: str

    department: Optional[str] = None

    college_name: Optional[str] = None

    # Student
    student_id: Optional[str] = None
    roll_number: Optional[str] = None
    course: Optional[str] = None
    academic_group: Optional[str] = None
    current_year: Optional[str] = None
    semester: Optional[str] = None

    # Lecturer
    faculty_id: Optional[str] = None
    designation: Optional[str] = None

    # HOD
    hod_id: Optional[str] = None
