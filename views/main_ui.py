import streamlit as st
import time
from components.ui_elements import apply_custom_style, render_header

class StoryView:
    def __init__(self):
        # Cấu hình tab trình duyệt
        st.set_page_config(
            page_title="AI Mầm Non - Kể Chuyện",
            page_icon="🏫",
            layout="centered"
        )
    
    def render(self):
        # 1. Gọi CSS và Header từ components
        apply_custom_style()
        render_header()

        # 2. Sidebar (Cấu hình)
        with st.sidebar:
            st.image("https://cdn-icons-png.flaticon.com/512/3468/3468306.png", width=100)
            st.header("⚙️ Cấu Hình Cô Giáo AI")
            api_key = st.text_input("🔑 Nhập API Key:", type="password", help="Nhập khóa Google Gemini của bạn")
            voice = st.selectbox("🎤 Chọn giọng đọc:", ["Cô Hoài My (Dịu dàng)", "Chú Nam Minh (Ấm áp)"])
            st.info("💡 Lưu ý: Cần có mạng Internet để AI hoạt động.")

        # 3. Form nhập liệu chính (Chia 2 cột)
        st.subheader("📝 Thông tin của bé")
        
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Tên của bé:", placeholder="Ví dụ: Bé Đào, Bé Bo...")
        with col2:
            hobby = st.text_input("Bé thích gì?", placeholder="Ví dụ: Siêu nhân, Elsa...")

        # Chọn chủ đề
        topic = st.selectbox(
            "📖 Chủ đề câu chuyện hôm nay:",
            ["Giáo dục lễ phép", "Vệ sinh cá nhân", "Khám phá thiên nhiên", "Tình bạn diệu kỳ", "Lễ hội quê hương"]
        )

        # 4. Khu vực hiển thị kết quả (Demo giao diện)
        st.markdown("<br>", unsafe_allow_html=True) # Tạo khoảng cách
        
        if st.button("✨ BẮT ĐẦU KỂ CHUYỆN ✨"):
            if not name or not hobby:
                st.warning("⚠️ Cô ơi, cô quên nhập tên hoặc sở thích của bé rồi!")
            else:
                # Đây là giao diện giả lập để xem trước (Chưa gọi AI thật)
                self.show_loading_and_result_demo(name, topic)

    def show_loading_and_result_demo(self, name, topic):
        """Hàm này chỉ để test giao diện hiển thị thế nào"""
        
        # Giả vờ đang suy nghĩ (Loading)
        with st.spinner(f'🤖 Cô AI đang sáng tác chuyện cho {name}...'):
            time.sleep(2) # Đợi 2 giây giả vờ
        
        # Hiển thị kết quả giả định
        st.success("✅ Đã xong! Mời cô và bé cùng nghe.")
        
        st.markdown(f"### 📖 Câu chuyện: {name} và bài học về {topic}")
        
        # Khung chứa nội dung truyện
        st.info(f"""
        Ngày xửa ngày xưa, ở một ngôi trường mầm non xinh đẹp, có một bạn nhỏ tên là **{name}**.
        Bạn ấy cực kỳ thích **{topic}**... (Đây là khu vực nội dung truyện sẽ hiện ra sau này).
        """)

        # Trình phát nhạc giả định
        st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", format='audio/mp3')
        
        # Nút tải về giả định
        st.button("📥 Tải câu chuyện về máy")