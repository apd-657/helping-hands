# routers/users.py
# All API routes related to user management

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models, schemas, auth

router = APIRouter(prefix="/api/users", tags=["Users"])


# ─────────────────────────────────────────────
# POST /api/users/register
# Creates a new user account (elder or volunteer)
# ─────────────────────────────────────────────
@router.post("/register", response_model=schemas.Token, status_code=201)
def register(user_data: schemas.UserRegister, db: Session = Depends(get_db)):
    # Check if email is already taken
    existing = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Validate role
    if user_data.role not in ["elder", "volunteer"]:
        raise HTTPException(status_code=400, detail="Role must be 'elder' or 'volunteer'")

    # Create new user with hashed password
    new_user = models.User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=auth.hash_password(user_data.password),
        age=user_data.age,
        role=user_data.role,
        contact=user_data.contact,
        location=user_data.location,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Return a token immediately so user is logged in after registration
    token = auth.create_access_token({"sub": str(new_user.id)})  # JWT sub must be a string
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": new_user.id,
        "name": new_user.name,
        "role": new_user.role,
    }


# ─────────────────────────────────────────────
# POST /api/users/login
# Logs in an existing user, returns JWT token
# ─────────────────────────────────────────────
@router.post("/login", response_model=schemas.Token)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    # Find user by email
    user = db.query(models.User).filter(models.User.email == credentials.email).first()

    # Verify email and password
    if not user or not auth.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    token = auth.create_access_token({"sub": str(user.id)})  # JWT sub must be a string
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "name": user.name,
        "role": user.role,
    }


# ─────────────────────────────────────────────
# GET /api/users/me
# Returns the profile of the logged-in user
# ─────────────────────────────────────────────
@router.get("/me", response_model=schemas.UserOut)
def get_my_profile(current_user: models.User = Depends(auth.get_current_user)):
    return current_user


# ─────────────────────────────────────────────
# GET /api/users/volunteers
# Lists all volunteers (useful for admin/display)
# ─────────────────────────────────────────────
@router.get("/volunteers", response_model=list[schemas.UserOut])
def list_volunteers(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return db.query(models.User).filter(models.User.role == "volunteer").all()
