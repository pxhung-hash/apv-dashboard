import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CẤU HÌNH TRANG WEB
st.set_page_config(page_title="Sales Team Analytics", page_icon="📈", layout="wide")
st.title("📈 Sales Team - Phân Tích Cơ Cấu & Loại Dự Án")
st.markdown("---")

# 2. HÀM KÉO DỮ LIỆU TỪ GOOGLE SHEETS
@st.cache_data(ttl=60)
def load_data():
    try:
        sheet_csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS227G6dkgwY-zTUJm8vt-ocNjH6JnTRw9jPGvx2LDR1aLGgXASNG8lEx_TKoUVXLpxBYoYvUlAhNR6/pub?gid=0&single=true&output=csv"
        df = pd.read_csv(sheet_csv_url)
        
        # Kiểm tra và tự động tạo cột nếu dính lỗi thiếu cột
        required_cols = ['project_type', 'project_stage', 'award_status', 'apv_fab_price_usd', 'material_amount_fab_usd', 'fab', 'name']
        for col in required_cols:
            if col not in df.columns:
                df[col] = None 
        
        # Tiền xử lý Dữ liệu
        # 1. Loại dự án
        df['type_clean'] = df['project_type'].fillna('Chưa phân loại').astype(str).str.strip()
        df['type_clean'] = df['type_clean'].replace({'-': 'Chưa phân loại', 'nan': 'Chưa phân loại'})
        
        # 2. Giai đoạn dự án
        df['stage_clean'] = df['project_stage'].fillna(df['award_status']).fillna('Unknown').astype(str)
        df['stage_clean'] = df['stage_clean'].replace({'Lost': 'LOST', 'MKT Research': 'Research'})
        
        # 3. Giá trị USD
        df['value_usd'] = pd.to_numeric(df['apv_fab_price_usd'], errors='coerce').fillna(
                          pd.to_numeric(df['material_amount_fab_usd'], errors='coerce')).fillna(0)
        
        return df
    except Exception as e:
        st.error(f"⚠️ Lỗi tải dữ liệu: {e}")
        return pd.DataFrame()

with st.spinner('Đang tải dữ liệu phân tích Sales...'):
    df = load_data()

if df.empty:
    st.stop()

# 3. THÔNG THỐ TỔNG QUAN (KPIs CARDS)
total_projects = len(df)
total_value = df['value_usd'].sum()
won_df = df[df['stage_clean'] == 'WON']
won_value = won_df['value_usd'].sum()
win_rate = (len(won_df) / total_projects * 100) if total_projects > 0 else 0

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Tổng số dự án", f"{total_projects:,}")
kpi2.metric("Tổng giá trị Pipeline", f"${total_value:,.0f}")
kpi3.metric("Giá trị trúng thầu (WON)", f"${won_value:,.0f}")
kpi4.metric("Tỷ lệ trúng thầu (Win Rate)", f"{win_rate:.1f}%")

st.markdown("---")

# 4. BỘ LỌC BÊN TAY TRÁI
st.sidebar.header("🔍 Bộ Lọc Sales")
all_types = list(df['type_clean'].unique())
selected_types = st.sidebar.multiselect("Chọn loại dự án:", options=all_types, default=[])

if selected_types:
    filtered_df = df[df['type_clean'].isin(selected_types)]
else:
    filtered_df = df

# 5. BIỂU ĐỒ PHÂN TÍCH THEO LOẠI DỰ ÁN
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Số lượng Dự án theo Phân loại")
    type_counts = filtered_df['type_clean'].value_counts().reset_index()
    type_counts.columns = ['Loại dự án', 'Số lượng']
    
    fig_type_count = px.pie(
        type_counts, 
        values='Số lượng', 
        names='Loại dự án',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_type_count.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_type_count, use_container_width=True)

with col2:
    st.subheader("2. Tổng Giá trị USD theo Phân loại")
    type_value = filtered_df.groupby('type_clean')['value_usd'].sum().reset_index()
    type_value.columns = ['Loại dự án', 'Giá trị USD']
    type_value = type_value.sort_values(by='Giá trị USD', ascending=True)
    
    fig_type_val = px.bar(
        type_value, 
        y='Loại dự án', 
        x='Giá trị USD', 
        orientation='h',
        text_auto='$.2s',
        color='Giá trị USD',
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig_type_val, use_container_width=True)

st.markdown("---")

# 6. BIỂU ĐỒ CỘT CHỒNG: LOẠI DỰ ÁN VS GIAI ĐOẠN (STAGE)
st.subheader("3. Ma trận Sức khỏe Pipeline: Loại dự án vs. Giai đoạn")
st.caption("Biểu đồ thể hiện từng loại dự án đang nằm ở bước nào (WON, LOST, Design, Spec, Quotation...)")

type_stage = filtered_df.groupby(['type_clean', 'stage_clean']).size().reset_index(name='Số lượng')

fig_stack = px.bar(
    type_stage, 
    x='type_clean', 
    y='Số lượng', 
    color='stage_clean',
    title="Phân bổ Giai đoạn theo Loại Dự án",
    barmode='stack',
    labels={'type_clean': 'Loại dự án', 'stage_clean': 'Giai đoạn', 'Số lượng': 'Số dự án'}
)
st.plotly_chart(fig_stack, use_container_width=True)

# 7. BẢNG CHI TIẾT DỰ ÁN TOP GIÁ TRỊ
with st.expander("📋 Xem chi tiết danh sách dự án trong nhóm"):
    st.dataframe(
        filtered_df[['project_code', 'name', 'type_clean', 'stage_clean', 'fab', 'value_usd']]
        .sort_values(by='value_usd', ascending=False),
        use_container_width=True
    )