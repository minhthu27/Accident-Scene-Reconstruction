# YOLO11 Accident Scene Reconstruction (Enterprise MLOps Edition)

He thong nhan dien va tai tao hien truong tai nan giao thong su dung **YOLO11** duoc xay dung theo tieu chuan **Advanced MLOps (Enterprise-grade)**. Kien truc nay tach biet hoan toan Data, Configuration (YAML) va Source Code, di kem he thong nhat ky (Logging) chuyen nghiep.

---

## Cau truc thu muc (Enterprise Layout)

```text
Yolo & VR/
|
|-- data/                            # [Chuan MLOps] Thu muc chua du lieu
|   |-- raw/                         # Data chua xu ly
|   +-- processed/                   # Data da qua tien xu ly, gan nhan YOLO
|       |-- CarDD-DamageDetection/   # Hu hong o to (6 classes)
|       |-- FireSmokeAccident/       # Lua/khoi/tai nan (5 classes)
|       |-- Custom-Accident-Scene/   # Hien truong tu thu thap (6 classes)
|       |-- MotorcycleDetection/     # Xe may (6 classes)
|       |-- MotorcycleHelmet/        # Mu bao hiem (2 classes)
|       +-- BrokenMotorcycles/       # Xe may do/tai nan (4 classes)
|
|-- configs/                         # Quan ly cau hinh tap trung (YAML)
|   |-- system.yaml                  # Duong dan he thong
|   |-- model/                       # Khai bao cac mo hinh
|   |   |-- cardd.yaml
|   |   |-- fire_smoke.yaml
|   |   |-- custom_scene.yaml
|   |   |-- motorcycle_detection.yaml
|   |   |-- motorcycle_helmet.yaml
|   |   +-- broken_motorcycles.yaml
|   +-- training/                    # Sieu tham so
|       |-- default.yaml             # Cho dataset lon (CarDD, FireSmoke, MotorcycleDetection)
|       +-- custom_finetune.yaml     # Cho dataset nho (Custom, Helmet, Broken)
|
|-- src/                             # Ma nguon Core Framework
|   |-- core/                        # Xu ly loi (Trainer, Predictor, Config Parser)
|   +-- utils/                       # Tien ich bo tro (Logger, Visualizer)
|
|-- scripts/                         # Khu vuc chua lenh chay chinh
|   |-- validate_data.py             # Kiem tra tinh toan ven dataset truoc khi train
|   |-- train.py                     # Kich ban huan luyen tong hop
|   +-- infer.py                     # Kich ban chay nhan dien du doan
|
|-- runs/                            # Noi luu Weights va ket qua Inference
|-- logs/                            # Noi luu file nhat ky he thong (.log)
|-- archive_legacy/                  # Chua cac script tu phien ban cu
+-- requirements.txt                 # Danh sach thu vien Python
```

---

## QUAN TRONG - DAT TEN DATASET

- Moi dataset tai tu **Kaggle** hoac **Roboflow** ve phai duoc giai nen va dat vao `data/processed/` voi ten thu muc **CHINH XAC** nhu ben duoi:

  1. `data/processed/CarDD-DamageDetection` - Dataset hu hong o to
  2. `data/processed/FireSmokeAccident` - Dataset lua/khoi/tai nan
  3. `data/processed/Custom-Accident-Scene` - Dataset hien truong tu thu thap
  4. `data/processed/MotorcycleDetection` - Dataset xe may
  5. `data/processed/MotorcycleHelmet` - Dataset mu bao hiem
  6. `data/processed/BrokenMotorcycles` - Dataset xe may do/tai nan

- Neu ten thu muc **SAI** so voi tren - he thong se **KHONG TIM THAY** dataset va bao loi khi train.
- Cau truc ben trong moi dataset **BAT BUOC** phai co:
  - `train/images/` va `train/labels/`
  - `valid/images/` va `valid/labels/` (hoac `val/`)
  - `test/images/` va `test/labels/` (tuy chon)
  - `data.yaml`

---

## Cai dat moi truong

```bash
pip install -r requirements.txt
```

---

## QUAN TRONG - KIEM TRA DATASET TRUOC KHI TRAIN

- **LUON LUON** chay lenh kiem tra (Health Check) dataset **TRUOC** khi bat dau huan luyen.
- Script se quet toan bo:
  1. Anh co file `.txt` nhan tuong ung khong
  2. Class ID co vuot qua gioi han khong
  3. Toa do bounding box co nam ngoai khoang `[0, 1]` khong

```bash
# Kiem tra tung dataset
python scripts/validate_data.py --dataset cardd
python scripts/validate_data.py --dataset fire_smoke
python scripts/validate_data.py --dataset custom_scene
python scripts/validate_data.py --dataset motorcycle_detection
python scripts/validate_data.py --dataset motorcycle_helmet
python scripts/validate_data.py --dataset broken_motorcycles
```

