# seed_data.py

from database import get_db, Base, engine
from models import Employee, Department, Attendance, LeaveRequest, Salary
from datetime import date, datetime, timedelta
import random

def create_sample_data():
    """Function to add sample data to the database"""
    # Get a database session
    db = next(get_db())

    try:
        # --- Check if departments already exist ---
        existing_depts = db.query(Department).all()
        if existing_depts:
            print("Departments already exist. Skipping department creation.")
            # Map existing department names to IDs
            dept_map = {dept.name: dept.id for dept in existing_depts}
        else:
            print("Adding departments...")
            dept_it = Department(name="تكنولوجيا المعلومات", description="قسم تكنولوجيا المعلومات")
            dept_hr = Department(name="الموارد البشرية", description="قسم الموارد البشرية")
            dept_fin = Department(name="المالية", description="قسم الشؤون المالية")
            dept_mkt = Department(name="التسويق", description="قسم التسويق")

            db.add_all([dept_it, dept_hr, dept_fin, dept_mkt])
            db.commit() # Commit to get IDs for relationships
            print("Departments added.")
            # Map new department names to IDs
            dept_map = {
                "تكنولوجيا المعلومات": dept_it.id,
                "الموارد البشرية": dept_hr.id,
                "المالية": dept_fin.id,
                "التسويق": dept_mkt.id
            }

        # --- Check if employees already exist ---
        existing_emps = db.query(Employee).all()
        if existing_emps:
            print("Employees already exist. Skipping employee creation.")
            employees_data = [(emp.full_name, emp.employee_id, emp.job_title, emp.department_id, emp.hire_date, emp.salary) for emp in existing_emps]
        else:
            print("Adding employees...")
            employees_data = [
                ("أحمد محمد", "EMP001", "مدير تقنية المعلومات", dept_map["تكنولوجيا المعلومات"], date(2022, 1, 15), 10000),
                ("فاطمة علي", "EMP002", "محلل موارد بشرية", dept_map["الموارد البشرية"], date(2023, 3, 10), 7000),
                ("محمد سعيد", "EMP003", "محاسب", dept_map["المالية"], date(2021, 6, 1), 6500),
                ("سارة خالد", "EMP004", "مديرة تسويق", dept_map["التسويق"], date(2022, 11, 20), 8500),
                ("عمر ناصر", "EMP005", "مطور برمجيات", dept_map["تكنولوجيا المعلومات"], date(2023, 8, 5), 7500),
                ("نورا عبدالله", "EMP006", "مساعد إداري", dept_map["الموارد البشرية"], date(2024, 1, 1), 5000),
            ]

            for emp_data in employees_data:
                emp = Employee(
                    full_name=emp_data[0],
                    employee_id=emp_data[1],
                    job_title=emp_data[2],
                    department_id=emp_data[3],
                    hire_date=emp_data[4],
                    salary=emp_data[5]
                )
                db.add(emp)
            db.commit()
            print(f"{len(employees_data)} Employees added.")

        # --- Add Attendance Records (for last 7 days) ---
        # Only add if no attendance records exist for the last 7 days
        today = date.today()
        last_week_start = today - timedelta(days=6) # Last 7 days including today
        existing_att_count = db.query(Attendance).filter(
            Attendance.date >= last_week_start,
            Attendance.date <= today
        ).count()

        if existing_att_count > 0:
            print(f"Attendance records for the last 7 days already exist ({existing_att_count} records found). Skipping attendance creation.")
        else:
            print("Adding attendance records...")
            for i in range(7): # Last 7 days
                record_date = today - timedelta(days=i)
                for emp_id in [e[1] for e in employees_data]: # For each employee
                    # Randomly assign present/absent (70% chance of being present)
                    status = "حاضر" if random.random() < 0.7 else "غائب"
                    attendance = Attendance(
                        employee_id=emp_id,
                        date=record_date,
                        status=status
                    )
                    db.add(attendance)
            db.commit()
            print("Attendance records added.")

        # --- Add Leave Requests ---
        existing_leaves = db.query(LeaveRequest).all()
        if existing_leaves:
            print(f"Leave requests already exist ({len(existing_leaves)} found). Skipping leave request creation.")
        else:
            print("Adding leave requests...")
            leave_types = ["إجازة سنوية", "إجازة مرضية", "إجازة بدون راتب"]
            
            # Use timedelta for safer date calculations
            today = date.today()
            # Some pending, some approved, some rejected
            leave_requests_data = [
                ("EMP001", random.choice(leave_types), today, today + timedelta(days=5), 5, "بانتظار الموافقة"),
                ("EMP002", random.choice(leave_types), today - timedelta(days=30), (today - timedelta(days=30)) + timedelta(days=3), 3, "موافق"),
                ("EMP003", random.choice(leave_types), today + timedelta(days=10), (today + timedelta(days=10)) + timedelta(days=4), 4, "مرفوض"),
                ("EMP004", random.choice(leave_types), today + timedelta(days=1), (today + timedelta(days=1)) + timedelta(days=2), 2, "بانتظار الموافقة"),
            ]

            for req_data in leave_requests_data:
                req = LeaveRequest(
                    employee_id=req_data[0],
                    leave_type=req_data[1],
                    start_date=req_data[2],
                    end_date=req_data[3],
                    days=req_data[4],
                    status=req_data[5]
                )
                db.add(req)
            db.commit()
            print(f"{len(leave_requests_data)} Leave requests added.")

        # --- Add Salaries ---
        # Check if salary records for current month already exist
        current_month = date.today().month
        current_year = date.today().year
        months = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
        current_month_name = months[current_month - 1]

        existing_salaries = db.query(Salary).filter(Salary.month == current_month_name).limit(1).first()
        if existing_salaries:
            print(f"Salary records for {current_month_name} already exist. Skipping salary creation for this month.")
        else:
            print("Adding salary records...")
            # Add salary for current month for all employees
            for emp_id in [e[1] for e in employees_data]:
                # Find employee to get base salary
                emp = db.query(Employee).filter(Employee.employee_id == emp_id).first()
                base_salary = emp.salary if emp else 5000 # Fallback
                deductions = round(random.uniform(200, 800), 2) # Random deductions
                net_salary = base_salary - deductions

                salary = Salary(
                    employee_id=emp_id,
                    month=current_month_name,
                    basic_salary=base_salary,
                    deductions=deductions,
                    net_salary=net_salary
                )
                db.add(salary)
            db.commit()
            print(f"Salary records added for {len(employees_data)} employees for {current_month_name}.")

        print("\nSample data successfully added (or confirmed to exist) in the database!")

    except Exception as e:
        print(f"An error occurred while adding sample data: {e}")
        import traceback
        traceback.print_exc() # Print detailed traceback
        db.rollback() # Rollback in case of error
    finally:
        db.close() # Close the session


if __name__ == "__main__":
    create_sample_data()