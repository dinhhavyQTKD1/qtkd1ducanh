"""
Comprehensive Deployment Auditor for Nam Việt Software AI Agent
Verifies Python syntax, JSON integrity, test suite, and output completeness.
"""
import os
import sys
import glob
import json
import py_compile

def audit():
    print("=" * 80)
    print("      KIỂM TRA & RÀ SOÁT TỔNG THỂ DỰ ÁN TRƯỚC KHI DEPLOY")
    print("=" * 80)
    
    errors = []
    
    # 1. Python Syntax Check
    print("[1] Rà soát cú pháp toàn bộ file Python (.py):")
    py_files = sorted(glob.glob("**/*.py", recursive=True))
    for p in py_files:
        try:
            py_compile.compile(p, doraise=True)
            print(f"  ✔ [OK] {p}")
        except Exception as e:
            errors.append(f"Lỗi cú pháp Python tại {p}: {e}")
            print(f"  ❌ [FAIL] {p}: {e}")

    # 2. JSON Integrity Check
    print("\n[2] Rà soát tính toàn vẹn toàn bộ file dữ liệu JSON (.json):")
    json_files = sorted(glob.glob("**/*.json", recursive=True))
    for j in json_files:
        try:
            with open(j, "r", encoding="utf-8") as f:
                data = json.load(f)
                count = len(data) if isinstance(data, (list, dict)) else 1
                print(f"  ✔ [OK] {j:<40} ({count} phần tử)")
        except Exception as e:
            errors.append(f"Lỗi file JSON tại {j}: {e}")
            print(f"  ❌ [FAIL] {j}: {e}")

    # 3. HTML / Web Assets Check
    print("\n[3] Rà soát các tệp giao diện Web & Dashboard:")
    html_files = sorted(glob.glob("**/*.html", recursive=True))
    for h in html_files:
        size = os.path.getsize(h)
        print(f"  ✔ [OK] {h:<40} ({size:,} bytes)")

    # 4. Batch Files Check
    print("\n[4] Rà soát các tệp thực thi Batch (.bat):")
    bat_files = sorted(glob.glob("*.bat"))
    for b in bat_files:
        size = os.path.getsize(b)
        print(f"  ✔ [OK] {b:<40} ({size} bytes)")

    # 5. Core Documentation Check
    print("\n[5] Rà soát tài liệu báo cáo & hướng dẫn:")
    doc_files = ["REPORT_TASK1_TASK2.md", "README.md"]
    for d in doc_files:
        if os.path.exists(d):
            size = os.path.getsize(d)
            print(f"  ✔ [OK] {d:<40} ({size:,} bytes)")
        else:
            errors.append(f"Thiếu file tài liệu: {d}")
            print(f"  ❌ [MISSING] {d}")

    # 6. Run Automated Tests
    print("\n[6] Chạy kiểm thử tự động 5 kịch bản (test_suite.py):")
    from tests.test_suite import run_tests
    test_result = run_tests()
    if test_result != 0:
        errors.append("Một số ca kiểm thử trong test_suite.py bị thất bại.")

    # Summary
    print("\n" + "=" * 80)
    if len(errors) == 0:
        print("          KẾT QUẢ RÀ SOÁT: 100% HOÀN HẢO - SẴN SÀNG DEPLOY!")
    else:
        print(f"          KẾT QUẢ RÀ SOÁT: CÓ {len(errors)} LỖI CẦN XỬ LÝ:")
        for err in errors:
            print(f"          - {err}")
    print("=" * 80)

    return 0 if len(errors) == 0 else 1

if __name__ == "__main__":
    sys.exit(audit())

