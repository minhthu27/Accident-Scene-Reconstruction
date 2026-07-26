#!/usr/bin/env python3
"""
3D Scene File Analyzer - Công cụ phân tích file cảnh quay
Kiểm tra: Kích thước, Định dạng, Số điểm, Chất lượng
"""

import os
import struct
import sys
from pathlib import Path

class Colors:
    """Terminal colors"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}╔{'═'*70}╗{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}║ {text:<68} ║{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}╚{'═'*70}╝{Colors.END}\n")

def print_section(text):
    print(f"{Colors.BOLD}{Colors.BLUE}📊 {text}{Colors.END}")
    print(f"{Colors.BLUE}{'─'*70}{Colors.END}")

def print_info(label, value, unit=""):
    print(f"  {label:<30} {Colors.GREEN}{value:>20}{Colors.END} {unit}")

def print_warning(text):
    print(f"  {Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_error(text):
    print(f"  {Colors.RED}❌ {text}{Colors.END}")

def print_success(text):
    print(f"  {Colors.GREEN}✅ {text}{Colors.END}")

def format_size(bytes_size):
    """Format bytes to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.2f} TB"

def analyze_scene3d(filepath):
    """Analyze .scene3d file"""
    if not os.path.exists(filepath):
        print_error(f"File không tìm thấy: {filepath}")
        return None
    
    file_size = os.path.getsize(filepath)
    print_section("Thông Tin File")
    print_info("Tên file", os.path.basename(filepath))
    print_info("Đường dẫn", filepath)
    print_info("Kích thước", format_size(file_size))
    print_info("Kích thước (byte)", f"{file_size:,}")
    
    # Check magic bytes
    try:
        with open(filepath, 'rb') as f:
            magic = f.read(4)
            if magic == b'ASR3':
                print_success("Định dạng: .scene3d (Valid)")
                
                # Try to read metadata
                try:
                    f.seek(4)
                    # Read version (optional)
                    version_bytes = f.read(4)
                    if len(version_bytes) == 4:
                        version = struct.unpack('<I', version_bytes)[0]
                        print_info("Phiên bản", f"{version}")
                    
                    # Try to estimate point count from file size
                    # Rough estimate: each point ~16-20 bytes (x,y,z,rgb)
                    remaining_size = file_size - f.tell()
                    estimated_points = remaining_size / 16  # Conservative estimate
                    print_info("Điểm ước tính", f"{int(estimated_points):,}")
                    
                except:
                    pass
                    
            else:
                print_error(f"Định dạng không hợp lệ (Magic: {magic})")
                return None
                
    except Exception as e:
        print_error(f"Lỗi đọc file: {e}")
        return None
    
    return file_size

def analyze_ply(filepath):
    """Analyze .ply file"""
    if not os.path.exists(filepath):
        print_error(f"File không tìm thấy: {filepath}")
        return None
    
    file_size = os.path.getsize(filepath)
    print_section("Thông Tin File")
    print_info("Tên file", os.path.basename(filepath))
    print_info("Đường dẫn", filepath)
    print_info("Kích thước", format_size(file_size))
    print_info("Kích thước (byte)", f"{file_size:,}")
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            first_line = f.readline().strip()
            if first_line != 'ply':
                print_error("Định dạng không phải PLY")
                return None
            
            print_success("Định dạng: PLY (Valid)")
            
            vertex_count = 0
            is_binary = False
            
            for line in f:
                line = line.strip()
                if line.startswith('element vertex'):
                    parts = line.split()
                    if len(parts) >= 3:
                        vertex_count = int(parts[2])
                        print_info("Số điểm (Vertices)", f"{vertex_count:,}")
                elif line.startswith('format'):
                    if 'binary' in line:
                        is_binary = True
                        if 'little_endian' in line:
                            print_info("Định dạng", "Binary (Little Endian)")
                        else:
                            print_info("Định dạng", "Binary (Big Endian)")
                    else:
                        print_info("Định dạng", "ASCII")
                elif line == 'end_header':
                    break
    
    except Exception as e:
        print_error(f"Lỗi đọc file: {e}")
        return None
    
    return file_size

def analyze_quality(file_size, point_count=None):
    """Analyze and provide recommendations"""
    print_section("Đánh Giá Chất Lượng")
    
    # File size assessment
    print_info("Kích thước file", f"{format_size(file_size)}", "")
    
    if file_size < 50 * 1024 * 1024:  # < 50MB
        print_warning("File nhỏ - Số điểm có thể thấp")
    elif file_size < 500 * 1024 * 1024:  # < 500MB
        print_success("Kích thước bình thường")
    elif file_size < 2 * 1024 * 1024 * 1024:  # < 2GB
        print_success("Kích thước lớn - Chi tiết tốt")
    else:
        print_warning("File rất lớn - Có thể tải chậm")
    
    print()

