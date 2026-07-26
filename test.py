import cv2, os, shutil
import numpy as np

# ===== CHỈ CẦN SỬA 2 DÒNG NÀY =====
RAW_DIR    = r"D:\workspace\python\cndpt\accident-scene-reconstruction\data-scene"   # thư mục chứa 784 ảnh gốc
OUTPUT_DIR = r"D:\workspace\python\cndpt\accident-scene-reconstruction\data-scene-filtered"    # thư mục output — tự tạo nếu chưa có
# =====================================

TARGET         = 200   # số ảnh muốn giữ lại
BLUR_THRESHOLD = 80    # giảm xuống 50 nếu lọc quá nhiều

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Bước 1: Quét tất cả ảnh
all_files = sorted([
    f for f in os.listdir(RAW_DIR)
    if f.lower().endswith(('.jpg', '.jpeg', '.png', '.heic'))
])
print(f"Tổng ảnh gốc: {len(all_files)}")

# Bước 2: Lọc ảnh blur
kept = []
for i, fname in enumerate(all_files):
    path = os.path.join(RAW_DIR, fname)
    img  = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"  Bỏ qua (không đọc được): {fname}")
        continue
    score = cv2.Laplacian(img, cv2.CV_64F).var()
    if score >= BLUR_THRESHOLD:
        kept.append((fname, score))
    if (i+1) % 50 == 0:
        print(f"  Đã xử lý {i+1}/{len(all_files)}...")

print(f"Sau lọc blur: còn {len(kept)} ảnh")

# Bước 3: Lấy đều ~200 ảnh
if len(kept) <= TARGET:
    selected = [f for f, s in kept]
    print(f"Giữ tất cả {len(selected)} ảnh (ít hơn target {TARGET})")
else:
    indices  = np.linspace(0, len(kept)-1, TARGET, dtype=int)
    selected = [kept[i][0] for i in indices]
    print(f"Lấy đều {len(selected)} ảnh từ {len(kept)} ảnh hợp lệ")

# Bước 4: Copy sang thư mục output
for fname in selected:
    shutil.copy(
        os.path.join(RAW_DIR, fname),
        os.path.join(OUTPUT_DIR, fname)
    )

print(f"\nHOÀN TẤT — {len(selected)} ảnh đã lưu vào:")
print(f"  {OUTPUT_DIR}")
print(f"\nBước tiếp: upload thư mục này lên Drive vào data-scene/images/")