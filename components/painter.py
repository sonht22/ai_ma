import requests
import time
import os
import random # Thêm thư viện để tự tạo mã Seed ngẫu nhiên

class AI_Painter:
    def __init__(self, hf_token):
        self.hf_token = hf_token
        
        # Danh sách model xịn nhất trên HF hiện nay
        self.models = [
            "black-forest-labs/FLUX.1-schnell", 
            "prompthero/openjourney",           
            "runwayml/stable-diffusion-v1-5"    
        ]
        
        # TỰ ĐỘNG TẠO SEED NGAY KHI HỌA SĨ BẮT ĐẦU LÀM VIỆC
        self.story_seed = random.randint(1, 4294967295)
        print(f"🔐 Đã khởi tạo Họa sĩ. Khóa nhân vật với Seed: {self.story_seed}")

    def generate_image(self, user_prompt, output_path):
        if len(self.hf_token) < 10:
            print("❌ Lỗi: Chưa nhập Hugging Face Token.")
            return False

        headers = {"Authorization": f"Bearer {self.hf_token}"}
        
        full_prompt = (
            f"super cute chibi 3d animation for kids, "
            f"nursery rhyme illustration style, friendly and cheerful characters, "
            f"bright pastel colors, disney junior style, "
            f"{user_prompt}, 8k resolution, masterpiece"
        )
        neg_prompt = "ugly, deformed, scary, creepy faces, dark shadows, gloomy, blurry, grainy, low resolution, realistic, adult style, cluttered background, text, watermark"

        # ĐƯA SEED VÀO GÓI LỆNH YÊU CẦU VẼ
        payload = {
            "inputs": full_prompt,
            "parameters": {
                "negative_prompt": neg_prompt,
                "seed": self.story_seed # Mọi bức ảnh trong truyện này đều xài chung 1 Seed
            }
        }

        for model in self.models:
            api_url = f"https://router.huggingface.co/hf-inference/models/{model}"
            print(f"🎨 Đang gọi họa sĩ: {model}...")
            
            for attempt in range(3):
                try:
                    response = requests.post(api_url, headers=headers, json=payload)
                    
                    if response.status_code == 200:
                        with open(output_path, 'wb') as f:
                            f.write(response.content)
                        print(f"✅ Vẽ thành công với {model}!")
                        return True
                        
                    elif response.status_code == 503:
                        data = response.json()
                        wait_time = data.get("estimated_time", 20.0)
                        print(f"⏳ Họa sĩ đang ngủ đông. Cần chờ khoảng {int(wait_time)} giây...")
                        time.sleep(wait_time + 2)
                        continue
                        
                    else:
                        print(f"⚠️ {model} từ chối (Lỗi {response.status_code}): {response.text}")
                        break 
                        
                except Exception as e:
                    print(f"⚠️ Lỗi kết nối mạng: {e}")
                    break

        print("❌ Thất bại: Tất cả họa sĩ đều bận hoặc không thể kết nối.")
        return False