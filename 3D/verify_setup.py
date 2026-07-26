#!/usr/bin/env python3
"""
3D Viewer - Setup Verification Script
Checks that all necessary files are in place and properly configured
"""

import os
import sys
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def check_file_exists(path, description):
    """Check if a file exists and report status"""
    exists = os.path.exists(path)
    if exists:
        size = os.path.getsize(path)
        print(f"  {Colors.GREEN}✓{Colors.RESET} {description}: {path} ({size:,} bytes)")
    else:
        print(f"  {Colors.RED}✗{Colors.RESET} {description}: {path} NOT FOUND")
    return exists

def check_file_content(path, search_string):
    """Check if file contains specific string"""
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            return search_string in content
    except:
        return False

def main():
    print(f"\n{Colors.BLUE}═══════════════════════════════════════════════════════════{Colors.RESET}")
    print(f"{Colors.BLUE}  🔬 3D Viewer - Setup Verification Script{Colors.RESET}")
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════════════{Colors.RESET}\n")
    
    base_dir = os.path.dirname(os.path.abspath(__file__)) if __file__ else os.getcwd()
    base_dir = "3D"  # Assume we're in project root
    
    print(f"Project root: {base_dir}\n")
    
    all_pass = True
    
    # Check main HTML files
    print(f"{Colors.BLUE}📋 Core Files{Colors.RESET}")
    all_pass &= check_file_exists(os.path.join(base_dir, "viewer.html"), "Main viewer")
    all_pass &= check_file_exists(os.path.join(base_dir, "diagnostics.html"), "Diagnostics")
    
    # Check library files
    print(f"\n{Colors.BLUE}📚 Library Files{Colors.RESET}")
    lib_dir = os.path.join(base_dir, "lib")
    if os.path.exists(lib_dir):
        print(f"  {Colors.GREEN}✓{Colors.RESET} lib/ folder exists")
        all_pass &= check_file_exists(os.path.join(lib_dir, "three.min.js"), "Three.js library")
        all_pass &= check_file_exists(os.path.join(lib_dir, "OrbitControls.js"), "OrbitControls")
    else:
        print(f"  {Colors.RED}✗{Colors.RESET} lib/ folder NOT FOUND")
        all_pass = False
    
    # Check scene file
    print(f"\n{Colors.BLUE}🎬 Scene Files{Colors.RESET}")
    scene_file = os.path.join(base_dir, "accident_scene.scene3d")
    if os.path.exists(scene_file):
        size = os.path.getsize(scene_file)
        print(f"  {Colors.GREEN}✓{Colors.RESET} Scene file: accident_scene.scene3d ({size:,} bytes)")
        # Check magic bytes
        try:
            with open(scene_file, 'rb') as f:
                magic = f.read(4)
                if magic == b'ASR3':
                    print(f"    {Colors.GREEN}✓{Colors.RESET} Valid .scene3d format (magic: ASR3)")
                else:
                    print(f"    {Colors.YELLOW}⚠{Colors.RESET} Unknown file format (magic: {magic[:4]})")
        except:
            print(f"    {Colors.RED}✗{Colors.RESET} Could not read file header")
            all_pass = False
    else:
        print(f"  {Colors.YELLOW}⚠{Colors.RESET} Scene file not found (optional - can drag/drop)")
    
    # Check documentation
    print(f"\n{Colors.BLUE}📖 Documentation Files{Colors.RESET}")
    docs = [
        ("README.md", "Main readme"),
        ("QUICK_REFERENCE.txt", "Quick reference"),
        ("FIXES_SUMMARY.txt", "Fixes summary"),
        ("VIEWER_FIXES_AND_DIAGNOSTICS.md", "Technical details"),
        ("SETUP_TROUBLESHOOTING.md", "Troubleshooting guide"),
        ("STATUS_REPORT.md", "Status report"),
    ]
    for doc_file, desc in docs:
        all_pass &= check_file_exists(os.path.join(base_dir, doc_file), desc)
    
    # Check viewer.html content
    print(f"\n{Colors.BLUE}✨ Viewer Features{Colors.RESET}")
    viewer_path = os.path.join(base_dir, "viewer.html")
    if os.path.exists(viewer_path):
        has_cdn_fallback = check_file_content(viewer_path, "loadThreeFromCDN")
        has_error_handling = check_file_content(viewer_path, "onerror")
        has_auto_load = check_file_content(viewer_path, "tryAutoLoad")
        
        if has_cdn_fallback:
            print(f"  {Colors.GREEN}✓{Colors.RESET} CDN fallback implemented")
        else:
            print(f"  {Colors.YELLOW}⚠{Colors.RESET} CDN fallback not found")
            all_pass = False
        
        if has_error_handling:
            print(f"  {Colors.GREEN}✓{Colors.RESET} Error handling implemented")
        else:
            print(f"  {Colors.YELLOW}⚠{Colors.RESET} Error handling not found")
            all_pass = False
        
        if has_auto_load:
            print(f"  {Colors.GREEN}✓{Colors.RESET} Auto-load feature implemented")
        else:
            print(f"  {Colors.YELLOW}⚠{Colors.RESET} Auto-load feature not found")
            all_pass = False
    
    # Summary
    print(f"\n{Colors.BLUE}═══════════════════════════════════════════════════════════{Colors.RESET}")
    if all_pass:
        print(f"{Colors.GREEN}✓ All checks passed! Viewer is ready.{Colors.RESET}\n")
        print("Next steps:")
        print("  1. Open: diagnostics.html in a web browser")
        print("  2. Run: Automated diagnostics")
        print("  3. Open: viewer.html to use viewer\n")
        return 0
    else:
        print(f"{Colors.RED}✗ Some checks failed. See details above.{Colors.RESET}\n")
        print("Issues to fix:")
        print("  • Ensure all files are in 3D/ folder")
        print("  • Check lib/ folder for Three.js and OrbitControls")
        print("  • Read: SETUP_TROUBLESHOOTING.md for help\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
