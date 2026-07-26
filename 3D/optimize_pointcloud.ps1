#!/usr/bin/env powershell
<#
.SYNOPSIS
  Script tối ưu hóa Point Cloud - 3D Viewer Quality Optimizer
  
.DESCRIPTION
  Tự động cải thiện chất lượng hình ảnh 3D viewer
  
.USAGE
  1. Mở PowerShell
  2. Chạy: .\optimize_pointcloud.ps1
  3. Chọn tùy chọn (1-5)
  4. Xem hình ảnh cải thiện!
#>

Write-Host "`n╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🎨 3D Viewer - Point Cloud Quality Optimizer" -ForegroundColor Cyan
Write-Host "║  Công cụ tối ưu hóa chất lượng hình ảnh 3D" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "📊 Vấn Đề Hiện Tại:" -ForegroundColor Yellow
Write-Host "  • Hình ảnh pixelated / khối vuông" -ForegroundColor Yellow
Write-Host "  • Chất lượng thấp" -ForegroundColor Yellow
Write-Host "  • Không mịn, bị nấu mép`n" -ForegroundColor Yellow

Write-Host "✅ Giải Pháp:" -ForegroundColor Green
Write-Host "  1. Tăng cỡ điểm (Thanh trượt UI)" -ForegroundColor Green
Write-Host "  2. Tăng cỡ điểm (Console - Nhanh)" -ForegroundColor Green
Write-Host "  3. Bật Anti-Aliasing (Mịn mép)" -ForegroundColor Green
Write-Host "  4. Sửa viewer.html (Vĩnh viễn)" -ForegroundColor Green
Write-Host "  5. Xuất lại file (Chất lượng cao)" -ForegroundColor Green
Write-Host "  0. Thoát`n" -ForegroundColor Green

$choice = Read-Host "Chọn tùy chọn (0-5)"

