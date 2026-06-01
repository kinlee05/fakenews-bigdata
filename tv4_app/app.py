import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Fake News Detector", page_icon="🔍", layout="wide")
st.title("🔍 Fake News Detection")
st.markdown("Nhập nội dung bài báo để kiểm tra **thật** hay **giả**")

# Khởi tạo lịch sử
if "history" not in st.session_state:
    st.session_state.history = []

st.divider()

# Layout 2 cột
col1, col2 = st.columns([1.5, 1])

with col1:
    st.subheader("📝 Phân tích bài báo")
    text_input = st.text_area("Nội dung bài báo:", height=200, placeholder="Dán nội dung bài báo vào đây...")
    if st.button("Phân tích", type="primary"):
        if text_input.strip() == "":
            st.warning("⚠️ Vui lòng nhập nội dung bài báo!")
        else:
            with st.spinner("Đang phân tích..."):
                try:
                    response = requests.post(
                        "http://localhost:8000/predict",
                        json={"text": text_input},
                        timeout=60
                    )
                    result = response.json()
                    label = result["label"]
                    confidence = result["confidence"]

                    # Lưu vào lịch sử
                    st.session_state.history.append({
                        "Nội dung": text_input[:80] + "..." if len(text_input) > 80 else text_input,
                        "Kết quả": label,
                        "Độ tin cậy": f"{confidence:.1%}"
                    })

                    st.divider()
                    if label == "FAKE":
                        st.error("❌ **GIẢ MẠO**")
                    else:
                        st.success("✅ **TIN THẬT**")
                    st.metric("Độ tin cậy", f"{confidence:.1%}")

                except Exception as e:
                    st.error(f"Lỗi kết nối API: {e}")

with col2:
    st.subheader("📊 Thống kê")
    if len(st.session_state.history) == 0:
        st.info("Chưa có dữ liệu. Hãy phân tích một vài bài báo!")
    else:
        df = pd.DataFrame(st.session_state.history)
        fake_count = len(df[df["Kết quả"] == "FAKE"])
        real_count = len(df[df["Kết quả"] == "REAL"])
        total = len(df)

        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Tổng", total)
        col_b.metric("❌ Giả", fake_count)
        col_c.metric("✅ Thật", real_count)

        # Biểu đồ tròn
        fig = px.pie(
            values=[fake_count, real_count],
            names=["FAKE", "REAL"],
            color_discrete_map={"FAKE": "#ff4b4b", "REAL": "#00c853"},
            title="Tỉ lệ Fake/Real"
        )
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# Lịch sử
if len(st.session_state.history) > 0:
    st.subheader("📋 Lịch sử phân tích")
    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df, use_container_width=True)
    if st.button("🗑️ Xóa lịch sử"):
        st.session_state.history = []
        st.rerun()

st.divider()

# Bảng so sánh 3 model
st.subheader("🤖 So sánh 3 mô hình ML (TV3)")
model_data = {
    "Mô hình": ["Logistic Regression", "Random Forest", "SVM"],
    "Accuracy": ["97.2%", "95.8%", "96.5%"],
    "Precision": ["97.1%", "95.6%", "96.3%"],
    "Recall": ["97.3%", "96.0%", "96.7%"],
    "F1-Score": ["97.2%", "95.8%", "96.5%"]
}
df_models = pd.DataFrame(model_data)
st.dataframe(df_models, use_container_width=True, hide_index=True)
st.caption("✅ Model được chọn: Logistic Regression (accuracy cao nhất)")
