import os
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

class VideoMaker:
    def __init__(self):
        pass

    def create_video(self, pages, output_path):
        """
        Nhận vào danh sách các trang (chứa đường dẫn ảnh và âm thanh)
        và xuất ra một file video MP4 hoàn chỉnh.
        """
        try:
            clips = []
            print("🎬 Bắt đầu quá trình ghép Video...")
            
            for i, page in enumerate(pages):
                img_path = page.get('img_path')
                audio_path = page.get('audio_path')

                # Bỏ qua nếu trang này bị lỗi thiếu ảnh hoặc âm thanh
                if not img_path or not os.path.exists(img_path):
                    print(f"⚠️ Bỏ qua trang {i+1}: Thiếu ảnh.")
                    continue
                if not audio_path or not os.path.exists(audio_path):
                    print(f"⚠️ Bỏ qua trang {i+1}: Thiếu âm thanh.")
                    continue

                # 1. Đọc file âm thanh để lấy thời lượng
                audio_clip = AudioFileClip(audio_path)
                duration = audio_clip.duration

                # 2. Tạo Video Clip từ bức ảnh, kéo dài thời gian bằng đúng độ dài âm thanh
                img_clip = ImageClip(img_path).set_duration(duration)
                
                # 3. Lồng âm thanh vào bức ảnh
                img_clip = img_clip.set_audio(audio_clip)

                clips.append(img_clip)

            if not clips:
                print("❌ Không có trang hợp lệ nào để ghép video!")
                return False

            # 4. Nối tất cả các clip (các trang) lại thành một video dài
            print("⏳ Đang xuất file MP4 (Có thể mất vài phút tùy độ dài)...")
            final_video = concatenate_videoclips(clips, method="compose")
            
            # Xuất ra file MP4 (fps=24 là đủ mượt cho truyện tranh, giúp file nhẹ)
            final_video.write_videofile(
                output_path, 
                fps=24, 
                codec="libx264", 
                audio_codec="aac",
                logger=None # Ẩn các dòng log rườm rà của thư viện
            )
            
            # Dọn dẹp bộ nhớ
            final_video.close()
            for c in clips:
                c.close()
                
            print("✅ Đã xuất Video thành công!")
            return True
            
        except Exception as e:
            print(f"❌ Lỗi khi tạo video: {e}")
            return False