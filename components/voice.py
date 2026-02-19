import edge_tts
from gtts import gTTS # Thư viện Chị Google

class VoiceEngine:
    def __init__(self, voice_name, rate_value=0):
        self.voice_name = voice_name
        
        # Xử lý tốc độ cho Edge TTS
        if rate_value >= 0:
            self.rate = f"+{int(rate_value)}%"
        else:
            self.rate = f"{int(rate_value)}%"

    async def generate_audio(self, text, output_path):
        try:
            # KIỂM TRA: Nếu người dùng chọn giọng Google
            if self.voice_name == "vi-Google":
                # Dùng thư viện gTTS (Chị Google)
                # Lưu ý: gTTS không chỉnh được tốc độ chi tiết như Edge, nên ta bỏ qua tham số rate
                tts = gTTS(text=text, lang='vi', slow=False)
                tts.save(output_path)
                
            else:
                # Dùng giọng Microsoft Edge (Hoài My / Nam Minh)
                communicate = edge_tts.Communicate(text, self.voice_name, rate=self.rate)
                await communicate.save(output_path)
                
        except Exception as e:
            print(f"Lỗi tạo giọng: {e}")