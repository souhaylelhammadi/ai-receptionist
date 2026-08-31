import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse
from app.core.deps import get_current_user

router = APIRouter(prefix="/customers", tags=["customers"])


def get_customer_or_404(customer_id: uuid.UUID, current_user: User, db: Session) -> Customer:
    """
    Va chercher un customer par id, MAIS uniquement s'il appartient à la même
    entreprise que l'utilisateur connecté. Sinon, renvoie 404 (pas 403 !) pour
    ne même pas révéler que le customer existe dans une autre entreprise.
    """
    customer = (
        db.query(Customer)
        .filter(Customer.id == customer_id, Customer.company_id == current_user.company_id)
        .first()
    )
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client introuvable.")
    return customer


@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(
    payload: CustomerCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    customer = Customer(**payload.model_dump(), company_id=current_user.company_id)
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@router.get("", response_model=list[CustomerResponse])
def list_customers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Customer)
        .filter(Customer.company_id == current_user.company_id)
        .order_by(Customer.created_at.desc())
        .all()
    )


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_customer_or_404(customer_id, current_user, db)


@router.patch("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: uuid.UUID,
    payload: CustomerUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    customer = get_customer_or_404(customer_id, current_user, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)
    db.commit()
    db.refresh(customer)
    return customer


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(
    customer_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    customer = get_customer_or_404(customer_id, current_user, db)
    db.delete(customer)
    db.commit()
    return None