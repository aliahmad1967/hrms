from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Employee(Base):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    employee_id = Column(String, unique=True, index=True)
    job_title = Column(String)
    department_id = Column(Integer, ForeignKey('departments.id'), nullable=True)
    hire_date = Column(Date)
    salary = Column(Float)

    department = relationship("Department", back_populates="employees")

class Department(Base):
    __tablename__ = 'departments'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(String)

    employees = relationship("Employee", back_populates="department")

class Attendance(Base):
    __tablename__ = 'attendance'
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey('employees.employee_id'))
    date = Column(Date)
    status = Column(String)  # حاضر/غائب

class LeaveRequest(Base):
    __tablename__ = 'leave_requests'
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey('employees.employee_id'))
    leave_type = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    days = Column(Integer)
    status = Column(String, default="بانتظار الموافقة")  # بانتظار الموافقة / موافق / مرفوض

class Salary(Base):
    __tablename__ = 'salaries'
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey('employees.employee_id'))
    month = Column(String)
    basic_salary = Column(Float)
    deductions = Column(Float, default=0)
    net_salary = Column(Float)