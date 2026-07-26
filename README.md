
# Accident Scene Reconstruction

Project này xây dựng một hệ thống phân tích và tái tạo hiện trường tai nạn giao thông bằng cách kết hợp:

1. Nhận diện đối tượng bằng YOLO11 / YOLOv11
2. Quá trình lọc dữ liệu, đánh nhãn và huấn luyện mô hình
3. Giao diện xem và kiểm tra cảnh 3D bằng point cloud / scene viewer
4. Hỗ trợ đo lường tỷ lệ scale và kiểm tra dữ liệu 3D

Mục tiêu của hệ thống là hỗ trợ phát hiện các tình huống tai nạn, xác định vị trí vật thể trong cảnh, và tái dựng không gian hiện trường để phục vụ phân tích, giám sát và báo cáo.

---

## Tóm tắt kiến trúc

Project được chia thành 2 phần chính:

- Phần 1: Mô hình phát hiện và phân loại sự cố bằng YOLO
  - Tham chiếu chi tiết trong [Yolo-VR-main/README.md](Yolo-VR-main/README.md)
  - Dữ liệu mô hình và các script huấn luyện / suy luận nằm trong thư mục [Yolo-VR-main](Yolo-VR-main)

- Phần 2: Xem và kiểm tra cảnh 3D / point cloud
  - Giao diện viewer: [3D/viewer.html](3D/viewer.html)
  - Công cụ kiểm tra môi trường: [3D/diagnostics.html](3D/diagnostics.html)
  - Script kiểm tra point cloud: [3D/check_pointcloud.py](3D/check_pointcloud.py)
  - Script hiệu chỉnh scale: [scale_calibration.py](scale_calibration.py)

---

## Cấu trúc thư mục

```text
accident-scene-reconstruction/
├── 3D/                          # Giao diện 3D, scene viewer, point cloud
│   ├── viewer.html
│   ├── diagnostics.html
│   ├── accident_scene.scene3d
│   └── lib/
├── Yolo-VR-main/                # Module YOLO11 / training / inference
│   ├── scripts/
│   ├── configs/
│   ├── src/
│   ├── data/
│   └── README.md
├── data-scene/                  # Bộ dữ liệu ảnh gốc
├── data-scene-filtered/         # Dữ liệu đã lọc blur / chọn lọc
├── scale_calibration.py         # Hiệu chỉnh scale trong không gian 3D
├── test.py                      # Script tiền xử lý / chọn ảnh
└── README.md                    # Mô tả tổng quan project
```

---

## Quy trình làm việc của project

Project này thường đi theo flow sau:

1. Thu thập ảnh / video hiện trường tai nạn
2. Lọc ảnh mờ, chọn mẫu phù hợp
3. Chuẩn bị dữ liệu theo định dạng YOLO
4. Kiểm tra tính hợp lệ của annotation
5. Huấn luyện mô hình phát hiện
6. Chạy suy luận trên ảnh / video / webcam
7. Dùng viewer 3D để hiển thị, kiểm tra và phân tích cảnh

---

## Phần 1: YOLO Detection Pipeline

Phần này tập trung vào việc huấn luyện và chạy các mô hình phát hiện tai nạn giao thông. Dữ liệu được tổ chức theo từng dataset rõ ràng và có thể chạy riêng lẻ hoặc đồng bộ.

### Mục tiêu

- Phát hiện sự cố trong cảnh
- Nhận diện các đối tượng liên quan: người, xe máy, vật thể fallen, mũ bảo hiểm, fire/smoke, hư hỏng xe
- Tạo cơ sở dữ liệu cảnh báo và phân tích hiện trường tai nạn

### Cấu hình dữ liệu

Để train đúng, dataset cần được đặt ở đúng vị trí trong thư mục [Yolo-VR-main/data/processed](Yolo-VR-main/data/processed) theo tên chuẩn:

- `CarDD-DamageDetection`
- `FireSmokeAccident`
- `Custom-Accident-Scene`
- `MotorcycleDetection`
- `MotorcycleHelmet`
- `BrokenMotorcycles`

Mỗi dataset cần có cấu trúc tối thiểu:

- `train/images/`
- `train/labels/`
- `valid/images/`
- `valid/labels/`
- `data.yaml`

---

## Phần 2: 3D Reconstruction / Scene Viewer

Phần 3D hỗ trợ xem cảnh hiện trường dưới dạng point cloud hoặc scene model. Đây là bước giúp người dùng kiểm tra, phát hiện không gian thực, và đo lường theo tỷ lệ chuẩn.

### Các file chính

