from google import genai
import json
import re

class StoryBrain:
    def __init__(self, api_key):
        self.api_key = api_key
        # Cập nhật tên Model chuẩn của Google, có kèm model dự phòng
        self.models_to_try = ["gemini-2.5-flash", "gemini-1.5-flash"] 
        
        try:
            self.client = genai.Client(api_key=api_key)
            self.is_connected = True
        except Exception as e:
            print(f"❌ Lỗi kết nối Google AI: {e}")
            self.is_connected = False

    def generate_story_pages(self, user_request, num_pages=1, story_length=""):
        backup_story = []
        for i in range(num_pages):
            backup_story.append({
                "text": f"Trang {i+1}: Câu chuyện về một người bạn nhỏ. (Offline).",
                "img_prompt": f"Cute 3d cartoon character, page {i+1}, disney style"
            })

        if not self.is_connected:
            return backup_story

        # BỘ LUẬT THÉP CẢI TIẾN: Hỗ trợ cả Sáng tác và Chia trang truyện có sẵn
        prompt = f"""
        Vai trò: Biên kịch truyện tranh thiếu nhi chuyên nghiệp.

        NỘI DUNG TỪ NGƯỜI DÙNG:
        "{user_request}"

        NHIỆM VỤ:
        Phân tích 'NỘI DUNG TỪ NGƯỜI DÙNG'.
        - Nếu đó là một chủ đề/ý tưởng ngắn, hãy SÁNG TÁC một câu chuyện hoàn chỉnh dựa trên chủ đề đó.
        - Nếu đó là một ĐOẠN VĂN BẢN DÀI (một câu chuyện đã viết sẵn), tuyệt đối KHÔNG ĐƯỢC tóm tắt hay cắt xén. Hãy CHIA ĐỀU toàn bộ văn bản đó thành các trang truyện.

        QUY ĐỊNH BẮT BUỘC:
        1. SỐ TRANG: Bắt buộc chia truyện thành ĐÚNG {num_pages} trang. Mảng JSON chỉ được phép có đúng {num_pages} phần tử.
        2. NỘI DUNG: {story_length} Phải đảm bảo tính liên tục của câu chuyện.
        3. HÌNH ẢNH: Phần 'img_prompt' viết bằng TIẾNG ANH, mô tả chi tiết bối cảnh, nhân vật, hành động để AI vẽ tranh minh họa cho trang đó.

        ĐỊNH DẠNG OUTPUT BẮT BUỘC (JSON List):
        [
          {{ "text": "Nội dung tiếng Việt trang 1...", "img_prompt": "Mô tả tranh tiếng Anh..." }}
        ]
        """

        for model in self.models_to_try:
            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=prompt
                )
                
                raw_text = response.text.strip()
                match = re.search(r'\[.*\]', raw_text, re.DOTALL)
                
                if match:
                    json_str = match.group(0)
                    pages = json.loads(json_str)
                    
                    if isinstance(pages, list):
                        if len(pages) > num_pages:
                            print(f"⚠️ AI lỡ tạo {len(pages)} trang. Đang cắt xén về đúng {num_pages} trang!")
                            pages = pages[:num_pages] 
                            
                        print(f"✅ AI đã viết xong {len(pages)} trang truyện bằng model {model}!")
                        return pages
            except Exception as e:
                print(f"⚠️ {model} gặp lỗi: {e}")
                continue
        
        print("❌ AI thất bại. Dùng dữ liệu mẫu.")
        return backup_story