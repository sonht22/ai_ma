import os
import sys
import time
import zipfile
import requests
import subprocess

# Thông tin GitHub của bạn
GITHUB_USER = "sonht22" 
GITHUB_REPO = "ai_ma"

def start_update():
    print("=======================================")
    print("   TRÌNH CẬP NHẬT TRUYỆN TRANH AI      ")
    print("=======================================")
    print("⚠️ Vui lòng ĐẢM BẢO phần mềm chính đã được TẮT trước khi cập nhật!")
    print("...")
    time.sleep(2)

    api_url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/latest"

    try:
        print("🔍 Đang tìm phiên bản mới nhất trên máy chủ GitHub...")
        # Thêm timeout để chống treo mạng
        response = requests.get(api_url, timeout=15) 
        
        if response.status_code == 200:
            data = response.json()
            version = data.get("tag_name", "Không rõ")
            assets = data.get("assets", [])
            
            if len(assets) > 0:
                download_url = assets[0]["browser_download_url"]
                print(f"⬇️ Đã tìm thấy bản {version}! Bắt đầu tải về...")
                
                # --- TÍNH NĂNG MỚI: TẢI THEO CHUNK VÀ HIỂN THỊ PHẦN TRĂM ---
                r = requests.get(download_url, stream=True, timeout=15)
                total_size = int(r.headers.get('content-length', 0))
                block_size = 1024 * 1024 # Tải từng 1MB
                downloaded = 0
                
                with open("update_temp.zip", "wb") as f:
                    for data in r.iter_content(block_size):
                        f.write(data)
                        downloaded += len(data)
                        if total_size > 0:
                            percent = int((downloaded / total_size) * 100)
                            # Hiệu ứng in đè lên dòng cũ để % chạy liên tục
                            print(f"\r⏳ Tiến độ: {percent}% ({downloaded//(1024*1024)}MB / {total_size//(1024*1024)}MB)", end="")
                
                print("\n📦 Tải xong! Đang giải nén và ghi đè hệ thống...")
                # ------------------------------------------------------------

                with zipfile.ZipFile("update_temp.zip", 'r') as zip_ref:
                    zip_ref.extractall(".") 
                
                os.remove("update_temp.zip")
                print(f"✅ Cập nhật thành công lên bản {version}!")
                time.sleep(2)
                
                if os.path.exists("TruyenTranhAI.exe"):
                    print("🚀 Đang khởi động lại phần mềm...")
                    subprocess.Popen(["TruyenTranhAI.exe"])
                
            else:
                print("⚠️ Phiên bản mới nhất trên GitHub chưa được đính kèm file.")
        else:
            print("⚠️ Không tìm thấy bản cập nhật.")
            
    except Exception as e:
        print(f"\n❌ Lỗi mạng hoặc lỗi hệ thống: {e}")

    print("\nẤn Enter để thoát...")
    input()

if __name__ == "__main__":
    start_update()