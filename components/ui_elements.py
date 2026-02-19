import streamlit as st

def apply_custom_style():
    """Hàm này chứa CSS để tô màu giao diện cho giống trường mầm non"""
    st.markdown("""
        <style>
        /* Đổi màu nền chính */
        .stApp {
            background-color: #FFF9C4; /* Màu vàng nhạt kem */
        }
        /* Tiêu đề chính */
        .main-title {
            color: #FF6F00;
            text-align: center;
            font-size: 40px;
            font-weight: bold;
            font-family: 'Comic Sans MS', cursive, sans-serif;
            margin-bottom: 10px;
        }
        /* Tiêu đề phụ */
        .sub-title {
            color: #2E7D32;
            text-align: center;
            font-size: 18px;
            font-style: italic;
        }
        /* Nút bấm */
        .stButton>button {
            background-color: #FF4081;
            color: white;
            border-radius: 20px;
            border: 2px solid white;
            font-weight: bold;
            width: 100%;
            height: 50px;
        }
        .stButton>button:hover {
            background-color: #F50057;
            border-color: #FFC107;
        }
        </style>
    """, unsafe_allow_html=True)

def render_header():
    """Hiển thị phần đầu trang"""
    st.markdown('<div class="main-title">🐻 Lớp Học Hạnh Phúc 🎈</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Hệ thống kể chuyện AI dành riêng cho bé</div>', unsafe_allow_html=True)
    st.markdown("---")