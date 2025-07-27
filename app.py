import streamlit as st
from auth import login, logout, is_logged_in
from database import get_db
from models import Employee, Department, Attendance, LeaveRequest, Salary
from sqlalchemy.orm import sessionmaker
import pandas as pd
from datetime import datetime, date
from utils import calculate_net_salary
import plotly.express as px

st.set_page_config(
    page_title="نظام إدارة الموارد البشرية",
    layout="wide",
    initial_sidebar_state="expanded"
)

# RTL CSS
st.markdown(
    """
    <style>
        body {
            direction: rtl;
            text-align: right;
            font-family: 'Arial', sans-serif;
        }
        .css-1v0mbdj {
            direction: rtl !important;
        }
        table {
            text-align: right;
        }
        .stDataFrame {
            direction: rtl;
        }
        .stSelectbox, .stTextInput, .stDateInput {
            text-align: right;
        }
    </style>
    """,
    unsafe_allow_html=True
)

if not is_logged_in():
    login()
else:
    # Sidebar
    st.sidebar.title(f"مرحبًا {st.session_state.get('username', 'مستخدم')}")
    st.sidebar.markdown("---")
    
    menu = ["لوحة التحكم", "إدارة الموظفين", "تتبع الحضور", "طلبات الإجازة", "الرواتب"]
    choice = st.sidebar.selectbox("القائمة", menu)

    if choice == "لوحة التحكم":
        st.subheader("📊 لوحة التحكم")
        db = next(get_db())
        
        # Get statistics
        emp_count = db.query(Employee).count()
        att_today = db.query(Attendance).filter(Attendance.date == date.today()).count()
        leaves_pending = db.query(LeaveRequest).filter(LeaveRequest.status == "بانتظار الموافقة").count()
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("عدد الموظفين", emp_count)
        col2.metric("الحضور اليومي", att_today)
        col3.metric("الإجازات المعلقة", leaves_pending)
        
        # Charts
        st.markdown("---")
        st.subheader("📈 الإحصائيات")
        
        # Employees by department (dummy data for now)
        dept_data = pd.DataFrame({
            "القسم": ["تكنولوجيا المعلومات", "الموارد البشرية", "المالية", "التسويق"],
            "عدد الموظفين": [15, 8, 6, 12]
        })
        fig1 = px.pie(dept_data, values="عدد الموظفين", names="القسم", title="توزيع الموظفين حسب الأقسام")
        st.plotly_chart(fig1, use_container_width=True)

    elif choice == "إدارة الموظفين":
        st.subheader("👥 إدارة الموظفين")
        db = next(get_db())
        
        tab1, tab2 = st.tabs(["عرض الموظفين", "إضافة موظف"])
        
        with tab1:
            employees = db.query(Employee).all()
            if employees:
                df = pd.DataFrame([{
                    "الاسم الكامل": e.full_name,
                    "رقم الهوية": e.employee_id,
                    "الوظيفة": e.job_title,
                    "القسم": e.department.name if e.department else "غير محدد",
                    "تاريخ التعيين": e.hire_date,
                    "الراتب": e.salary
                } for e in employees])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("لا توجد بيانات موظفين")
        
        with tab2:
            with st.form("add_employee"):
                st.subheader("إضافة موظف جديد")
                full_name = st.text_input("الاسم الكامل")
                employee_id = st.text_input("رقم الهوية")
                job_title = st.text_input("الوظيفة")
                hire_date = st.date_input("تاريخ التعيين", value=date.today())
                salary = st.number_input("الراتب", min_value=0.0, step=100.0)
                
                submitted = st.form_submit_button("إضافة موظف")
                if submitted:
                    if full_name and employee_id:
                        new_employee = Employee(
                            full_name=full_name,
                            employee_id=employee_id,
                            job_title=job_title,
                            hire_date=hire_date,
                            salary=salary
                        )
                        db.add(new_employee)
                        db.commit()
                        st.success("تمت إضافة الموظف بنجاح!")
                        st.rerun()
                    else:
                        st.error("يرجى ملء جميع الحقول المطلوبة")

    elif choice == "تتبع الحضور":
        st.subheader("📅 تتبع الحضور")
        db = next(get_db())
        
        tab1, tab2 = st.tabs(["تسجيل الحضور", "تقارير الحضور"])
        
        with tab1:
            with st.form("attendance_form"):
                st.subheader("تسجيل حضور يدوي")
                
                # Get employees
                employees = db.query(Employee).all()
                if employees:
                    emp_names = [f"{e.full_name} ({e.employee_id})" for e in employees]
                    selected_emp = st.selectbox("اختر موظفًا", emp_names)
                    
                    att_date = st.date_input("التاريخ", value=date.today())
                    status = st.radio("الحالة", ["حاضر", "غائب"])
                    
                    submitted = st.form_submit_button("تسجيل الحضور")
                    if submitted and selected_emp:
                        emp_id = selected_emp.split("(")[1].split(")")[0]
                        new_attendance = Attendance(
                            employee_id=emp_id,
                            date=att_date,
                            status=status
                        )
                        db.add(new_attendance)
                        db.commit()
                        st.success("تم تسجيل الحضور بنجاح!")
                else:
                    st.warning("لا توجد موظفين مسجلين")
        
        with tab2:
            st.subheader("تقارير الحضور")
            attendances = db.query(Attendance).all()
            if attendances:
                df = pd.DataFrame([{
                    "رقم الهوية": a.employee_id,
                    "التاريخ": a.date,
                    "الحالة": a.status
                } for a in attendances])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("لا توجد بيانات حضور")

    elif choice == "طلبات الإجازة":
        st.subheader("📝 طلبات الإجازة")
        db = next(get_db())
        
        tab1, tab2 = st.tabs(["تقديم طلب", "إدارة الطلبات"])
        
        with tab1:
            with st.form("leave_request"):
                st.subheader("تقديم طلب إجازة")
                employee_id = st.session_state.get("employee_id", "EMP001")
                leave_type = st.selectbox("نوع الإجازة", ["إجازة سنوية", "إجازة مرضية", "إجازة بدون راتب"])
                start_date = st.date_input("تاريخ البدء")
                end_date = st.date_input("تاريخ الانتهاء")
                
                # Calculate days
                if start_date and end_date:
                    days = (end_date - start_date).days + 1
                    st.info(f"عدد الأيام: {days}")
                
                reason = st.text_area("السبب")
                
                submitted = st.form_submit_button("إرسال الطلب")
                if submitted:
                    new_leave = LeaveRequest(
                        employee_id=employee_id,
                        leave_type=leave_type,
                        start_date=start_date,
                        end_date=end_date,
                        days=days,
                        status="بانتظار الموافقة"
                    )
                    db.add(new_leave)
                    db.commit()
                    st.success("تم إرسال طلب الإجازة بنجاح!")
                    st.balloons()
        
        with tab2:
            st.subheader("إدارة طلبات الإجازة")
            leaves = db.query(LeaveRequest).all()
            if leaves:
                df = pd.DataFrame([{
                    "رقم الهوية": l.employee_id,
                    "نوع الإجازة": l.leave_type,
                    "من": l.start_date,
                    "إلى": l.end_date,
                    "عدد الأيام": l.days,
                    "الحالة": l.status
                } for l in leaves])
                st.dataframe(df, use_container_width=True)
                
                # Approval section
                st.markdown("---")
                st.subheader("الموافقة على الطلبات")
                
                pending_leaves = [l for l in leaves if l.status == "بانتظار الموافقة"]
                if pending_leaves:
                    leave_options = [f"{l.employee_id} - {l.leave_type} ({l.start_date} إلى {l.end_date})" for l in pending_leaves]
                    selected_leave = st.selectbox("اختر طلبًا للموافقة", leave_options)
                    
                    if selected_leave:
                        leave_id = pending_leaves[leave_options.index(selected_leave)].id
                        leave_request = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✅ الموافقة"):
                                leave_request.status = "موافق"
                                db.commit()
                                st.success("تمت الموافقة على الطلب!")
                                st.rerun()
                        with col2:
                            if st.button("❌ رفض"):
                                leave_request.status = "مرفوض"
                                db.commit()
                                st.success("تم رفض الطلب!")
                                st.rerun()
                else:
                    st.info("لا توجد طلبات معلقة")
            else:
                st.info("لا توجد طلبات إجازة")

    elif choice == "الرواتب":
        st.subheader("💰 إدارة الرواتب")
        db = next(get_db())
        
        tab1, tab2 = st.tabs(["عرض الرواتب", "حساب الرواتب"])
        
        with tab1:
            salaries = db.query(Salary).all()
            if salaries:
                df = pd.DataFrame([{
                    "رقم الهوية": s.employee_id,
                    "الشهر": s.month,
                    "الراتب الأساسي": s.basic_salary,
                    "الخصومات": s.deductions,
                    "صافي الراتب": s.net_salary
                } for s in salaries])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("لا توجد بيانات رواتب")
        
        with tab2:
            with st.form("salary_calculation"):
                st.subheader("حساب الراتب الشهري")
                
                # Get employees
                employees = db.query(Employee).all()
                if employees:
                    emp_names = [f"{e.full_name} ({e.employee_id})" for e in employees]
                    selected_emp = st.selectbox("اختر موظفًا", emp_names)
                    
                    month = st.selectbox("الشهر", [
                        "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
                        "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"
                    ])
                    
                    if selected_emp:
                        emp_id = selected_emp.split("(")[1].split(")")[0]
                        employee = db.query(Employee).filter(Employee.employee_id == emp_id).first()
                        basic_salary = st.number_input("الراتب الأساسي", value=float(employee.salary) if employee.salary else 0.0)
                    
                    deductions = st.number_input("الخصومات", min_value=0.0, step=100.0)
                    
                    net_salary = calculate_net_salary(basic_salary, deductions)
                    st.info(f"صافي الراتب: {net_salary}")
                    
                    submitted = st.form_submit_button("حفظ الراتب")
                    if submitted:
                        new_salary = Salary(
                            employee_id=emp_id,
                            month=month,
                            basic_salary=basic_salary,
                            deductions=deductions,
                            net_salary=net_salary
                        )
                        db.add(new_salary)
                        db.commit()
                        st.success("تم حفظ الراتب بنجاح!")
                else:
                    st.warning("لا توجد موظفين مسجلين")

    # Logout button
    if st.sidebar.button("تسجيل الخروج", type="secondary"):
        logout()