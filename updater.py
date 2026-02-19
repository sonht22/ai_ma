import os
import sys
import time
import zipfile
import requests
import subprocess

# 👇 ĐIỀN THÔNG TIN GITHUB CỦA BẠN VÀO ĐÂY 👇
# 👇 ĐIỀN THÔNG TIN GITHUB CỦA BẠN VÀO ĐÂY 👇
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
        response = requests.get(api_url)
        
        if response.status_code == 200:
            data = response.json()
            version = data.get("tag_name", "Không rõ")
            assets = data.get("assets", [])
            
            if len(assets) > 0:
                download_url = assets[0]["browser_download_url"]
                print(f"⬇️ Đã tìm thấy bản {version}! Đang tải về (có thể mất vài phút)...")
                
                # Tải file zip về
                r = requests.get(download_url, allow_redirects=True)
                with open("update_temp.zip", "wb") as f:
                    f.write(r.content)
                
                print("📦 Đang giải nén và ghi đè hệ thống...")
                with zipfile.ZipFile("update_temp.zip", 'r') as zip_ref:
                    zip_ref.extractall(".") # Giải nén đè thẳng vào thư mục hiện tại
                
                # Xóa file zip rác sau khi giải nén xong
                os.remove("update_temp.zip")
                print(f"✅ Cập nhật thành công lên bản {version}!")
                time.sleep(2)
                
                # Tự động bật lại phần mềm chính
                if os.path.exists("TruyenTranhAI.exe"):
                    print("🚀 Đang khởi động lại phần mềm...")
                    subprocess.Popen(["TruyenTranhAI.exe"])
                
            else:
                print("⚠️ Phiên bản mới nhất trên GitHub chưa được đính kèm file.")
        else:
            print("⚠️ Không tìm thấy bản cập nhật. (Kho GitHub có thể đang để Private/Bí mật, hãy chuyển sang Public).")
            
    except Exception as e:
        print(f"❌ Lỗi mạng hoặc lỗi hệ thống: {e}")

    print("\nẤn Enter để thoát...")
    input()

if __name__ == "__main__":
    start_update()