def provide_recommendations(filepath):
    """Provide optimization recommendations"""
    print_section("Khuyến Nghị Cải Thiện")
    
    file_size = os.path.getsize(filepath)
    
    print(f"{Colors.BOLD}Nếu chất lượng không đủ:{Colors.END}")
    print()
    
    if file_size < 100 * 1024 * 1024:  # < 100MB
        print(f"  {Colors.YELLOW}1️⃣  File quá nhỏ (< 100MB){Colors.END}")
        print(f"     • Số điểm có thể rất ít (< 1 triệu)")
        print(f"     • {Colors.BOLD}GIẢI PHÁP:{Colors.END} Re-export với mật độ điểm cao hơn")
        print()
        print(f"     CloudCompare:")
        print(f"       1. Mở file trong CloudCompare")
        print(f"       2. Filter → Subsample")
        print(f"       3. Giảm khoảng cách (ví dụ: 0.01)")
        print(f"       4. Export lại")
        print()
        print(f"     COLMAP:")
        print(f"       • Tăng resolution hoặc giảm voxel size")
        print()
        
    else:
        print(f"  {Colors.GREEN}✅ Kích thước file bình thường{Colors.END}")
        print(f"     • Số điểm có thể đủ (1M+)")
        print(f"     • {Colors.BOLD}GIẢI PHÁP:{Colors.END} Tăng cỡ điểm trong viewer")
        print()
        print(f"     3 Cách trong thứ tự ưu tiên:")
        print(f"       1. Thanh trượt UI - Kéo cỡ điểm từ 2→6")
        print(f"       2. Console - Paste code optimize")
        print(f"       3. Sửa viewer.html - Vĩnh viễn")
        print()
    
    print(f"{Colors.BOLD}Bước kiểm tra nhanh:{Colors.END}")
    print(f"  1. Mở: viewer.html")
    print(f"  2. F12 → Console")
    print(f"  3. Paste:")
    print()
    print(f"     {Colors.CYAN}const pc = window.scene.children.find(o => o.isPoints);")
    print(f"     console.log('Điểm:', pc?.geometry.attributes.position.count);{Colors.END}")
    print()

def main():
    print_header("🔍 PHÂN TÍCH FILE SCENE 3D")
    
    # Define scene file path
    scene_file = r"g:\accident-scene-reconstruction\3D\accident_scene.scene3d"
    
    # Check if file exists
    if not os.path.exists(scene_file):
        print_error(f"File không tìm thấy: {scene_file}")
        print("\nTìm kiếm các file .scene3d hoặc .ply trong folder...")
        
        folder = r"g:\accident-scene-reconstruction\3D"
        if os.path.exists(folder):
            files = []
            for ext in ['*.scene3d', '*.ply', '*.Scene3D', '*.PLY']:
                files.extend(Path(folder).glob(ext))
            
            if files:
                print(f"\nTìm thấy {len(files)} file:")
                for i, f in enumerate(files, 1):
                    print(f"  {i}. {f.name} ({format_size(os.path.getsize(f))})")
                
                if len(files) > 0:
                    scene_file = str(files[0])
                    print(f"\nPhân tích file: {files[0].name}")
            else:
                print_error("Không tìm thấy file .scene3d hoặc .ply")
                return
        else:
            print_error(f"Folder không tìm thấy: {folder}")
            return
    
    print()
    
    # Analyze file based on extension
    filename_lower = os.path.basename(scene_file).lower()
    
    if filename_lower.endswith('.scene3d'):
        analyze_scene3d(scene_file)
    elif filename_lower.endswith('.ply'):
        analyze_ply(scene_file)
    else:
        # Try to detect by content
        with open(scene_file, 'rb') as f:
            magic = f.read(4)
            if magic == b'ASR3':
                analyze_scene3d(scene_file)
            elif magic == b'ply\n' or magic[:3] == b'ply':
                analyze_ply(scene_file)
            else:
                print_error("Định dạng file không rõ")
                return
    
    file_size = os.path.getsize(scene_file)
    analyze_quality(file_size)
    provide_recommendations(scene_file)
    
    print_section("Liên Kết Hữu Ích")
    print(f"  📖 Hướng dẫn chi tiết: TOI_UU_DIEM_CLOUD_TIENG_VIET.md")
    print(f"  📋 3 Cách nhanh: 3_CACH_CANH_THIEN_CHATLUONG.txt")
    print(f"  🎨 So sánh: HUONG_DAN_TIENG_VIET.md")
    print()
    
    print(f"{Colors.BOLD}{Colors.GREEN}Kiểm tra hoàn tất!{Colors.END}")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Người dùng dừng chương trình{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}Lỗi: {e}{Colors.END}")
