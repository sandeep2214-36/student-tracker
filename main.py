from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    status
)

from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session

from sqlalchemy.exc import IntegrityError

from database import (
    engine,
    Base,
    get_db
)

from models import (
    User,
    Student,
    Lecturer,
    HOD
)

from schemas import (
    LoginRequest,
    RegisterRequest
)

from auth import (
    hash_password,
    verify_password,
    create_access_token
)


# ============================================================
# CREATE DATABASE TABLES
# ============================================================

Base.metadata.create_all(
    bind=engine
)


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="EduTrack API",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "*"
    ],

    allow_credentials=True,

    allow_methods=[
        "*"
    ],

    allow_headers=[
        "*"
    ]
)


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "message": "EduTrack backend is running"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/api/health")
def health():

    return {
        "status": "ok"
    }


# ============================================================
# REGISTER
# ============================================================

@app.post("/api/register")
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):

    role = data.role.lower().strip()


    # --------------------------------------------------------
    # VALID ROLE
    # --------------------------------------------------------

    if role not in [
        "student",
        "lecturer",
        "hod"
    ]:

        raise HTTPException(
            status_code=400,
            detail="Invalid account type."
        )


    # --------------------------------------------------------
    # PASSWORD
    # --------------------------------------------------------

    if len(data.password) < 6:

        raise HTTPException(
            status_code=400,
            detail="Password must contain at least 6 characters."
        )


    if data.password != data.confirm_password:

        raise HTTPException(
            status_code=400,
            detail="Passwords do not match."
        )


    # --------------------------------------------------------
    # CHECK EMAIL
    # --------------------------------------------------------

    existing_email = db.query(
        User
    ).filter(
        User.email == str(data.email).lower()
    ).first()


    if existing_email:

        raise HTTPException(
            status_code=409,
            detail="Email is already registered."
        )


    # --------------------------------------------------------
    # USERNAME
    #
    # Login page accepts username OR email.
    #
    # We generate username from the role-specific ID.
    # --------------------------------------------------------

    if role == "student":

        if not data.student_id:

            raise HTTPException(
                status_code=400,
                detail="Student ID is required."
            )

        username = data.student_id.strip()


    elif role == "lecturer":

        if not data.faculty_id:

            raise HTTPException(
                status_code=400,
                detail="Faculty ID is required."
            )

        username = data.faculty_id.strip()


    else:

        if not data.hod_id:

            raise HTTPException(
                status_code=400,
                detail="HOD ID is required."
            )

        username = data.hod_id.strip()


    # --------------------------------------------------------
    # CHECK USERNAME
    # --------------------------------------------------------

    existing_username = db.query(
        User
    ).filter(
        User.username == username
    ).first()


    if existing_username:

        raise HTTPException(
            status_code=409,
            detail="ID is already registered."
        )


    # --------------------------------------------------------
    # CREATE USER
    # --------------------------------------------------------

    new_user = User(

        username=username,

        email=str(
            data.email
        ).lower(),

        password_hash=hash_password(
            data.password
        ),

        role=role,

        status="active"
    )


    db.add(new_user)

    db.flush()


    # --------------------------------------------------------
    # STUDENT
    # --------------------------------------------------------

    if role == "student":

        if not data.roll_number:

            db.rollback()

            raise HTTPException(
                status_code=400,
                detail="Roll Number is required."
            )


        existing_roll = db.query(
            Student
        ).filter(
            Student.roll_number ==
            data.roll_number.strip()
        ).first()


        if existing_roll:

            db.rollback()

            raise HTTPException(
                status_code=409,
                detail="Roll Number is already registered."
            )


        student = Student(

            user_id=new_user.id,

            student_id=data.student_id.strip(),

            full_name=data.full_name.strip(),

            roll_number=data.roll_number.strip(),

            mobile=data.mobile,

            department=data.department,

            course=data.course,

            academic_group=data.academic_group,

            current_year=data.current_year,

            semester=data.semester,

            college_name=data.college_name
        )


        db.add(student)


    # --------------------------------------------------------
    # LECTURER
    # --------------------------------------------------------

    elif role == "lecturer":

        lecturer = Lecturer(

            user_id=new_user.id,

            faculty_id=data.faculty_id.strip(),

            full_name=data.full_name.strip(),

            mobile=data.mobile,

            department=data.department,

            designation=data.designation,

            college_name=data.college_name
        )


        db.add(lecturer)


    # --------------------------------------------------------
    # HOD
    # --------------------------------------------------------

    elif role == "hod":

        hod = HOD(

            user_id=new_user.id,

            hod_id=data.hod_id.strip(),

            full_name=data.full_name.strip(),

            mobile=data.mobile,

            department=data.department,

            college_name=data.college_name
        )


        db.add(hod)


    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    try:

        db.commit()

        db.refresh(new_user)

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Account information already exists."
        )


    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {

        "success": True,

        "message":
            f"{role.capitalize()} account created successfully.",

        "user": {

            "id": new_user.id,

            "username": new_user.username,

            "email": new_user.email,

            "role": new_user.role

        }

    }


# ============================================================
# LOGIN
# ============================================================

@app.post("/api/login")
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):

    login_value = data.username.strip()


    # --------------------------------------------------------
    # FIND USER BY USERNAME OR EMAIL
    # --------------------------------------------------------

    user = db.query(
        User
    ).filter(
        (
            User.username == login_value
        ) |
        (
            User.email == login_value.lower()
        )
    ).first()


    # --------------------------------------------------------
    # USER NOT FOUND
    # --------------------------------------------------------

    if not user:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password."
        )


    # --------------------------------------------------------
    # ACCOUNT STATUS
    # --------------------------------------------------------

    if user.status != "active":

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account is inactive."
        )


    # --------------------------------------------------------
    # PASSWORD
    # --------------------------------------------------------

    if not verify_password(
        data.password,
        user.password_hash
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password."
        )


    # --------------------------------------------------------
    # TOKEN
    # --------------------------------------------------------

    access_token = create_access_token(

        user_id=user.id,

        username=user.username,

        role=user.role
    )


    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {

        "success": True,

        "access_token": access_token,

        "token_type": "bearer",

        "role": user.role,

        "user": {

            "id": user.id,

            "username": user.username,

            "email": user.email,

            "role": user.role

        }

    }


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(

        "main:app",

        host="0.0.0.0",

        port=8000,

        reload=True
    )