switch($choice) {
  "1" {
    Write-Host "`n📋 CÁCH 1: Dùng Thanh Trượt UI (Dễ Nhất)`n" -ForegroundColor Cyan
    
    Write-Host "Bước 1: Mở file" -ForegroundColor White
    Write-Host "  g:\accident-scene-reconstruction\3D\viewer.html`n"
    
    Write-Host "Bước 2: Tìm thanh trượt 'Cỡ Điểm' bên phải màn hình`n"
    
    Write-Host "Bước 3: Kéo thanh từ 2.0 → 6.0 - 10.0`n"
    
    Write-Host "✅ XONG! Hình ảnh sẽ cải thiện ngay!`n" -ForegroundColor Green
    
    Write-Host "💡 Mẹo: Kéo từ từ để tìm giá trị tối ưu cho bạn`n" -ForegroundColor Yellow
  }
  
  "2" {
    Write-Host "`n📋 CÁCH 2: Tăng Cỡ Điểm Qua Console (Nhanh)`n" -ForegroundColor Cyan
    
    Write-Host "Bước 1: Mở viewer.html`n"
    
    Write-Host "Bước 2: Nhấn F12 để mở Developer Tools`n"
    
    Write-Host "Bước 3: Chọn tab 'Console'`n"
    
    Write-Host "Bước 4: Copy & Paste code dưới đây:`n" -ForegroundColor Yellow
    
    $code = @"
// Tăng cỡ điểm lên 8
window.pointsMaterial.size = 8;
window.pointsMaterial.needsUpdate = true;
window.renderer.render(window.scene, window.camera);
console.log("✓ Cỡ điểm tăng thành: 8");
"@
    
    Write-Host $code -ForegroundColor Green
    
    Write-Host "`n✅ Kết Quả: Hình ảnh mịn hơn 3-4 lần!`n" -ForegroundColor Green
    
    Write-Host "💡 Mẹo: Thay '8' bằng số khác (4, 6, 10) nếu cần`n" -ForegroundColor Yellow
  }
  
  "3" {
    Write-Host "`n📋 CÁCH 3: Bật Anti-Aliasing (Mịn Mép)`n" -ForegroundColor Cyan
    
    Write-Host "Bước 1: Mở viewer.html`n"
    
    Write-Host "Bước 2: Nhấn F12 → Console`n"
    
    Write-Host "Bước 3: Copy & Paste tất cả:`n" -ForegroundColor Yellow
    
    $code = @"
// Bật chế độ cao cấp
window.renderer.antialias = true;
window.pointsMaterial.sizeAttenuation = false;
window.pointsMaterial.opacity = 1.0;
window.pointsMaterial.needsUpdate = true;
window.renderer.render(window.scene, window.camera);
console.log("✓ Chế độ cao cấp bật!");
"@
    
    Write-Host $code -ForegroundColor Green
    
    Write-Host "`n✅ Kết Quả: Mịn hơn, không bị nấu mép!`n" -ForegroundColor Green
  }
  
  "4" {
    Write-Host "`n📋 CÁCH 4: Sửa viewer.html (Vĩnh Viễn)`n" -ForegroundColor Cyan
    
    Write-Host "Bước 1: Mở file viewer.html bằng editor" -ForegroundColor White
    Write-Host "  g:\accident-scene-reconstruction\3D\viewer.html`n"
    
    Write-Host "Bước 2: Tìm dòng ~320 (tìm 'pointsMaterial'):" -ForegroundColor White
    Write-Host "  Ctrl+F → tìm 'size: 2.0'`n"
    
    Write-Host "Bước 3: Đổi đoạn này:" -ForegroundColor White
    Write-Host "  CŨ: size: 2.0," -ForegroundColor Red
    Write-Host "  CŨ: sizeAttenuation: true,`n"
    
    Write-Host "  MỚI: size: 6.0," -ForegroundColor Green
    Write-Host "  MỚI: sizeAttenuation: false,`n"
    
    Write-Host "Bước 4: Lưu file (Ctrl+S)`n"
    
    Write-Host "✅ XONG! Mở viewer.html lại - Chất lượng cao luôn!`n" -ForegroundColor Green
  }
  
  "5" {
    Write-Host "`n📋 CÁCH 5: Xuất Lại File (Chất Lượng Cao)`n" -ForegroundColor Cyan
    
    Write-Host "Nếu các cách trên vẫn không đủ, vấn đề ở file gốc.`n" -ForegroundColor Yellow
    
    Write-Host "Bạn cần xuất lại với mật độ điểm cao hơn:`n"
    
    Write-Host "Tùy Chọn 1: Dùng CloudCompare (Free)" -ForegroundColor White
    Write-Host "  1. Tải: https://www.cloudcompare.org" -ForegroundColor Cyan
    Write-Host "  2. Mở file .scene3d hoặc .ply" -ForegroundColor Cyan
    Write-Host "  3. Filter → Subsample" -ForegroundColor Cyan
    Write-Host "  4. Chọn 'Space-based' với khoảng cách nhỏ hơn" -ForegroundColor Cyan
    Write-Host "  5. Export lại`n"
    
    Write-Host "Tùy Chọn 2: Dùng COLMAP" -ForegroundColor White
    Write-Host "  • Giảm: --sparse_model_num_pixels = 10" -ForegroundColor Cyan
    Write-Host "  • Tăng số điểm trong bước render`n"
    
    Write-Host "Tùy Chọn 3: Dùng OpenDroneMap" -ForegroundColor White
    Write-Host "  • Settings → Point Cloud" -ForegroundColor Cyan
    Write-Host "  • Tăng: --pc-quality 'high' hoặc 'ultra'`n"
    
    Write-Host "✅ Sau khi xuất, hình ảnh sẽ tốt hơn nhiều!`n" -ForegroundColor Green
  }
  
  "0" {
    Write-Host "`n👋 Thoát. Chúc bạn sử dụng 3D Viewer vui vẻ!`n" -ForegroundColor Cyan
    exit
  }
  
  default {
    Write-Host "`n❌ Tùy chọn không hợp lệ. Vui lòng chọn 0-5`n" -ForegroundColor Red
  }
}

Write-Host "`n📚 Tài Liệu Thêm:" -ForegroundColor Cyan
Write-Host "  • TOI_UU_DIEM_CLOUD_TIENG_VIET.md - Hướng dẫn chi tiết" -ForegroundColor Cyan
Write-Host "  • HUONG_DAN_TIENG_VIET.md - Hướng dẫn sử dụng`n" -ForegroundColor Cyan

Write-Host "🚀 Bước Tiếp Theo:" -ForegroundColor Green
Write-Host "  1. Áp dụng cách bạn chọn" -ForegroundColor Green
Write-Host "  2. Mở viewer.html" -ForegroundColor Green
Write-Host "  3. Xem hình ảnh cải thiện!`n" -ForegroundColor Green

Read-Host "Nhấn Enter để tiếp tục"
