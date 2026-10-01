import os
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DB_FILE = "fitbuddy.db"
DATABASE_URL = f"sqlite:///{DB_FILE}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, index=True)
    username = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    weight = Column(Integer, nullable=False)
    goal = Column(String, nullable=False)
    intensity = Column(String, nullable=False)

    plan = relationship("Plan", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.user_id"), unique=True, nullable=False)
    original_plan = Column(Text, nullable=False)
    updated_plan = Column(Text, nullable=True)
    nutrition_tip = Column(Text, nullable=True)

    user = relationship("User", back_populates="plan")


Base.metadata.create_all(bind=engine)


# Database Utility Functions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def save_user(db, user_id: str, username: str, age: int, weight: int, goal: str, intensity: str):
    user = db.query(User).filter(User.user_id == user_id).first()
    if user:
        user.username = username
        user.age = age
        user.weight = weight
        user.goal = goal
        user.intensity = intensity
    else:
        user = User(
            user_id=user_id,
            username=username,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )
        db.add(user)
    db.commit()
    db.refresh(user)
    return user


def save_plan(db, user_id: str, original_plan: str, nutrition_tip: str):
    plan = db.query(Plan).filter(Plan.user_id == user_id).first()
    if plan:
        plan.original_plan = original_plan
        plan.nutrition_tip = nutrition_tip
    else:
        plan = Plan(
            user_id=user_id,
            original_plan=original_plan,
            nutrition_tip=nutrition_tip,
        )
        db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def update_plan(db, user_id: str, updated_plan_text: str, new_nutrition_tip: str = None):
    plan = db.query(Plan).filter(Plan.user_id == user_id).first()
    if plan:
        plan.updated_plan = updated_plan_text
        if new_nutrition_tip:
            plan.nutrition_tip = new_nutrition_tip
        db.commit()
        db.refresh(plan)
    return plan


def get_user(db, user_id: str):
    return db.query(User).filter(User.user_id == user_id).first()


def get_original_plan(db, user_id: str):
    plan = db.query(Plan).filter(Plan.user_id == user_id).first()
    return plan.original_plan if plan else None


def get_all_users(db):
    return db.query(User).all()


def get_all_plans(db):
    return db.query(Plan).all()


def delete_user(db, user_id: str):
    user = db.query(User).filter(User.user_id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return True
    return False
