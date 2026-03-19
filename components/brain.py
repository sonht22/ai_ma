from google import genai
import json
import re

class StoryBrain:
    def __init__(self, api_key):
        self.api_key = api_key
        # 👇 ĐÃ SỬA DÒNG NÀY: Cập nhật tên Model chuẩn của Google, có kèm model dự phòng
        self.models_to_try = ["gemini-2.5-flash", "gemini-1.5-flash"] 
        
        try:
            self.client = genai.Client(api_key=api_key)
            self.is_connected = True
        except Exception as e:
            print(f"❌ Lỗi kết nối Google AI: {e}")
            self.is_connected = False

    def generate_story_pages(self, user_request, num_pages=1, story_length="150 ký tự"):
        backup_story = []
        for i in range(num_pages):
            backup_story.append({
                "text": f"Trang {i+1}: Câu chuyện về một người bạn nhỏ. (Offline).",
                "img_prompt": f"Cute 3d cartoon character, page {i+1}, disney style"
            })

        if not self.is_connected:
            return backup_story

        # BỘ LUẬT THÉP: Ép AI tuân thủ chính xác Số trang và Độ dài
        prompt = f"""
        Vai trò: Biên kịch truyện tranh thiếu nhi chuyên nghiệp.
        
        YÊU CẦU TỪ NGƯỜI DÙNG: "{user_request}"
        
        QUY ĐỊNH BẮT BUỘC:
        1. SỐ TRANG: Bắt buộc chia truyện thành ĐÚNG {num_pages} trang. Mảng JSON của bạn chỉ được phép có đúng {num_pages} phần tử. Tuyệt đối không tạo nhiều hơn!
        2. ĐỘ DÀI MỖI TRANG: {story_length}. Bạn hãy căn chỉnh số từ sao cho phần 'text' của mỗi trang đáp ứng đúng giới hạn ký tự/độ dài này.
        3. HÌNH ẢNH: Phần 'img_prompt' viết bằng tiếng Anh mô tả bối cảnh để AI vẽ tranh.
        
        ĐỊNH DẠNG OUTPUT (JSON List):
        [
          {{ "text": "Nội dung tiếng Việt...", "img_prompt": "Mô tả tranh tiếng Anh..." }}
        ]
        """

        for model in self.models_to_try:
            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=prompt
                )
                
                raw_text = response.text.strip()
                # Dùng Regex để trích xuất đúng phần mảng JSON ra
                match = re.search(r'\[.*\]', raw_text, re.DOTALL)
                
                if match:
                    json_str = match.group(0)
                    pages = json.loads(json_str)
                    
                    if isinstance(pages, list):
                        # BƯỚC XỬ LÝ QUYẾT ĐỊNH: Cắt bỏ phần thừa nếu AI tạo lố trang
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