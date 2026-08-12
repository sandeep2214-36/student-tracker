from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum,
    ForeignKey,
    DateTime,
    func
)

from sqlalchemy.orm import relationship

from database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    username = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    email = Column(
        String(150),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    role = Column(
        Enum(
            "student",
            "lecturer",
            "hod"
        ),
        nullable=False
    )

    status = Column(
        Enum(
            "active",
            "inactive"
        ),
        default="active"
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    student = relationship(
        "Student",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    lecturer = relationship(
        "Lecturer",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    hod = relationship(
        "HOD",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )


class Student(Base):

    __tablename__ = "students"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        unique=True,
        nullable=False
    )

    student_id = Column(
        String(50),
        unique=True,
        nullable=False
    )

    full_name = Column(
        String(150),
        nullable=False
    )

    roll_number = Column(
        String(50),
        unique=True,
        nullable=False
    )

    mobile = Column(
        String(20)
    )

    department = Column(
        String(100)
    )

    course = Column(
        String(100)
    )

    academic_group = Column(
        String(100)
    )

    current_year = Column(
        String(50)
    )

    semester = Column(
        String(50)
    )

    college_name = Column(
        String(200)
    )

    user = relationship(
        "User",
        back_populates="student"
    )


class Lecturer(Base):

    __tablename__ = "lecturers"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        unique=True,
        nullable=False
    )

    faculty_id = Column(
        String(50),
        unique=True,
        nullable=False
    )

    full_name = Column(
        String(150),
        nullable=False
    )

    mobile = Column(
        String(20)
    )

    department = Column(
        String(100)
    )

    designation = Column(
        String(100)
    )

    college_name = Column(
        String(200)
    )

    user = relationship(
        "User",
        back_populates="lecturer"
    )


class HOD(Base):

    __tablename__ = "hods"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        unique=True,
        nullable=False
    )

    hod_id = Column(
        String(50),
        unique=True,
        nullable=False
    )

    full_name = Column(
        String(150),
        nullable=False
    )

    mobile = Column(
        String(20)
    )

    department = Column(
        String(100)
    )

    college_name = Column(
        String(200)
    )

    user = relationship(
        "User",
        back_populates="hod"
    )
