import streamlit as st

def require_login():
    """Hàm kiểm tra xác thực và quản lý Sidebar"""
    
    # Khởi tạo trạng thái
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    # Trường hợp CHƯA đăng nhập -> Hiện màn hình Login & Ẩn Sidebar
    if not st.session_state["password_correct"]:
        # CSS ẩn Sidebar hoàn toàn
        st.markdown(
            """
            <style>
                [data-testid="stSidebar"] {display: none;}
            </style>
            """,
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.write("")
            st.write("")
            st.title("🔒 YKK AP System Login")
            st.caption("Vui lòng đăng nhập để truy cập Báo cáo Sales & S&OP")
            st.markdown("---")

            username = st.text_input("Tên đăng nhập")
            password = st.text_input("Mật khẩu", type="password")

            if st.button("🚀 Đăng nhập", use_container_width=True):
                if username == "admin" and password == "Ykk@2026":
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.error("❌ Tài khoản hoặc mật khẩu không đúng!")
        
        st.stop()  # Khóa toàn bộ các đoạn code phía dưới

    # Trường hợp ĐÃ đăng nhập -> Hiện nút Đăng xuất trên Sidebar
    with st.sidebar:
        st.markdown("### 👤 Tài khoản: **Admin**")
        if st.button("🚪 Đăng xuất", use_container_width=True):
            st.session_state["password_correct"] = False
            st.rerun()
        st.markdown("---")