- [3D/viewer.html](3D/viewer.html): giao diện xem scene 3D
- [3D/diagnostics.html](3D/diagnostics.html): công cụ chẩn đoán / kiểm tra viewer
- [3D/accident_scene.scene3d](3D/accident_scene.scene3d): file scene model
- [3D/check_pointcloud.py](3D/check_pointcloud.py): kiểm tra point cloud
- [scale_calibration.py](scale_calibration.py): hiệu chỉnh độ dài thực tế trong model

### Mục đích

- Xem dữ liệu hiện trường dưới dạng mô hình 3D
- Kiểm tra độ ổn định của point cloud
- Đo tỷ lệ thực tế bằng thước mẫu
- Hỗ trợ tái dựng không gian cảnh tai nạn

---

## Cài đặt môi trường

Khuyến nghị tạo môi trường ảo Python riêng trước khi chạy.

### Cài đặt dependency cho YOLO

```bash
cd Yolo-VR-main
pip install -r requirements.txt
```

### Cài đặt gói hỗ trợ 3D

Nếu bạn chạy phần viewer / point cloud, cần đảm bảo các package Open3D / NumPy / matplotlib được cài sẵn trong môi trường hiện tại.

---

## Kiểm tra dữ liệu trước khi train

Trước khi bắt đầu huấn luyện, cần chạy validate để đảm bảo dữ liệu không có lỗi annotation.

Ví dụ:

```bash
cd Yolo-VR-main
python scripts/validate_data.py --dataset custom_scene
python scripts/validate_data.py --dataset cardd
python scripts/validate_data.py --dataset fire_smoke
python scripts/validate_data.py --dataset motorcycle_detection
python scripts/validate_data.py --dataset motorcycle_helmet
python scripts/validate_data.py --dataset broken_motorcycles
```

Nếu tất cả kết quả đều hợp lệ thì mới nên tiến hành huấn luyện.

---

## Huấn luyện mô hình

Các tham số huấn luyện được lưu ở file YAML trong thư mục config. Người dùng không cần sửa code Python mà chỉ cần điều chỉnh config phù hợp.

### Huấn luyện toàn bộ

```bash
cd Yolo-VR-main
python scripts/train.py
```

### Huấn luyện từng model riêng lẻ

```bash
python scripts/train.py --only custom_scene
python scripts/train.py --only cardd
python scripts/train.py --only fire_smoke
python scripts/train.py --only motorcycle_detection
python scripts/train.py --only motorcycle_helmet
python scripts/train.py --only broken_motorcycles
```

---

## Suy luận / Inference

Sau khi huấn luyện, chạy mô hình trên ảnh, video hoặc webcam.

```bash
python scripts/infer.py --source test_image.jpg --model cardd
python scripts/infer.py --source video.mp4 --model broken_motorcycles --show
python scripts/infer.py --source 0 --model all --show
```

Kết quả sẽ được lưu vào thư mục `runs/predict/` hoặc theo cấu hình output của YOLO.

---

## Workflow đề xuất cho toàn project

Một workflow gợi ý để chạy project chuẩn là:

1. Chuẩn bị dữ liệu ảnh vào data-scene
2. Lọc ảnh bằng test.py
3. Chuyển dữ liệu phù hợp vào processed
4. Chạy validate_data.py
5. Chạy train.py
6. Chạy infer.py
7. Mở viewer.html để xem cảnh 3D
8. Nếu cần đo kích thước thực tế, dùng scale_calibration.py

---

## Ưu điểm của project

- Tách rõ dữ liệu, cấu hình và code
- Dễ mở rộng thêm dataset mới
- Hỗ trợ huấn luyện nhiều model song song
- Có khả năng phân tích hiện trường cả bằng ảnh và không gian 3D
- Dễ tích hợp vào quy trình MLOps / nghiên cứu / demo

---

## Lưu ý quan trọng

- Tên folder dataset phải khớp chính xác với quy định trong README.md
- Không nên bỏ qua bước validate dữ liệu trước khi train
- Khi chạy viewer 3D, cần đảm bảo file scene hoặc point cloud tồn tại và tương thích
- Nếu gặp lỗi liên quan đến Open3D / Three.js / browser, hãy chạy diagnostics.html trước

---

## Kết luận

Project này không chỉ là một repo YOLO đơn thuần, mà là một hệ thống kết hợp:

- Phân tích hiện trường tai nạn bằng computer vision
- Phát hiện đối tượng và sự cố bằng mô hình học sâu
- Tái dựng và kiểm tra cảnh sự cố trong không gian 3D

Đây là một nền tảng phù hợp cho việc nghiên cứu, demo và phát triển hệ thống nhận diện tai nạn giao thông theo hướng ứng dụng thực tế.

---

## Tài liệu tham khảo

- README.md
- viewer.html
- diagnostics.html
- scale_calibration.py


