import streamlit as st

def require_login():
    """Hàm xử lý Đăng nhập & Tạo Sidebar Menu riêng"""
    
    # 1. Khởi tạo trạng thái
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    # 2. CHƯA ĐĂNG NHẬP -> Hiện Form Login & Ẩn Sidebar
    if not st.session_state["password_correct"]:
        # CSS ẩn Sidebar hoàn toàn
        st.markdown(
            """
            <style>
                [data-testid="stSidebar"] {display: none !important;}
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
        
        st.stop()

    # 3. ĐÃ ĐĂNG NHẬP -> HIỆN SIDEBAR NGHỆ THUẬT DO CHÚNG TA TỰ DỰNG
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] {display: block !important;}
            /* Ẩn menu mặc định của Streamlit nếu có */
            [data-testid="stSidebarNav"] {display: none !important;}
        </style>
        """,
        unsafe_allow_html=True
    )
    
    with st.sidebar:
        st.title("📌 Menu Hệ Thống")
        st.markdown("👤 **Tài khoản:** Admin")
        
        if st.button("🚪 Đăng xuất", use_container_width=True):
            st.session_state["password_correct"] = False
            st.rerun()
            
        st.markdown("---")
        st.subheader("📑 Danh sách Báo cáo")
        
        # ĐÂY CHÍNH LÀ ĐOẠN TẠO MENU CHUYỂN TRANG
        st.page_link("dashboard.py", label="📊 Tổng Quan Sales", icon="🏠")
        st.page_link("pages/1_📈_Sales_Team.py", label="📈 Sales Team Analytics", icon="📈")
        
        st.markdown("---")