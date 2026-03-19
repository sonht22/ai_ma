import customtkinter as ctk
import os
from dotenv import load_dotenv

# Lệnh này sẽ tự động tìm file .env và nạp các thông tin vào bộ nhớ
load_dotenv(override=True)
import threading
import asyncio
import pygame
import time
import json
import shutil 
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
        
        # Lấy key từ .env
        self.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        
        try: pygame.mixer.init()
        except: print("Lỗi âm thanh")
        
        self.title("Truyện Tranh AI (V11.0 - Cấu hình Ngang Dọc & Đọc Truyện Dài)")
        self.geometry("1150x780") 
        
        self.pages = []
        self.current_page_idx = 0
        self.is_auto_playing = False 
        self.is_dragging = False

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
        
        self.voice_map = {"Nữ: Hoài My": "vi-VN-HoaiMyNeural", "Nam: Nam Minh": "vi-VN-NamMinhNeural", "Nữ: Chị Google": "vi-Google", "Anh: Christopher": "en-US-ChristopherNeural"}
        self.voice_opt = ctk.CTkOptionMenu(self.row_config, values=list(self.voice_map.keys()), width=150); self.voice_opt.pack(side="left", padx=5)
        
        self.voice_frame = ctk.CTkFrame(self.sidebar, fg_color="#B2EBF2")
        self.voice_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(self.voice_frame, text="Tốc độ đọc:", font=("Arial", 12, "bold")).pack(pady=(5,0))
        self.speed_slider = ctk.CTkSlider(self.voice_frame, from_=-50, to=50, number_of_steps=20, command=self.update_speed_label)
        self.speed_slider.pack(fill="x", padx=10, pady=5); self.speed_slider.set(-10)
        self.speed_label = ctk.CTkLabel(self.voice_frame, text="Mặc định (-10%)"); self.speed_label.pack(pady=(0,5))

        ctk.CTkLabel(self.sidebar, text="-----------------").pack()

        # --- MENU CHỌN KHUNG HÌNH NGANG/DỌC ---
        self.ratio_cb = ctk.CTkOptionMenu(
            self.row_config, 
            values=["Ngang (16:9)", "Dọc (9:16)"], 
            width=120,
            fg_color="#3F51B5",
            button_color="#303F9F",
            button_hover_color="#1A237E"
        )
        self.ratio_cb.set("Ngang (16:9)") 
        self.ratio_cb.pack(side="left", padx=5)

        # === HAI NÚT QUY TRÌNH MỚI (ĐÁP ỨNG LUẬT KIỂM SOÁT AI) ===
        self.btn_create = ctk.CTkButton(self.sidebar, text="✍️ 1. VIẾT KỊCH BẢN (AI)", height=40, command=self.start_script_process, fg_color="#FF5722", font=("Arial", 14, "bold"), hover_color="#E64A19")
        self.btn_create.pack(pady=(10, 5), padx=10, fill="x")

        self.btn_generate_media = ctk.CTkButton(self.sidebar, text="🎨 2. DUYỆT & TẠO TRANH", height=40, command=self.open_script_editor, state="disabled", fg_color="#4CAF50", font=("Arial", 14, "bold"))
        self.btn_generate_media.pack(pady=(0, 10), padx=10, fill="x")
        
        self.status_lbl = ctk.CTkLabel(self.sidebar, text="Sẵn sàng", wraplength=200, text_color="green")
        self.status_lbl.pack(side="bottom", pady=20)

        # === CỘT PHẢI (HIỂN THỊ) ===
        self.book_frame = ctk.CTkFrame(self, fg_color="white")
        self.book_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.nav_frame = ctk.CTkFrame(self.book_frame, fg_color="#F5F5F5", height=100); self.nav_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        self.slider_frame = ctk.CTkFrame(self.nav_frame, fg_color="transparent"); self.slider_frame.pack(side="top", fill="x", padx=10, pady=5)
        self.lbl_current_time = ctk.CTkLabel(self.slider_frame, text="00:00", width=40); self.lbl_current_time.pack(side="left")
        # KHỞI TẠO THANH TRƯỢT KIỂU MỚI (Dùng Event chuột)
        self.slider = ctk.CTkSlider(self.slider_frame, from_=0, to=100)
        self.slider.pack(side="left", fill="x", expand=True, padx=10)
        
        # Bắt sự kiện Bấm chuột và Nhả chuột
        self.slider.bind("<ButtonPress-1>", self.on_slider_press)
        self.slider.bind("<ButtonRelease-1>", self.on_slider_release)
        self.lbl_total_time = ctk.CTkLabel(self.slider_frame, text="00:00", width=40); self.lbl_total_time.pack(side="right")
        self.buttons_frame = ctk.CTkFrame(self.nav_frame, fg_color="transparent"); self.buttons_frame.pack(side="bottom", fill="x", pady=5)
        self.btn_prev = ctk.CTkButton(self.buttons_frame, text="⏮️ Trước", state="disabled", width=80, command=lambda: self.manual_flip(-1)); self.btn_prev.pack(side="left", padx=20)
        self.btn_play = ctk.CTkButton(self.buttons_frame, text="▶️ ĐỌC TRUYỆN", state="disabled", fg_color="green", width=150, command=self.toggle_auto_read); self.btn_play.pack(side="left", expand=True)
        self.btn_next = ctk.CTkButton(self.buttons_frame, text="Sau ⏭️", state="disabled", width=80, command=lambda: self.manual_flip(1)); self.btn_next.pack(side="right", padx=20)
        self.text_box = ctk.CTkTextbox(self.book_frame, height=130, font=("Arial", 16), wrap="word"); self.text_box.pack(side="bottom", fill="x", padx=10, pady=5)
        self.img_label = ctk.CTkLabel(self.book_frame, text="[Tranh minh họa]", fg_color="#EEEEEE"); self.img_label.pack(side="top", fill="both", expand=True, padx=10, pady=10)

    # ================= CÁC TÍNH NĂNG MỚI =================
    def cleanup_old_data(self):
        data_dir = "data"
        if not os.path.exists(data_dir): return
            
        current_time = time.time()
        deleted_count = 0
        
        for filename in os.listdir(data_dir):
            filepath = os.path.join(data_dir, filename)
            if os.path.isfile(filepath):
                if current_time - os.path.getmtime(filepath) > 86400:
                    try:
                        os.remove(filepath)
                        deleted_count += 1
                    except: pass
        if deleted_count > 0:
            print(f"🧹 Đã tự động xóa {deleted_count} file rác cũ hơn 24h trong thư mục data.")

    def save_story(self):
        if not self.pages: return
        
        folder_path = filedialog.asksaveasfilename(
            title="Nhập tên thư mục để lưu trọn bộ truyện", 
            defaultextension=""
        )
        if not folder_path: return
        
        try:
            os.makedirs(folder_path, exist_ok=True)
            export_pages = []
            for i, page in enumerate(self.pages):
                new_page = page.copy()
                
                old_img = page.get('img_path', '')
                if os.path.exists(old_img):
                    new_img_name = f"trang_{i+1}.jpg"
                    new_img_path = os.path.join(folder_path, new_img_name)
                    shutil.copy2(old_img, new_img_path)
                    new_page['img_path'] = new_img_name
                
                old_audio = page.get('audio_path', '')
                if os.path.exists(old_audio):
                    new_audio_name = f"giong_doc_{i+1}.mp3"
                    new_audio_path = os.path.join(folder_path, new_audio_name)
                    shutil.copy2(old_audio, new_audio_path)
                    new_page['audio_path'] = new_audio_name 
                    
                export_pages.append(new_page)
            
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
                
                base_dir = os.path.dirname(file_path)
                
                with open(file_path, 'r', encoding='utf-8') as f: 
                    loaded_pages = json.load(f)
                
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

    def update_speed_label(self, value): 
        val = int(value)
        self.speed_label.configure(text=f"Nhanh (+{val}%)" if val > 0 else f"Chậm ({val}%)")

    # ====================================================================
    # QUY TRÌNH BƯỚC 1: AI GỢI Ý KỊCH BẢN
    # ====================================================================
    def start_script_process(self):
        if not self.GOOGLE_API_KEY or len(self.GOOGLE_API_KEY) < 10: 
            self.status_lbl.configure(text="⚠️ Lỗi: Thiếu Google API Key!", text_color="red")
            return
            
        hf_key = os.getenv("HUGGINGFACE_TOKEN")
        if not hf_key or len(hf_key) < 10:
            self.status_lbl.configure(text="⚠️ Lỗi: Chưa có Hugging Face Token!", text_color="red")
            return
            
        try:
            user_prompt = self.request_box.get("0.0", "end-1c").strip()
            num_pages = int(self.page_count_ent.get().strip())
            image_ratio = self.ratio_cb.get() 
            
            if not user_prompt: return self.status_lbl.configure(text="⚠️ Bạn chưa nhập ý tưởng!", text_color="red")
            if num_pages <= 0: return self.status_lbl.configure(text="⚠️ Số trang phải > 0!", text_color="red")
        except Exception as e:
            return self.status_lbl.configure(text=f"⚠️ Lỗi dữ liệu: {e}", text_color="red")
        
        # Khóa nút bấm
        self.btn_create.configure(state="disabled", text="⏳ Đang viết kịch bản...")
        self.btn_generate_media.configure(state="disabled")
        self.status_lbl.configure(text="🚀 Đang nhờ AI (Gemini) viết kịch bản...", text_color="#3F51B5")
        
        threading.Thread(target=self.run_generate_script, args=(hf_key, user_prompt, num_pages, image_ratio), daemon=True).start()

    def run_generate_script(self, hf_key, user_prompt, num_pages, image_ratio):
        try:
            brain = StoryBrain(self.GOOGLE_API_KEY)
            length_desc = "Cân đối độ dài các trang. Tuyệt đối không cắt xén văn bản nếu là một câu chuyện dài."
            raw_pages = brain.generate_story_pages(user_prompt, num_pages, length_desc)

            if not raw_pages: 
                self.update_status("⚠️ AI viết truyện thất bại. Hãy thử lại.")
                self.after(0, lambda: self.btn_create.configure(state="normal", text="✍️ 1. VIẾT LẠI KỊCH BẢN"))
                return

            # Lưu tạm kịch bản và thông số để chờ duyệt
            self.pending_pages = raw_pages
            self.current_hf_key = hf_key
            self.current_image_ratio = image_ratio

            self.update_status("✅ Đã có kịch bản! Vui lòng duyệt và chỉnh sửa.")
            self.after(0, self.on_script_ready)
        except Exception as e:
            self.update_status(f"⚠️ Lỗi: {e}")
            self.after(0, lambda: self.btn_create.configure(state="normal", text="✍️ 1. VIẾT LẠI KỊCH BẢN"))

    def on_script_ready(self):
        self.btn_create.configure(state="normal", text="✍️ 1. VIẾT LẠI KỊCH BẢN")
        self.btn_generate_media.configure(state="normal", text="🎨 2. DUYỆT & TẠO TRANH", fg_color="#4CAF50")
        self.open_script_editor() # Tự động mở bảng duyệt

    # ====================================================================
    # QUY TRÌNH BƯỚC 2: CON NGƯỜI KIỂM DUYỆT -> HỆ THỐNG THỰC THI
    # ====================================================================
    def open_script_editor(self):
        if hasattr(self, 'editor_window') and self.editor_window.winfo_exists():
            self.editor_window.focus()
            return

        self.editor_window = ctk.CTkToplevel(self)
        self.editor_window.title("Kiểm duyệt & Chỉnh sửa Kịch bản (Con người kiểm soát AI)")
        self.editor_window.geometry("750x650")
        self.editor_window.attributes('-topmost', True)
        
        # Căn giữa màn hình
        self.editor_window.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - 375
        y = self.winfo_y() + (self.winfo_height() // 2) - 325
        self.editor_window.geometry(f"+{x}+{y}")

        ctk.CTkLabel(self.editor_window, text="Vui lòng kiểm tra và sửa lại lời thoại cho phù hợp với trẻ trước khi tạo âm thanh:", font=("Arial", 16, "bold"), text_color="#E64A19").pack(pady=10)

        scroll_frame = ctk.CTkScrollableFrame(self.editor_window, width=700, height=500)
        scroll_frame.pack(pady=5, padx=10, fill="both", expand=True)

        self.editor_textboxes = []
        for i, page in enumerate(self.pending_pages):
            frame = ctk.CTkFrame(scroll_frame)
            frame.pack(pady=5, fill="x", padx=5)
            ctk.CTkLabel(frame, text=f"Trang {i+1}:", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(5,0))
            
            # --- CHỈ GIỮ LẠI ĐÚNG 3 DÒNG TẠO KHUNG CHỮ NÀY ---
            txt = ctk.CTkTextbox(frame, height=180, wrap="word", font=("Arial", 14))
            txt.pack(fill="x", padx=10, pady=5)
            txt.insert("0.0", page['text'])
            # -------------------------------------------------

            self.editor_textboxes.append((txt, page))

        btn_confirm = ctk.CTkButton(self.editor_window, text="✅ HOÀN TẤT & BẮT ĐẦU VẼ TRANH", height=45, font=("Arial", 14, "bold"), fg_color="green", command=self.start_media_process)
        btn_confirm.pack(pady=15)

    def start_media_process(self):
        # 1. CẬP NHẬT LẠI KỊCH BẢN SAU KHI CON NGƯỜI SỬA
        for txt_widget, page_data in self.editor_textboxes:
            edited_text = txt_widget.get("0.0", "end-1c").strip()
            page_data['text'] = edited_text
        
        self.editor_window.destroy()

        # 2. Bắt đầu luồng thực thi (Vẽ tranh & Thu âm)
        self.btn_create.configure(state="disabled")
        self.btn_generate_media.configure(state="disabled", text="⏳ Đang vẽ & thu âm...", fg_color="gray")
        self.status_lbl.configure(text="🎨 Đang khởi động Họa sĩ AI...", text_color="#3F51B5")

        threading.Thread(target=self.run_generate_media, daemon=True).start()

    def run_generate_media(self):
        try:
            self.pages = self.pending_pages
            hf_key = getattr(self, 'current_hf_key', '')
            image_ratio = getattr(self, 'current_image_ratio', "Ngang (16:9)")

            selected_label = self.voice_opt.get()
            voice_code = self.voice_map[selected_label]
            speed_val = self.speed_slider.get()

            painter = AI_Painter(hf_token=hf_key) 
            if not os.path.exists("data"): os.makedirs("data")
            session_id = int(time.time()) 
            
            total_pages = len(self.pages)
            for i, page in enumerate(self.pages):
                self.update_status(f"🎨 Đang vẽ trang {i+1}/{total_pages} (Khung hình: {image_ratio})...")
                img_path = os.path.abspath(f"data/{session_id}_scene_{i}.jpg")
                
                success = painter.generate_image(page['img_prompt'], img_path, ratio=image_ratio)
                if success: page['img_path'] = img_path
                else:
                    self.update_status(f"⚠️ Lỗi vẽ tranh. Server quá tải.")
                    return
                
                self.update_status(f"🎤 Đang thu âm trang {i+1}/{total_pages}...")
                audio_path = os.path.abspath(f"data/{session_id}_scene_{i}.mp3")
                voice_eng = VoiceEngine(voice_code, rate_value=speed_val)
                asyncio.run(voice_eng.generate_audio(page['text'], audio_path))
                page['audio_path'] = audio_path
            
            self.update_status("✅ Sáng tác hoàn tất!")
            self.current_page_idx = 0
            self.after(0, self.update_book_ui)
            
        except Exception as e:
            self.update_status(f"⚠️ Lỗi hệ thống: {e}")
        finally:
            self.after(0, lambda: self.btn_create.configure(state="normal", text="✍️ 1. VIẾT LẠI KỊCH BẢN"))
            self.after(0, lambda: self.btn_generate_media.configure(state="normal", text="🎨 2. DUYỆT & TẠO TRANH", fg_color="#4CAF50"))
            
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
            # Đang phát -> Chuyển sang TẠM DỪNG
            self.is_auto_playing = False
            self.is_paused = True # Cắm cờ đánh dấu đang tạm dừng
            try: pygame.mixer.music.pause() # Chỉ Pause, không Stop
            except: pass
            self.btn_play.configure(text="▶️ TIẾP TỤC", fg_color="green")
        else: 
            # Đang dừng -> Chuyển sang PHÁT TIẾP
            self.is_auto_playing = True
            self.btn_play.configure(text="⏹️ DỪNG", fg_color="red")
            
            # Nếu audio đang ở trạng thái Tạm dừng thì phát tiếp (Unpause)
            if getattr(self, 'is_paused', False):
                self.is_paused = False
                try: pygame.mixer.music.unpause()
                except: pass
                self.update_slider_loop() # Cho thanh trượt chạy tiếp
            else:
                self.play_audio_sequence() # Nếu đọc bài mới tinh thì phát từ đầu

    def stop_audio(self):
        # Lệnh này dùng để DỪNG HẲN (khi chuyển qua trang khác)
        self.is_auto_playing = False
        self.is_paused = False # Xóa cờ tạm dừng
        try: pygame.mixer.music.stop()
        except: pass
        self.btn_play.configure(text="▶️ ĐỌC TRUYỆN", fg_color="green")
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
                
                # Biến ghi nhớ "ĐIỂM XUẤT PHÁT" để tính toán khi tua
                self.start_offset = 0 
                pygame.mixer.music.play()
                self.update_slider_loop()
            except Exception as e: 
                print(f"Lỗi phát nhạc: {e}")
                self.stop_audio()
        else: 
            print(f"Không tìm thấy file: {audio}")
            self.stop_audio()

    def update_slider_loop(self):
        # Nếu đã hát xong và đang chạy Auto (không bị Pause) thì tự chuyển trang
        if not pygame.mixer.music.get_busy() and self.is_auto_playing and not getattr(self, 'is_paused', False):
            if self.current_page_idx < len(self.pages) - 1: 
                self.current_page_idx += 1
                self.update_book_ui()
                self.after(1000, self.play_audio_sequence)
            else: 
                self.stop_audio()
                self.status_lbl.configure(text="🎉 Đã đọc xong truyện!")
            return
            
        # Nếu đang phát VÀ bạn KHÔNG giữ chuột kéo thanh trượt -> Mới cập nhật UI
        if (pygame.mixer.music.get_busy() or getattr(self, 'is_paused', False)) and not self.is_dragging:
            try: 
                # Công thức mới: Thời gian thực = Điểm xuất phát + Thời gian đã chạy
                curr = getattr(self, 'start_offset', 0) + (pygame.mixer.music.get_pos() / 1000)
                if curr > self.audio_duration: curr = self.audio_duration
                if curr < 0: curr = 0
                
                self.slider.set(curr)
                self.lbl_current_time.configure(text=time.strftime('%M:%S', time.gmtime(curr)))
            except: pass
            
        # Duy trì vòng lặp
        if self.is_auto_playing or pygame.mixer.music.get_busy(): 
            self.after(500, self.update_slider_loop)

    # ==== 2 HÀM MỚI ĐỂ XỬ LÝ SỰ KIỆN KÉO THẢ THANH TRƯỢT ====
    def on_slider_press(self, event):
        # Đánh dấu đang giữ chuột -> Tạm ngưng cập nhật tự động
        self.is_dragging = True

    def on_slider_release(self, event):
        # Nhả chuột ra -> Tua nhạc
        self.is_dragging = False
        if not self.pages: return
        
        value = self.slider.get() # Lấy vị trí thời gian bạn vừa thả tay
        page = self.pages[self.current_page_idx]
        audio = page.get('audio_path', '')
        
        if os.path.exists(audio):
            try:
                # Cách chuẩn nhất để tua MP3: Load lại và play từ vị trí bạn chọn
                pygame.mixer.music.load(audio)
                pygame.mixer.music.play(start=value)
                
                # Cập nhật mốc "điểm xuất phát" mới
                self.start_offset = value 
                self.lbl_current_time.configure(text=time.strftime('%M:%S', time.gmtime(value)))
                
                # Nếu bạn đang Tạm dừng mà kéo tua, thì tua xong vẫn phải nằm ở trạng thái Tạm dừng
                if getattr(self, 'is_paused', False):
                    pygame.mixer.music.pause()
            except Exception as e:
                print(f"Lỗi tua nhạc: {e}")

    def manual_flip(self, direction):
        self.stop_audio()
        self.current_page_idx += direction
        self.update_book_ui()

    def update_status(self, text):
        self.after(0, lambda: self.status_lbl.configure(text=text))
        
   # ================= CÁC HÀM XUẤT VIDEO (MỚI) =================
    def export_video(self):
        if not self.pages:
            self.update_status("⚠️ Chưa có truyện để xuất video!")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Lưu Video MP4",
            defaultextension=".mp4", 
            filetypes=[("MP4 Video", "*.mp4")]
        )
        if not file_path: 
            return

        self.btn_export.configure(state="disabled", text="⏳ Đang render...")
        self.update_status("🎬 Đang chuẩn bị xuất video...")

        # --- TẠO CỬA SỔ POPUP HIỂN THỊ TIẾN TRÌNH ---
        self.progress_window = ctk.CTkToplevel(self)
        self.progress_window.title("Đang render Video")
        self.progress_window.geometry("400x150")
        self.progress_window.attributes('-topmost', True) # Ép luôn nổi trên cùng
        self.progress_window.transient(self) 
        
        # Căn giữa màn hình
        self.progress_window.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - 200
        y = self.winfo_y() + (self.winfo_height() // 2) - 75
        self.progress_window.geometry(f"+{x}+{y}")

        # Các thành phần trong popup
        self.lbl_prog_title = ctk.CTkLabel(self.progress_window, text="Đang ghép ảnh và âm thanh...", font=("Arial", 14))
        self.lbl_prog_title.pack(pady=(20, 10))
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_window, width=300, fg_color="#E0E0E0", progress_color="#4CAF50")
        self.progress_bar.pack(pady=5)
        self.progress_bar.set(0) # Bắt đầu từ 0%
        
        self.lbl_percent = ctk.CTkLabel(self.progress_window, text="0%", font=("Arial", 16, "bold"), text_color="#FF5722")
        self.lbl_percent.pack()

        # Chạy tiến trình ngầm
        threading.Thread(target=self.run_export_video, args=(file_path,), daemon=True).start()

    # --- HÀM NÀY ĐÓNG VAI TRÒ "NHẬN ĐIỆN TÍN" TỪ VIDEO MAKER GỬI VỀ ---
    def update_export_progress(self, msg, percent):
        # Dùng self.after để an toàn cho giao diện khi chạy đa luồng
        self.after(0, self._safe_update_progress, msg, percent)

    def _safe_update_progress(self, msg, percent):
        if hasattr(self, 'progress_window') and self.progress_window.winfo_exists():
            self.lbl_prog_title.configure(text=msg)
            self.progress_bar.set(percent / 100.0) # Thanh trượt nhận giá trị 0.0 -> 1.0
            self.lbl_percent.configure(text=f"{int(percent)}%")

    def run_export_video(self, file_path):
        maker = VideoMaker()
        
        # CHÚ Ý: Ta truyền thêm hàm update_export_progress cho VideoMaker
        # Để nó biết đường gửi % về cập nhật lên màn hình
        success = maker.create_video(self.pages, file_path, progress_callback=self.update_export_progress)
        
        # Xong việc thì đóng cửa sổ
        self.after(0, self.finish_export, success, file_path)

    def finish_export(self, success, file_path):
        # Đóng cửa sổ popup
        if hasattr(self, 'progress_window') and self.progress_window.winfo_exists():
            self.progress_window.destroy()
            
        if success:
            self.update_status(f"🎉 Đã xuất Video: {os.path.basename(file_path)}")
        else:
            self.update_status("❌ Lỗi xuất video. Xem Terminal.")
            
        self.btn_export.configure(state="normal", text="🎬 Xuất MP4")

if __name__ == "__main__":
    app = App()
    app.mainloop()