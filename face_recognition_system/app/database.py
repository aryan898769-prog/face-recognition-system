import os
from sqlalchemy import create_engine, Column, Integer, String, Table, MetaData, select
from sqlalchemy.orm import registry, Session

DATABASE_URL = "sqlite:///employees.db"

mapper_registry = registry()
metadata = MetaData()

employees_table = Table(
    "employees",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("employee_id", String, unique=True, nullable=False),
    Column("name", String, nullable=False),
    Column("allowed_area", String, nullable=False),
)

class Employee:
    def __init__(self, employee_id: str, name: str, allowed_area: str):
        self.employee_id = employee_id
        self.name = name
        self.allowed_area = allowed_area

mapper_registry.map_imperatively(Employee, employees_table)

engine = create_engine(DATABASE_URL, echo=False, future=True)
metadata.create_all(engine)


def add_employee(employee_id: str, name: str, allowed_area: str):
    with Session(engine) as session:
        employee = Employee(employee_id=employee_id, name=name, allowed_area=allowed_area)
        session.add(employee)
        session.commit()
        return employee


def get_employee_by_id(employee_id: str):
    with Session(engine) as session:
        statement = select(Employee).where(employees_table.c.employee_id == employee_id)
        return session.scalar(statement)


def get_all_employees():
    with Session(engine) as session:
        statement = select(Employee)
        return session.scalars(statement).all()
