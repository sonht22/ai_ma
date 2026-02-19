# File: test_key.py
from google import genai

# Dán key của bạn vào đây
MY_KEY = "AIzaSyCvg_812SSuJCFlQ3g3TQeVUJQAsT7UGPs" 

print(f"--- Đang kiểm tra Key: {MY_KEY[:10]}... ---")

try:
    client = genai.Client(api_key=MY_KEY)
    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents="Xin chào, bạn có khỏe không?"
    )
    print("\n✅ KẾT QUẢ: Key hoạt động tốt!")
    print(f"AI trả lời: {response.text}")
except Exception as e:
    print(f"\n❌ LỖI: {e}")
    print("👉 Gợi ý: Key sai, hoặc chưa bật 'Generative Language API' trong Google Cloud.")