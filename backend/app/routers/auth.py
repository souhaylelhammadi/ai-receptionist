from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.company import Company
from app.models.user import User, UserRole
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    # Vérifie que l'email n'est pas déjà utilisé
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Cet email est déjà utilisé.")

    # Crée l'entreprise
    company = Company(name=payload.company_name, email=payload.email)
    db.add(company)
    db.flush()  # permet d'obtenir company.id avant le commit final

    # Crée le premier utilisateur, propriétaire (OWNER) de l'entreprise
    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=UserRole.OWNER,
        company_id=company.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({
        "sub": str(user.id),
        "company_id": str(user.company_id),
        "role": user.role.value,
    })
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect.")

    token = create_access_token({
        "sub": str(user.id),
        "company_id": str(user.company_id),
        "role": user.role.value,
    })
    return TokenResponse(access_token=token)