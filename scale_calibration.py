# scale_calibration.py — chạy trên máy local
import numpy as np
import open3d as o3d

# Load file ply
pcd = o3d.io.read_point_cloud(r"đường\dẫn\point_cloud.ply")
o3d.visualization.draw_geometries(
    [pcd],
    window_name="Click 2 đầu thước để đo",
    width=1280, height=720
)

# Sau khi xác định tọa độ 2 đầu thước trong viewer:
# Đo khoảng cách 2 điểm trong model
p1 = np.array([x1, y1, z1])  # tọa độ đầu 1 của thước
p2 = np.array([x2, y2, z2])  # tọa độ đầu 2 của thước

dist_in_model = np.linalg.norm(p1 - p2)
real_length   = 1.0  # thước dài 1 mét thực tế

scale_factor = real_length / dist_in_model
print(f"Scale factor: {scale_factor:.6f} (mét/unit)")
print(f"Tức là 1 unit trong model = {1/scale_factor*100:.2f} cm thực tế")