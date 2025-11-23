from sqlalchemy.orm import Session
from .db_models import UserDB
from .models import UserCreate, UserUpdate


def create_user(db: Session, user: UserCreate):
    new_user = UserDB(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        phone=user.phone,
        address=user.address,
        city=user.city,
        state=user.state,
        zip_code=user.zip_code,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_users(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    city: str = None,
    state: str = None,
    status: str = None
):
    query = db.query(UserDB)

    # Filtering logic
    if city:
        query = query.filter(UserDB.city == city)
    if state:
        query = query.filter(UserDB.state == state)
    if status:
        query = query.filter(UserDB.status == status)

    # Pagination
    return query.offset(skip).limit(limit).all()


def update_user(db: Session, user_id: int, user_update: UserUpdate):
    db_user = db.query(UserDB).filter(UserDB.user_id == user_id).first()

    if not db_user:
        return None

    # Only update fields the client provided
    update_data = user_update.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user
def delete_user(db: Session, user_id: int):
    db_user = db.query(UserDB).filter(UserDB.user_id == user_id).first()
    if not db_user:
        return False

    db.delete(db_user)
    db.commit()
    return True


