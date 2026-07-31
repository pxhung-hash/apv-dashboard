import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CẤU HÌNH TRANG WEB
st.set_page_config(page_title="YKK Sales Dashboard", page_icon="📊", layout="wide")

# ==========================================
# CHỨC NĂNG BẢO VỆ MẬT KHẨU NỘI BỘ
# ==========================================
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        st.title("🔒 Đăng nhập Hệ thống Báo cáo YKK AP")
        pwd = st.text_input("Vui lòng nhập mật khẩu nội bộ:", type="password")
        if st.button("Đăng nhập"):
            if pwd == "Ykk@2026":  # <-- BẠN THAY MẬT KHẨU MỚI TẠI ĐÂY
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ Mật khẩu không đúng!")
        return False
    return True

# Kiểm tra mật khẩu, nếu chưa đúng sẽ CHẶN toàn bộ chương trình bên dưới
if not check_password():
    st.stop()

# ==========================================
# NỘI DUNG DASHBOARD (CHỈ HIỆN KHU ĐÃ ĐĂNG NHẬP)
# ==========================================
st.title("📊 YKK AP - Sales & S&OP Dashboard")
st.markdown("---")

# 2. HÀM KÉO DỮ LIỆU TỪ GOOGLE SHEETS CÓ BẢO VỆ
@st.cache_data(ttl=60) # Tự động làm mới dữ liệu mỗi 60 giây
def load_data():
    try:
        # Link CSV trực tiếp
        sheet_csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS227G6dkgwY-zTUJm8vt-ocNjH6JnTRw9jPGvx2LDR1aLGgXASNG8lEx_TKoUVXLpxBYoYvUlAhNR6/pub?gid=0&single=true&output=csv"
        df = pd.read_csv(sheet_csv_url)
        
        # BẢO VỆ CỘT: Kiểm tra nếu Sheets bị đổi tên cột thì tự động tạo cột trống để web không sập
        required_cols = ['project_stage', 'award_status', 'apv_fab_price_usd', 'material_amount_fab_usd', 'fab']
        for col in required_cols:
            if col not in df.columns:
                df[col] = None 
        
        # Tiền xử lý dữ liệu
        df['stage_clean'] = df['project_stage'].fillna(df['award_status']).fillna('Unknown').astype(str)
        df['stage_clean'] = df['stage_clean'].replace({'Lost': 'LOST', 'MKT Research': 'Research'})
        
        # Ép kiểu dữ liệu tiền USD
        df['value_usd'] = pd.to_numeric(df['apv_fab_price_usd'], errors='coerce').fillna(
                          pd.to_numeric(df['material_amount_fab_usd'], errors='coerce')).fillna(0)
        
        # Xử lý tên FAB
        df['fab_clean'] = df['fab'].fillna('Unknown').astype(str).str.strip()
        df['fab_clean'] = df['fab_clean'].replace({'-': 'Unknown', 'nan': 'Unknown'})
        
        return df
    
    except Exception as e:
        # Nếu có lỗi mạng hoặc lỗi file, in ra màn hình web thay vì làm sập server
        st.error(f"⚠️ Không thể tải dữ liệu từ Google Sheets. Chi tiết lỗi: {e}")
        return pd.DataFrame()

with st.spinner('Đang kéo dữ liệu từ Google Sheets...'):
    df = load_data()

# Dừng chạy tiếp nếu không có dữ liệu
if df.empty:
    st.stop()

# 3. TẠO BỘ LỌC BÊN SIDEBAR (Thêm nút Đăng xuất)
st.sidebar.header("🔍 Bộ lọc dữ liệu")

# Thêm nút Đăng xuất ở góc trái cho tiện sử dụng
if st.sidebar.button("🚪 Đăng xuất"):
    st.session_state["password_correct"] = False
    st.rerun()

valid_fabs = [f for f in df['fab_clean'].unique() if f != 'Unknown']
selected_fabs = st.sidebar.multiselect("Chọn đối tác FAB:", options=valid_fabs, default=[])

if selected_fabs:
    filtered_df = df[df['fab_clean'].isin(selected_fabs)]
else:
    filtered_df = df

# 4. VẼ BIỂU ĐỒ 
col1, col2 = st.columns(2)

with col1:
    st.subheader("Số lượng Dự án theo Giai đoạn")
    stage_counts = filtered_df['stage_clean'].value_counts().reset_index()
    stage_counts.columns = ['Giai đoạn', 'Số lượng']
    fig1 = px.bar(stage_counts, y='Giai đoạn', x='Số lượng', orientation='h', text='Số lượng', color='Số lượng', color_continuous_scale='Viridis')
    fig1.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Tỷ lệ Trúng / Trượt (WON/LOST)")
    closed_df = filtered_df[filtered_df['stage_clean'].isin(['WON', 'LOST'])]
    if not closed_df.empty:
        closed_counts = closed_df['stage_clean'].value_counts().reset_index()
        closed_counts.columns = ['Trạng thái', 'Số lượng']
        fig2 = px.pie(closed_counts, values='Số lượng', names='Trạng thái', color='Trạng thái', color_discrete_map={'WON':'#10b981', 'LOST':'#ef4444'}, hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Chưa có dự án WON/LOST.")

st.markdown("---")
st.subheader("Top Đối tác FAB theo Giá trị (USD)")
top_fabs = filtered_df[filtered_df['fab_clean'] != 'Unknown'].groupby('fab_clean')['value_usd'].sum().reset_index()
top_fabs = top_fabs.sort_values(by='value_usd', ascending=False).head(10)

fig3 = px.bar(top_fabs, x='value_usd', y='fab_clean', orientation='h', text_auto='$.2s', color='value_usd', color_continuous_scale='Blues')
fig3.update_layout(yaxis={'categoryorder':'total ascending'}, xaxis_title="Giá trị (USD)", yaxis_title="Nhà thầu (FAB)")
st.plotly_chart(fig3, use_container_width=True)