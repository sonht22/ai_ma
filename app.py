import customtkinter as ctk
import os
import threading
import asyncio
import pygame
import time
import json
import shutil # Thư viện mới để copy file
from tkinter import filedialog
from PIL import Image
from components.video_maker import VideoMaker
from components.brain import StoryBrain
from components.painter import AI_Painter
from components.voice import VoiceEngine

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # 👇 1. DÁN API KEY GOOGLE VÀO ĐÂY 👇
        self.GOOGLE_API_KEY = "AIzaSyCvg_812SSuJCFlQ3g3TQeVUJQAsT7UGPs" 
        
        try: pygame.mixer.init()
        except: print("Lỗi âm thanh")
        
        self.title("Truyện Tranh AI (V10.0 - Đóng gói & Dọn rác tự động)")
        self.geometry("1150x780") 
        
        self.pages = []
        self.current_page_idx = 0
        self.is_auto_playing = False 
        self.is_dragging = False

        # --- GỌI TÍNH NĂNG DỌN RÁC KHI MỞ APP ---
        self.cleanup_old_data()
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        # === CỘT TRÁI (INPUT) ===
        self.sidebar = ctk.CTkFrame(self, fg_color="#E0F7FA")
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.menu_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.menu_frame.pack(fill="x", pady=10)
        self.btn_load = ctk.CTkButton(self.menu_frame, text="📂 Mở", width=80, fg_color="#607D8B", command=self.load_story)
        self.btn_load.pack(side="left", padx=5)
        self.btn_save = ctk.CTkButton(self.menu_frame, text="💾 Lưu trọn bộ", width=120, fg_color="#4CAF50", command=self.save_story)
        self.btn_save.pack(side="right", padx=5)

        # --- NÚT XUẤT VIDEO MỚI ---
        self.btn_export = ctk.CTkButton(self.menu_frame, text="🎬 Xuất MP4", width=80, fg_color="#9C27B0", command=self.export_video)
        self.btn_export.pack(side="right", padx=2)

        ctk.CTkLabel(self.sidebar, text="-----------------").pack()

        # --- PHẦN NHẬP LIỆU ---
        ctk.CTkLabel(self.sidebar, text="Ý TƯỞNG TRUYỆN", font=("Arial", 20, "bold")).pack(pady=10)
        ctk.CTkLabel(self.sidebar, text="Bạn muốn kể chuyện gì?", anchor="w").pack(fill="x", padx=15)
        self.request_box = ctk.CTkTextbox(self.sidebar, height=120, font=("Arial", 14))
        self.request_box.pack(pady=5, padx=10, fill="x")
        self.request_box.insert("0.0", "Kể chuyện về một chú rồng con tập bay.")

        # --- CẤU HÌNH ---
        ctk.CTkLabel(self.sidebar, text="Cấu hình:", anchor="w").pack(fill="x", padx=15, pady=(10,0))
        self.row_config = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.row_config.pack(fill="x", padx=5)
        self.page_count_ent = ctk.CTkEntry(self.row_config, width=70, placeholder_text="Số trang"); self.page_count_ent.pack(side="left", padx=5); self.page_count_ent.insert(0, "1")
        self.length_ent = ctk.CTkEntry(self.row_config, width=120, placeholder_text="Số ký tự"); self.length_ent.pack(side="left", padx=5); self.length_ent.insert(0, "150 ký tự")
        self.voice_map = {"Nữ: Hoài My": "vi-VN-HoaiMyNeural", "Nam: Nam Minh": "vi-VN-NamMinhNeural", "Nữ: Chị Google": "vi-Google", "Anh: Christopher": "en-US-ChristopherNeural"}
        self.voice_opt = ctk.CTkOptionMenu(self.row_config, values=list(self.voice_map.keys()), width=150); self.voice_opt.pack(side="left", padx=5)
        
        self.voice_frame = ctk.CTkFrame(self.sidebar, fg_color="#B2EBF2")
        self.voice_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(self.voice_frame, text="Tốc độ đọc:", font=("Arial", 12, "bold")).pack(pady=(5,0))
        self.speed_slider = ctk.CTkSlider(self.voice_frame, from_=-50, to=50, number_of_steps=20, command=self.update_speed_label)
        self.speed_slider.pack(fill="x", padx=10, pady=5); self.speed_slider.set(-10)
        self.speed_label = ctk.CTkLabel(self.voice_frame, text="Mặc định (-10%)"); self.speed_label.pack(pady=(0,5))

        ctk.CTkLabel(self.sidebar, text="-----------------").pack()

        # === KHU VỰC HUGGING FACE TOKEN ===
        self.api_frame = ctk.CTkFrame(self.sidebar, fg_color="#E8EAF6") 
        self.api_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(self.api_frame, text="🤗 Hugging Face Token:", font=("Arial", 12, "bold"), text_color="#3F51B5").pack(anchor="w", padx=10, pady=(5,0))
        self.hf_key_ent = ctk.CTkEntry(self.api_frame, placeholder_text="Dán Token (hf_...) vào đây...", show="*")
        self.hf_key_ent.pack(fill="x", padx=10, pady=5)

        self.btn_create = ctk.CTkButton(self.sidebar, text="✨ SÁNG TÁC NGAY", height=50, command=self.start_process, fg_color="#FF5722", font=("Arial", 16, "bold"), hover_color="#E64A19")
        self.btn_create.pack(pady=10, padx=10)
        
        self.status_lbl = ctk.CTkLabel(self.sidebar, text="Sẵn sàng", wraplength=200, text_color="green")
        self.status_lbl.pack(side="bottom", pady=20)

        # === CỘT PHẢI (HIỂN THỊ) ===
        self.book_frame = ctk.CTkFrame(self, fg_color="white")
        self.book_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.nav_frame = ctk.CTkFrame(self.book_frame, fg_color="#F5F5F5", height=100); self.nav_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        self.slider_frame = ctk.CTkFrame(self.nav_frame, fg_color="transparent"); self.slider_frame.pack(side="top", fill="x", padx=10, pady=5)
        self.lbl_current_time = ctk.CTkLabel(self.slider_frame, text="00:00", width=40); self.lbl_current_time.pack(side="left")
        self.slider = ctk.CTkSlider(self.slider_frame, from_=0, to=100, command=self.on_slider_drag); self.slider.pack(side="left", fill="x", expand=True, padx=10)
        self.lbl_total_time = ctk.CTkLabel(self.slider_frame, text="00:00", width=40); self.lbl_total_time.pack(side="right")
        self.buttons_frame = ctk.CTkFrame(self.nav_frame, fg_color="transparent"); self.buttons_frame.pack(side="bottom", fill="x", pady=5)
        self.btn_prev = ctk.CTkButton(self.buttons_frame, text="⏮️ Trước", state="disabled", width=80, command=lambda: self.manual_flip(-1)); self.btn_prev.pack(side="left", padx=20)
        self.btn_play = ctk.CTkButton(self.buttons_frame, text="▶️ ĐỌC TRUYỆN", state="disabled", fg_color="green", width=150, command=self.toggle_auto_read); self.btn_play.pack(side="left", expand=True)
        self.btn_next = ctk.CTkButton(self.buttons_frame, text="Sau ⏭️", state="disabled", width=80, command=lambda: self.manual_flip(1)); self.btn_next.pack(side="right", padx=20)
        self.text_box = ctk.CTkTextbox(self.book_frame, height=130, font=("Arial", 16), wrap="word"); self.text_box.pack(side="bottom", fill="x", padx=10, pady=5)
        self.img_label = ctk.CTkLabel(self.book_frame, text="[Tranh minh họa]", fg_color="#EEEEEE"); self.img_label.pack(side="top", fill="both", expand=True, padx=10, pady=10)

    # ================= CÁC TÍNH NĂNG MỚI =================
    def cleanup_old_data(self):
        """Dọn dẹp các file trong thư mục data đã tạo hơn 24 giờ."""
        data_dir = "data"
        if not os.path.exists(data_dir):
            return
            
        current_time = time.time()
        deleted_count = 0
        
        for filename in os.listdir(data_dir):
            filepath = os.path.join(data_dir, filename)
            if os.path.isfile(filepath):
                # Check file age (24 hours = 86400 seconds)
                if current_time - os.path.getmtime(filepath) > 86400:
                    try:
                        os.remove(filepath)
                        deleted_count += 1
                    except: pass
        if deleted_count > 0:
            print(f"🧹 Đã tự động xóa {deleted_count} file rác cũ hơn 24h trong thư mục data.")

    def save_story(self):
        if not self.pages: return
        
        # Mở cửa sổ yêu cầu nhập Tên Thư Mục
        folder_path = filedialog.asksaveasfilename(
            title="Nhập tên thư mục để lưu trọn bộ truyện", 
            defaultextension=""
        )
        if not folder_path: return
        
        try:
            # 1. Tạo thư mục mới (nếu chưa có)
            os.makedirs(folder_path, exist_ok=True)
            
            export_pages = []
            for i, page in enumerate(self.pages):
                new_page = page.copy()
                
                # 2. Copy file ảnh vào thư mục mới và sửa tên
                old_img = page.get('img_path', '')
                if os.path.exists(old_img):
                    new_img_name = f"trang_{i+1}.jpg"
                    new_img_path = os.path.join(folder_path, new_img_name)
                    shutil.copy2(old_img, new_img_path)
                    new_page['img_path'] = new_img_name # Chỉ lưu tên tương đối
                
                # 3. Copy file âm thanh vào thư mục mới và sửa tên
                old_audio = page.get('audio_path', '')
                if os.path.exists(old_audio):
                    new_audio_name = f"giong_doc_{i+1}.mp3"
                    new_audio_path = os.path.join(folder_path, new_audio_name)
                    shutil.copy2(old_audio, new_audio_path)
                    new_page['audio_path'] = new_audio_name # Chỉ lưu tên tương đối
                    
                export_pages.append(new_page)
            
            # 4. Lưu kịch bản (JSON) vào trong thư mục đó
            json_path = os.path.join(folder_path, "kich_ban.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(export_pages, f, ensure_ascii=False, indent=4)
                
            self.update_status(f"💾 Đã đóng gói thành công vào: {os.path.basename(folder_path)}")
        except Exception as e:
            self.update_status(f"❌ Lỗi lưu file: {e}")

    def load_story(self):
        file_path = filedialog.askopenfilename(
            title="Chọn file kich_ban.json trong thư mục truyện",
            filetypes=[("JSON files", "*.json")]
        )
        if file_path:
            try:
                self.stop_audio()
                pygame.mixer.music.unload()
                
                base_dir = os.path.dirname(file_path) # Lấy thư mục gốc chứa file json
                
                with open(file_path, 'r', encoding='utf-8') as f: 
                    loaded_pages = json.load(f)
                
                # Khôi phục lại đường dẫn file tuyệt đối để phần mềm đọc được
                for page in loaded_pages:
                    if 'img_path' in page and not os.path.isabs(page['img_path']):
                        page['img_path'] = os.path.abspath(os.path.join(base_dir, page['img_path']))
                    if 'audio_path' in page and not os.path.isabs(page['audio_path']):
                        page['audio_path'] = os.path.abspath(os.path.join(base_dir, page['audio_path']))
                        
                self.pages = loaded_pages
                self.current_page_idx = 0
                self.update_book_ui()
                self.update_status(f"📂 Đã mở truyện từ: {os.path.basename(base_dir)}")
            except Exception as e: 
                self.update_status(f"❌ Lỗi đọc file: {e}")
    # =======================================================

    def update_speed_label(self, value): val = int(value); self.speed_label.configure(text=f"Nhanh (+{val}%)" if val > 0 else f"Chậm ({val}%)")

    def start_process(self):
        if len(self.GOOGLE_API_KEY) < 10: 
            self.status_lbl.configure(text="⚠️ Lỗi: Thiếu Google API Key!", text_color="red")
            return
        
        hf_key = self.hf_key_ent.get().strip()
        if len(hf_key) < 10:
             self.status_lbl.configure(text="⚠️ Lỗi: Chưa nhập Hugging Face Token!", text_color="red")
             return

        self.btn_create.configure(state="disabled", text="⏳ Đang chạy...")
        threading.Thread(target=self.run_generation, args=(hf_key,)).start()

    def run_generation(self, hf_key):
        try:
            try: num_pages = int(self.page_count_ent.get())
            except: num_pages = 1
            length_desc = self.length_ent.get() or "150 ký tự"
            user_request = self.request_box.get("0.0", "end").strip()
            selected_label = self.voice_opt.get(); voice_code = self.voice_map[selected_label]; speed_val = self.speed_slider.get()

            if not user_request: self.update_status("⚠️ Chưa nhập ý tưởng!"); return

            self.update_status(f"🧠 Google đang viết truyện...")
            brain = StoryBrain(self.GOOGLE_API_KEY)
            raw_pages = brain.generate_story_pages(user_request, num_pages, length_desc)

            if not raw_pages: self.update_status("⚠️ AI viết truyện thất bại."); return

            self.pages = raw_pages
            painter = AI_Painter(hf_token=hf_key) 
            
            if not os.path.exists("data"): os.makedirs("data")
            session_id = int(time.time()) 
            
            total_pages = len(self.pages)
            for i, page in enumerate(self.pages):
                self.update_status(f"🎨 Đang vẽ trang {i+1}/{total_pages}...")
                img_name = f"data/{session_id}_scene_{i}.jpg"
                img_path = os.path.abspath(img_name)
                
                success = painter.generate_image(page['img_prompt'], img_path)
                if success:
                    page['img_path'] = img_path
                else:
                    self.update_status(f"⚠️ Lỗi vẽ tranh. Server bận hoặc Token lỗi.")
                    return
                
                self.update_status(f"🎤 Thu âm {i+1}/{total_pages}...")
                audio_name = f"data/{session_id}_scene_{i}.mp3"
                audio_path = os.path.abspath(audio_name)
                voice_eng = VoiceEngine(voice_code, rate_value=speed_val)
                asyncio.run(voice_eng.generate_audio(page['text'], audio_path))
                page['audio_path'] = audio_path
            
            self.update_status("✅ Hoàn tất!")
            self.current_page_idx = 0
            self.after(0, self.update_book_ui)
            
        except Exception as e:
            self.update_status(f"Lỗi: {e}")
            print(e)
        finally:
            self.after(0, lambda: self.btn_create.configure(state="normal", text="✨ SÁNG TÁC NGAY"))

    def update_book_ui(self):
        if not self.pages: return
        page = self.pages[self.current_page_idx]
        self.text_box.delete("0.0", "end")
        self.text_box.insert("0.0", f"Trang {self.current_page_idx + 1}/{len(self.pages)}:\n\n{page['text']}")
        
        if os.path.exists(page.get('img_path', '')):
            try:
                pil_img = Image.open(page['img_path'])
                max_h = 380
                w, h = pil_img.size
                ratio = max_h / h 
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(int(w * ratio), max_h))
                self.img_label.configure(image=ctk_img, text="")
            except: 
                self.img_label.configure(text="Lỗi ảnh")
        else: 
            self.img_label.configure(image=None, text="⚠️ Ảnh lỗi/Chưa tải")

        self.btn_play.configure(state="normal", text="▶️ ĐỌC TRUYỆN", fg_color="green")
        self.btn_prev.configure(state="normal" if self.current_page_idx > 0 else "disabled")
        self.btn_next.configure(state="normal" if self.current_page_idx < len(self.pages) - 1 else "disabled")
        self.slider.set(0)
        self.lbl_current_time.configure(text="00:00")
        self.is_auto_playing = False

    def toggle_auto_read(self):
        if self.is_auto_playing: 
            self.stop_audio()
        else: 
            self.is_auto_playing = True
            self.btn_play.configure(text="⏹️ DỪNG", fg_color="red")
            self.play_audio_sequence()

    def stop_audio(self):
        self.is_auto_playing = False
        try: pygame.mixer.music.stop()
        except: pass
        self.btn_play.configure(text="▶️ TIẾP TỤC", fg_color="green")

    def play_audio_sequence(self):
        page = self.pages[self.current_page_idx]
        audio = page.get('audio_path', '')
        if os.path.exists(audio):
            try: 
                pygame.mixer.music.load(audio)
                sound = pygame.mixer.Sound(audio)
                self.audio_duration = sound.get_length()
                self.slider.configure(to=self.audio_duration)
                self.lbl_total_time.configure(text=time.strftime('%M:%S', time.gmtime(self.audio_duration)))
                pygame.mixer.music.play()
                self.update_slider_loop()
            except Exception as e: 
                print(f"Lỗi phát nhạc: {e}")
                self.stop_audio()
        else: 
            print(f"Không tìm thấy file: {audio}")
            self.stop_audio()

    def update_slider_loop(self):
        if not pygame.mixer.music.get_busy() and self.is_auto_playing:
            if self.current_page_idx < len(self.pages) - 1: 
                self.current_page_idx += 1
                self.update_book_ui()
                self.after(1000, self.play_audio_sequence)
            else: 
                self.stop_audio()
                self.status_lbl.configure(text="🎉 Xong!")
            return
        if pygame.mixer.music.get_busy() and not self.is_dragging:
            try: 
                curr = pygame.mixer.music.get_pos() / 1000
                self.slider.set(curr)
                self.lbl_current_time.configure(text=time.strftime('%M:%S', time.gmtime(curr)))
            except: pass
        if self.is_auto_playing or pygame.mixer.music.get_busy(): 
            self.after(500, self.update_slider_loop)

    def on_slider_drag(self, value):
        try: pygame.mixer.music.set_pos(value)
        except: pass

    def manual_flip(self, direction):
        self.stop_audio()
        self.current_page_idx += direction
        self.update_book_ui()

    def update_status(self, text):
        self.after(0, lambda: self.status_lbl.configure(text=text))
    def export_video(self):
        if not self.pages:
            self.update_status("⚠️ Chưa có truyện để xuất video!")
            return
            
        # Hỏi người dùng nơi lưu file mp4
        file_path = filedialog.asksaveasfilename(
            title="Lưu Video MP4",
            defaultextension=".mp4", 
            filetypes=[("MP4 Video", "*.mp4")]
        )
        if not file_path: 
            return

        self.btn_export.configure(state="disabled", text="⏳ Đang render...")
        self.update_status("🎬 Đang ghép video... Vui lòng đợi!")

        # Chạy ngầm trong luồng riêng để giao diện không bị đơ
        threading.Thread(target=self.run_export_video, args=(file_path,)).start()

    def run_export_video(self, file_path):
        maker = VideoMaker()
        success = maker.create_video(self.pages, file_path)
        
        if success:
            self.update_status(f"🎉 Đã xuất Video: {os.path.basename(file_path)}")
        else:
            self.update_status("❌ Lỗi xuất video. Xem Terminal.")
            
        self.after(0, lambda: self.btn_export.configure(state="normal", text="🎬 Xuất MP4"))
if __name__ == "__main__":
    app = App()
    app.mainloop()
    