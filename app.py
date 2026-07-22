import streamlit as st
from auth import login, logout, is_logged_in
from database import get_db
from models import Employee, Department, Attendance, LeaveRequest, Salary
from sqlalchemy.orm import sessionmaker
import pandas as pd
from datetime import datetime, date
from utils import calculate_net_salary
import plotly.express as px
import plotly.graph_objects as go

# Set page config WITH THEME OPTIONS
st.set_page_config(
    page_title="نظام إدارة الموارد البشرية",
    layout="wide",
    initial_sidebar_state="expanded",
    # Add theme configuration
    menu_items={
        'Get Help': 'https://github.com/your_username/hrms',
        'Report a bug': "https://github.com/your_username/hrms/issues",
        'About': "# نظام إدارة الموارد البشرية\nBuilt with Streamlit and SQLAlchemy."
    }
)

# --- Theme-Specific CSS ---
# This CSS adapts based on Streamlit's light/dark theme
st.markdown(
    """
    <style>
        /* General Body Styling - Adapts to theme */
        body {
            direction: rtl;
            text-align: right;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            /* Colors adapt based on theme */
            background-color: var(--theme-bg-color);
            color: var(--theme-text-color);
        }

        /* Main Container */
        .main {
            background-color: var(--theme-card-bg);
            border-radius: 10px;
            box-shadow: 0 4px 6px var(--theme-shadow-color);
            padding: 2rem;
            margin-top: 1rem;
        }

        /* Sidebar Styling */
        .css-1d391kg {
            background-color: var(--theme-sidebar-bg);
            color: var(--theme-sidebar-text);
            border-radius: 10px;
            padding: 1rem;
        }
        .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3, .css-1d391kg h4, .css-1d391kg h5, .css-1d391kg h6 {
            color: var(--theme-sidebar-text);
        }
        .css-ffhzg2 { /* Sidebar header */
            background-color: var(--theme-sidebar-bg);
        }

        /* Headers */
        h1, h2, h3, h4, h5, h6 {
            color: var(--theme-header-color);
            font-weight: 600;
        }

        /* Buttons */
        .stButton>button {
            background-color: var(--theme-primary-btn-bg);
            color: var(--theme-primary-btn-text);
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s ease, transform 0.1s ease;
        }
        .stButton>button:hover {
            background-color: var(--theme-primary-btn-hover-bg);
            transform: translateY(-2px); /* Subtle lift on hover */
        }
        .stButton>button:active {
            transform: scale(0.98);
        }
        /* Secondary Button */
        .stButton>button[type="secondary"] {
            background-color: var(--theme-secondary-btn-bg);
            color: var(--theme-secondary-btn-text);
        }
        .stButton>button[type="secondary"]:hover {
            background-color: var(--theme-secondary-btn-hover-bg);
        }

        /* Input Fields */
        .stTextInput>div>div>input, 
        .stSelectbox>div>div>select, 
        .stDateInput>div>div>input {
            border: 1px solid var(--theme-input-border);
            border-radius: 5px;
            padding: 0.5rem;
            background-color: var(--theme-input-bg);
            color: var(--theme-input-text);
        }
        .stTextInput>div>div>input:focus, 
        .stSelectbox>div>div>select:focus, 
        .stDateInput>div>div>input:focus {
             border-color: var(--theme-primary-accent);
             box-shadow: 0 0 0 2px var(--theme-primary-accent-light); /* Focus ring */
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
            background-color: var(--theme-tab-bar-bg);
            padding: 0.5rem;
            border-radius: 8px 8px 0 0;
        }
        .stTabs [data-baseweb="tab"] {
            height: 40px;
            border-radius: 5px 5px 0 0;
            background-color: var(--theme-tab-inactive-bg);
            color: var(--theme-tab-inactive-text);
        }
        .stTabs [data-baseweb="tab"]:hover {
            background-color: var(--theme-tab-hover-bg);
        }
        .stTabs [aria-selected="true"] {
            background-color: var(--theme-tab-active-bg);
            color: var(--theme-tab-active-text);
        }

        /* DataFrames */
        .stDataFrame {
            border: 1px solid var(--theme-table-border);
            border-radius: 5px;
            overflow: auto;
            background-color: var(--theme-table-bg);
        }
        /* DataFrame Header */
        .stDataFrame th {
            background-color: var(--theme-table-header-bg);
            color: var(--theme-table-header-text);
            font-weight: bold;
        }
        /* DataFrame Cells */
        .stDataFrame td {
            color: var(--theme-table-cell-text);
        }

        /* Cards/Metrics */
        .css-1v0mbdj {
            direction: rtl !important;
            text-align: right;
        }
        .stMetric {
            background-color: var(--theme-metric-bg);
            padding: 1rem;
            border-radius: 5px;
            border: 1px solid var(--theme-metric-border);
            box-shadow: 0 2px 4px var(--theme-shadow-color);
        }
        .stMetric .metric-value {
            font-size: 1.5rem;
            font-weight: bold;
            color: var(--theme-metric-value-color);
        }
        .stMetric .metric-label {
            color: var(--theme-metric-label-color);
        }

        /* Alerts */
        .stAlert {
            border-radius: 5px;
            background-color: var(--theme-alert-bg);
            color: var(--theme-alert-text);
            border: 1px solid var(--theme-alert-border);
        }

        /* Footer */
        footer {
            visibility: hidden;
        }

        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-track {
            background: var(--theme-scrollbar-track);
        }
        ::-webkit-scrollbar-thumb {
            background: var(--theme-scrollbar-thumb);
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: var(--theme-scrollbar-thumb-hover);
        }

        /* Custom Card Style for Dashboard Metrics */
        .custom-metric-card {
            padding: 1rem;
            border-radius: 5px;
            border-left: 5px solid var(--theme-card-border-highlight);
            background-color: var(--theme-card-bg-light);
            color: var(--theme-card-text);
            margin-bottom: 1rem;
        }
        .custom-metric-card h4 {
            margin: 0 0 0.5rem 0;
            color: var(--theme-card-subheader);
        }
        .custom-metric-card p {
            font-size: 1.5rem;
            font-weight: bold;
            margin: 0;
            color: var(--theme-card-value);
        }

    </style>

    <!-- Define CSS variables based on Streamlit's theme -->
    <script>
        // Function to get Streamlit theme properties (requires Streamlit JS API)
        function applyTheme() {
            const root = document.documentElement;

            // Get Streamlit theme variables (these are injected by Streamlit)
            // They might be available on window or through Streamlit's JS API
            // For now, we'll define them based on common Streamlit theme structures
            // This is a simplified version - full implementation might need Streamlit's JS SDK
            
            // Assume a default light theme if not explicitly set
            let isDark = window.getComputedStyle(document.body).backgroundColor === 'rgb(10, 10, 10)'; // Very basic check
            // A more robust way is to listen to theme changes via Streamlit events or use session state if possible
            
            // Define CSS variables based on assumed theme
            if (isDark) {
                root.style.setProperty('--theme-bg-color', '#1f1f1f');
                root.style.setProperty('--theme-text-color', '#f0f0f0');
                root.style.setProperty('--theme-card-bg', '#2d2d2d');
                root.style.setProperty('--theme-shadow-color', 'rgba(255, 255, 255, 0.1)');
                root.style.setProperty('--theme-sidebar-bg', '#262730');
                root.style.setProperty('--theme-sidebar-text', '#fafafa');
                root.style.setProperty('--theme-header-color', '#ffffff');
                root.style.setProperty('--theme-primary-btn-bg', '#0068c9');
                root.style.setProperty('--theme-primary-btn-text', '#ffffff');
                root.style.setProperty('--theme-primary-btn-hover-bg', '#0054a3');
                root.style.setProperty('--theme-secondary-btn-bg', '#d30c0c');
                root.style.setProperty('--theme-secondary-btn-text', '#ffffff');
                root.style.setProperty('--theme-secondary-btn-hover-bg', '#a80a0a');
                root.style.setProperty('--theme-input-bg', '#31333f');
                root.style.setProperty('--theme-input-text', '#ffffff');
                root.style.setProperty('--theme-input-border', '#4a4d57');
                root.style.setProperty('--theme-primary-accent', '#808495');
                root.style.setProperty('--theme-primary-accent-light', 'rgba(0, 104, 201, 0.2)');
                root.style.setProperty('--theme-tab-bar-bg', '#262730');
                root.style.setProperty('--theme-tab-inactive-bg', '#31333f');
                root.style.setProperty('--theme-tab-inactive-text', '#e0e0e0');
                root.style.setProperty('--theme-tab-hover-bg', '#3a3d4a');
                root.style.setProperty('--theme-tab-active-bg', '#0068c9');
                root.style.setProperty('--theme-tab-active-text', '#ffffff');
                root.style.setProperty('--theme-table-bg', '#2d2d2d');
                root.style.setProperty('--theme-table-border', '#4a4d57');
                root.style.setProperty('--theme-table-header-bg', '#3a3d4a');
                root.style.setProperty('--theme-table-header-text', '#ffffff');
                root.style.setProperty('--theme-table-cell-text', '#e0e0e0');
                root.style.setProperty('--theme-metric-bg', '#2d2d2d');
                root.style.setProperty('--theme-metric-border', '#4a4d57');
                root.style.setProperty('--theme-metric-value-color', '#ffffff');
                root.style.setProperty('--theme-metric-label-color', '#bfbfbf');
                root.style.setProperty('--theme-alert-bg', '#3a3d4a');
                root.style.setProperty('--theme-alert-text', '#f0f0f0');
                root.style.setProperty('--theme-alert-border', '#808495');
                root.style.setProperty('--theme-scrollbar-track', '#2d2d2d');
                root.style.setProperty('--theme-scrollbar-thumb', '#4a4d57');
                root.style.setProperty('--theme-scrollbar-thumb-hover', '#63687b');
                root.style.setProperty('--theme-card-bg-light', '#3a3d4a');
                root.style.setProperty('--theme-card-text', '#f0f0f0');
                root.style.setProperty('--theme-card-subheader', '#bfbfbf');
                root.style.setProperty('--theme-card-value', '#ffffff');
                root.style.setProperty('--theme-card-border-highlight', '#0068c9');
            } else { // Light theme (default/fallback)
                root.style.setProperty('--theme-bg-color', '#f8f9fa');
                root.style.setProperty('--theme-text-color', '#262730');
                root.style.setProperty('--theme-card-bg', '#ffffff');
                root.style.setProperty('--theme-shadow-color', 'rgba(0, 0, 0, 0.1)');
                root.style.setProperty('--theme-sidebar-bg', '#2c3e50');
                root.style.setProperty('--theme-sidebar-text', '#ffffff');
                root.style.setProperty('--theme-header-color', '#2c3e50');
                root.style.setProperty('--theme-primary-btn-bg', '#3498db');
                root.style.setProperty('--theme-primary-btn-text', '#ffffff');
                root.style.setProperty('--theme-primary-btn-hover-bg', '#2980b9');
                root.style.setProperty('--theme-secondary-btn-bg', '#e74c3c');
                root.style.setProperty('--theme-secondary-btn-text', '#ffffff');
                root.style.setProperty('--theme-secondary-btn-hover-bg', '#c0392b');
                root.style.setProperty('--theme-input-bg', '#ffffff');
                root.style.setProperty('--theme-input-text', '#262730');
                root.style.setProperty('--theme-input-border', '#cccccc');
                root.style.setProperty('--theme-primary-accent', '#3498db');
                root.style.setProperty('--theme-primary-accent-light', 'rgba(52, 152, 219, 0.2)');
                root.style.setProperty('--theme-tab-bar-bg', '#e9ecef');
                root.style.setProperty('--theme-tab-inactive-bg', '#dee2e6');
                root.style.setProperty('--theme-tab-inactive-text', '#495057');
                root.style.setProperty('--theme-tab-hover-bg', '#ced4da');
                root.style.setProperty('--theme-tab-active-bg', '#3498db');
                root.style.setProperty('--theme-tab-active-text', '#ffffff');
                root.style.setProperty('--theme-table-bg', '#ffffff');
                root.style.setProperty('--theme-table-border', '#dee2e6');
                root.style.setProperty('--theme-table-header-bg', '#e9ecef');
                root.style.setProperty('--theme-table-header-text', '#212529');
                root.style.setProperty('--theme-table-cell-text', '#212529');
                root.style.setProperty('--theme-metric-bg', '#f8f9fa');
                root.style.setProperty('--theme-metric-border', '#dee2e6');
                root.style.setProperty('--theme-metric-value-color', '#2c3e50');
                root.style.setProperty('--theme-metric-label-color', '#6c757d');
                root.style.setProperty('--theme-alert-bg', '#e7f3fe');
                root.style.setProperty('--theme-alert-text', '#084298');
                root.style.setProperty('--theme-alert-border', '#b6d4fe');
                root.style.setProperty('--theme-scrollbar-track', '#f1f1f1');
                root.style.setProperty('--theme-scrollbar-thumb', '#bdc3c7');
                root.style.setProperty('--theme-scrollbar-thumb-hover', '#95a5a6');
                root.style.setProperty('--theme-card-bg-light', '#eaf2f8');
                root.style.setProperty('--theme-card-text', '#2c3e50');
                root.style.setProperty('--theme-card-subheader', '#6c757d');
                root.style.setProperty('--theme-card-value', '#2c3e50');
                root.style.setProperty('--theme-card-border-highlight', '#3498db');
            }
        }

        // Call applyTheme on initial load
        applyTheme();

        // Listen for Streamlit's theme change event (if available in future versions or via custom JS)
        // window.addEventListener('streamlit:themeChange', applyTheme);

    </script>
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
        st.header("📊 لوحة التحكم")
        db = next(get_db())
        
        # Get statistics
        emp_count = db.query(Employee).count()
        att_today = db.query(Attendance).filter(Attendance.date == date.today()).count()
        leaves_pending = db.query(LeaveRequest).filter(LeaveRequest.status == "بانتظار الموافقة").count()
        
        # Display metrics in themed cards
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(
                f"""
                <div class="custom-metric-card">
                    <h4>عدد الموظفين</h4>
                    <p>{emp_count}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                f"""
                <div class="custom-metric-card">
                    <h4>الحضور اليومي</h4>
                    <p>{att_today}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col3:
            st.markdown(
                f"""
                <div class="custom-metric-card">
                    <h4>الإجازات المعلقة</h4>
                    <p>{leaves_pending}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        # Charts
        st.markdown("---")
        st.subheader("📈 الإحصائيات")
        
        # Employees by department (dummy data for now)
        dept_data = pd.DataFrame({
            "القسم": ["تكنولوجيا المعلومات", "الموارد البشرية", "المالية", "التسويق"],
            "عدد الموظفين": [15, 8, 6, 12]
        })
        fig1 = px.pie(dept_data, values="عدد الموظفين", names="القسم", title="توزيع الموظفين حسب الأقسام")
        fig1.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig1, use_container_width=True)

    elif choice == "إدارة الموظفين":
        st.header("👥 إدارة الموظفين")
        db = next(get_db())
        
        tab1, tab2, tab3 = st.tabs(["عرض الموظفين", "إضافة موظف", "تعديل/حذف"])
        
        with tab1:
            st.subheader("قائمة الموظفين")
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
                # Apply styling to dataframe
                st.dataframe(df.style.set_properties(**{'text-align': 'right'}), use_container_width=True)
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
                
                submitted = st.form_submit_button("➕ إضافة موظف")
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
                        st.success("✅ تمت إضافة الموظف بنجاح!")
                        st.rerun()
                    else:
                        st.error("❌ يرجى ملء جميع الحقول المطلوبة")
        
        with tab3:
            st.subheader("تعديل أو حذف موظف")
            employees = db.query(Employee).all()
            if employees:
                emp_names = [f"{e.full_name} ({e.employee_id})" for e in employees]
                selected_emp = st.selectbox("اختر موظفًا للتعديل", emp_names)
                
                if selected_emp:
                    emp_id = selected_emp.split("(")[1].split(")")[0]
                    employee = db.query(Employee).filter(Employee.employee_id == emp_id).first()
                    
                    if employee:
                        with st.form("edit_employee"):
                            full_name = st.text_input("الاسم الكامل", value=employee.full_name)
                            job_title = st.text_input("الوظيفة", value=employee.job_title)
                            hire_date = st.date_input("تاريخ التعيين", value=employee.hire_date)
                            salary = st.number_input("الراتب", min_value=0.0, step=100.0, value=float(employee.salary))
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                update_btn = st.form_submit_button("✏️ تحديث الموظف")
                            with col2:
                                delete_btn = st.form_submit_button("🗑️ حذف الموظف", type="secondary")
                            
                            if update_btn:
                                employee.full_name = full_name
                                employee.job_title = job_title
                                employee.hire_date = hire_date
                                employee.salary = salary
                                db.commit()
                                st.success("✅ تم تحديث بيانات الموظف بنجاح!")
                                st.rerun()
                            
                            if delete_btn:
                                db.delete(employee)
                                db.commit()
                                st.success("✅ تم حذف الموظف بنجاح!")
                                st.rerun()
            else:
                st.info("❌ لا توجد بيانات موظفين للتعديل")

    elif choice == "تتبع الحضور":
        st.header("📅 تتبع الحضور")
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
                    
                    submitted = st.form_submit_button("✅ تسجيل الحضور")
                    if submitted and selected_emp:
                        emp_id = selected_emp.split("(")[1].split(")")[0]
                        
                        # Check if already exists
                        existing = db.query(Attendance).filter(
                            Attendance.employee_id == emp_id,
                            Attendance.date == att_date
                        ).first()
                        
                        if existing:
                            st.warning("⚠️ هذا التسجيل موجود بالفعل!")
                        else:
                            new_attendance = Attendance(
                                employee_id=emp_id,
                                date=att_date,
                                status=status
                            )
                            db.add(new_attendance)
                            db.commit()
                            st.success("✅ تم تسجيل الحضور بنجاح!")
                else:
                    st.warning("⚠️ لا توجد موظفين مسجلين")
        
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
                st.info("❌ لا توجد بيانات حضور")

    elif choice == "طلبات الإجازة":
        st.header("📝 طلبات الإجازة")
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
                    st.info(f"🔢 عدد الأيام: {days}")
                
                reason = st.text_area("السبب")
                
                submitted = st.form_submit_button("📤 إرسال الطلب")
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
                    st.success("✅ تم إرسال طلب الإجازة بنجاح!")
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
                                st.success("✅ تمت الموافقة على الطلب!")
                                st.rerun()
                        with col2:
                            if st.button("❌ رفض"):
                                leave_request.status = "مرفوض"
                                db.commit()
                                st.success("❌ تم رفض الطلب!")
                                st.rerun()
                else:
                    st.info("❌ لا توجد طلبات معلقة")
            else:
                st.info("❌ لا توجد طلبات إجازة")

    elif choice == "الرواتب":
        st.header("💰 إدارة الرواتب")
        db = next(get_db())
        
        tab1, tab2 = st.tabs(["عرض الرواتب", "حساب الرواتب"])
        
        with tab1:
            st.subheader("قائمة الرواتب")
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
                st.info("❌ لا توجد بيانات رواتب")
        
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
                    st.info(f"🧮 صافي الراتب: {net_salary}")
                    
                    submitted = st.form_submit_button("💾 حفظ الراتب")
                    if submitted:
                        # Check if already exists
                        existing = db.query(Salary).filter(
                            Salary.employee_id == emp_id,
                            Salary.month == month
                        ).first()
                        
                        if existing:
                            st.warning("⚠️ هذا الراتب مسجل بالفعل!")
                        else:
                            new_salary = Salary(
                                employee_id=emp_id,
                                month=month,
                                basic_salary=basic_salary,
                                deductions=deductions,
                                net_salary=net_salary
                            )
                            db.add(new_salary)
                            db.commit()
                            st.success("✅ تم حفظ الراتب بنجاح!")
                else:
                    st.warning("⚠️ لا توجد موظفين مسجلين")

    # Logout button in sidebar
    if st.sidebar.button("🚪 تسجيل الخروج", type="secondary"):
        logout()