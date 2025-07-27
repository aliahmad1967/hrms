import streamlit as st

def login():
    st.markdown('<style>body {direction: rtl;}</style>', unsafe_allow_html=True)
    st.title("نظام إدارة الموارد البشرية")
    st.subheader("تسجيل الدخول")
    
    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("دخول"):
            if username == "admin" and password == "admin123":
                st.session_state["role"] = "مدير"
                st.session_state["username"] = "مدير النظام"
                st.success("مرحبًا مدير النظام!")
                st.rerun()
            elif username == "employee" and password == "emp123":
                st.session_state["role"] = "موظف"
                st.session_state["username"] = "موظف"
                st.session_state["employee_id"] = "EMP001"
                st.success("مرحبًا موظف!")
                st.rerun()
            else:
                st.error("بيانات الدخول غير صحيحة")
    
    with col2:
        if st.button("نسيت كلمة المرور؟"):
            st.info("يرجى التواصل مع قسم الموارد البشرية")

def logout():
    st.session_state.clear()
    st.rerun()

def is_logged_in():
    return "role" in st.session_state

def require_role(required_role):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if st.session_state.get("role") == required_role:
                return func(*args, **kwargs)
            else:
                st.warning("ليس لديك صلاحية الوصول إلى هذه الصفحة")
                return None
        return wrapper
    return decorator