- Neu script bao **"TAT CA DU LIEU HOP LE"** - ban moi nen chay train.
- Neu bao loi - sua data truoc, chay lai validate cho den khi sach.

---

## Huan Luyen (Training)

- Moi cau hinh (Epochs, Batch size, Augmentations) da duoc chuyen ra file `configs/` - nguoi khong biet code van chinh duoc.

### Lenh train:

```bash
# 1 - Huan luyen TAT CA 6 model
python scripts/train.py

# 2 - Chi huan luyen 1 dataset cu the
python scripts/train.py --only custom_scene
python scripts/train.py --only cardd
python scripts/train.py --only fire_smoke
python scripts/train.py --only motorcycle_detection
python scripts/train.py --only motorcycle_helmet
python scripts/train.py --only broken_motorcycles
```

### QUAN TRONG - CAU HINH TRAINING

- Tham so training **KHONG** nam trong code Python - chung nam o file YAML:
  - `configs/training/default.yaml` - cho CarDD, FireSmoke, MotorcycleDetection
  - `configs/training/custom_finetune.yaml` - cho Custom Scene, MotorcycleHelmet, BrokenMotorcycles (Augmentation nhe hon)
- Muon thay doi epochs, batch size, learning rate - **SUA FILE YAML**, khong can sua code.
- Ket qua weights luu tai:

| Dataset key | Weights path |
|---|---|
| cardd | `runs/cardd/train/weights/best.pt` |
| fire_smoke | `runs/fire_smoke/train/weights/best.pt` |
| custom_scene | `runs/custom_scene/train/weights/best.pt` |
| motorcycle_detection | `runs/motorcycle_detection/train/weights/best.pt` |
| motorcycle_helmet | `runs/motorcycle_helmet/train/weights/best.pt` |
| broken_motorcycles | `runs/broken_motorcycles/train/weights/best.pt` |

---

## Du doan (Inference)

```bash
python scripts/infer.py --source <anh/video/cam> --model <chon model>
```

### QUAN TRONG - CAC TUY CHON MODEL

| Gia tri `--model` | Mo ta | Weights tu dong tim tai |
|---|---|---|
| `cardd` | Hu hong xe (xuoc, mop, vo kinh) | `runs/cardd/train/weights/best.pt` |
| `fire_smoke` | Chay no, boi canh tai nan | `runs/fire_smoke/train/weights/best.pt` |
| `custom_scene` | Nguoi bi nan, xe do, mu BH, thuoc, mau | `runs/custom_scene/train/weights/best.pt` |
| `motorcycle_detection` | Nhan dien xe may | `runs/motorcycle_detection/train/weights/best.pt` |
| `motorcycle_helmet` | Mu bao hiem / khong mu | `runs/motorcycle_helmet/train/weights/best.pt` |
| `broken_motorcycles` | Xe may do, nguoi bi nan | `runs/broken_motorcycles/train/weights/best.pt` |
| `all` / `both` | Chay qua TAT CA model da train | Tu quet toan bo |

### Vi du su dung:

```bash
# 1 - Du doan hu hong xe tren 1 anh
python scripts/infer.py --source test_image.jpg --model cardd

# 2 - Test xe may do/nguoi bi nan tren video
python scripts/infer.py --source video.mp4 --model broken_motorcycles --show

# 3 - Chay TAT CA model qua webcam truc tiep
python scripts/infer.py --source 0 --model all --show

# 4 - Dung weights tuy chinh (bo qua --model)
python scripts/infer.py --source anh.jpg --weights runs/custom_scene/train/weights/best.pt
```

- Ket qua se duoc tu dong dan nhan va luu tai thu muc `runs/predict/`

---

## Go Loi Bang File Nhat Ky (Logs)

- Moi lan chay lenh - file nhat ky se tu dong ghi vao `logs/`
- Vi du: `logs/yolo_project_20260331.log`
- Neu gap su co - mo file log gan nhat thay vi phai chay lai tu dau

---

## Tong hop 6 Dataset va 29 Classes

| Dataset | So anh | Classes |
|---|---|---|
| FireSmokeAccident | 25,425 | accident, vehicle, pothole, fire, smoke |
| CarDD-DamageDetection | 4,000 | dent, scratch, crack, glass shatter, lamp broken, tire flat |
| Custom-Accident-Scene | 258 | person-acident, motorcycle_fallen, helmet, ruler, fallen_object, blood |
| MotorcycleDetection | 6,617 | helmet, motorcycle, plate, traffic-green, traffic-red, walk-lane |
| MotorcycleHelmet | 1,268 | helmet, no helmet |
| BrokenMotorcycles | 370 | motorcycle, motorcycle_accident, people, people_accident |
