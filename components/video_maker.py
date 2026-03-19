import os
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from proglog import ProgressBarLogger

# ========================================================
# TẠO "CẢM BIẾN" BÁO CÁO TIẾN TRÌNH RENDER CHO MOVIEPY
# ========================================================
class RenderLogger(ProgressBarLogger):
    def __init__(self, ui_updater): # <--- Đã đổi tên ở đây
        super().__init__()
        self.ui_updater = ui_updater # <--- Đổi tên để không bị "đụng hàng" với hệ thống

    def bars_callback(self, bar, attr, value, old_value=None):
        if bar == 't':
            total = self.bars[bar].get('total', 0)
            if total > 0:
                percent = 10 + (value / total) * 90 
                if self.ui_updater:
                    self.ui_updater("🎬 Đang render những khung hình cuối cùng...", percent)

class VideoMaker:
    def __init__(self):
        pass

    # ĐÃ THÊM: Biến progress_callback để nhận hàm cập nhật giao diện
    def create_video(self, pages, output_path, progress_callback=None):
        """
        Nhận vào danh sách các trang (chứa đường dẫn ảnh và âm thanh)
        và xuất ra một file video MP4 hoàn chỉnh có báo cáo % tiến trình.
        """
        try:
            clips = []
            if progress_callback:
                progress_callback("⏳ Đang chuẩn bị gom ảnh và giọng đọc...", 5)
            
            total_pages = len(pages)
            for i, page in enumerate(pages):
                img_path = page.get('img_path')
                audio_path = page.get('audio_path')

                if not img_path or not os.path.exists(img_path):
                    continue
                if not audio_path or not os.path.exists(audio_path):
                    continue

                # Đọc file âm thanh
                audio_clip = AudioFileClip(audio_path)
                duration = audio_clip.duration

                # Kéo dài ảnh bằng đúng âm thanh và lồng tiếng vào
                img_clip = ImageClip(img_path).set_duration(duration)
                img_clip = img_clip.set_audio(audio_clip)

                clips.append(img_clip)

            if not clips:
                return False

            if progress_callback:
                progress_callback("⏳ Đang ráp nối các trang truyện lại với nhau...", 10)
                
            final_video = concatenate_videoclips(clips, method="compose")
            
            # Kích hoạt bộ cảm biến báo cáo %
            my_logger = RenderLogger(progress_callback) if progress_callback else None
            
            # Tiến hành render file MP4
            final_video.write_videofile(
                output_path, 
                fps=24, 
                codec="libx264", 
                audio_codec="aac",
                logger=my_logger  # <--- Gắn cảm biến vào đây thay vì để None như cũ
            )
            
            # Dọn dẹp bộ nhớ chống tràn RAM
            final_video.close()
            for c in clips:
                c.close()
                
            if progress_callback:
                progress_callback("✅ Xong! Đang lưu file...", 100)
                
            return True
            
        except Exception as e:
            print(f"❌ Lỗi khi tạo video: {e}")
            return False