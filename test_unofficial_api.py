#!/usr/bin/env python3
"""
Comprehensive Test Runner for Unofficial Public API
Tests all endpoints with real messages to WhatsApp
"""

import requests
import time
import base64
import json
import os
from datetime import datetime

# ──── Configuration ────
BASE_URL = "http://localhost:8000/api/unofficial"
DEVICE_ID = "34451e53-8d99-4eb9-9388-13355994f08c"
DEVICE_NAME = "test-device"
RECEIVER = "919970820770"
FILE_PATH = r"D:\whatsapp api project clone  data\whatsapp-api-backend\README.md"
IMAGE_PATH = r"C:\Users\ASUS\Downloads\image (1).png"
MESSAGE = "Hello from Unofficial API Test! " + datetime.now().strftime("%H:%M:%S")

results = []

def log_result(test_name, method, endpoint, status_code, response_time, response_body, success):
    results.append({
        "test_name": test_name,
        "method": method,
        "endpoint": endpoint,
        "status_code": status_code,
        "response_time_ms": round(response_time * 1000),
        "success": success,
        "response_preview": str(response_body)[:200]
    })
    icon = "PASS" if success else "FAIL"
    print(f"  [{icon}] [{status_code}] {response_time*1000:.0f}ms - {test_name}")

def test_endpoint(test_name, method, url, **kwargs):
    try:
        start = time.time()
        resp = requests.request(method, url, timeout=60, **kwargs)
        elapsed = time.time() - start
        
        try:
            body = resp.json()
        except:
            body = resp.text[:200]
        
        is_success = resp.status_code in [200, 201, 202]
        log_result(test_name, method, url.replace(BASE_URL, ""), resp.status_code, elapsed, body, is_success)
        return resp
    except Exception as e:
        log_result(test_name, method, url.replace(BASE_URL, ""), 0, 0, str(e), False)
        return None

# ══════════════════════════════════════════
print("=" * 70)
print("  UNOFFICIAL API TEST SUITE")
print("  Device: " + DEVICE_ID)
print("  Receiver: " + RECEIVER)
print("  Time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("=" * 70)

# ──── 1. Status Check (GET) ────
print("\n1. Status Check")
test_endpoint(
    "GET /status-check",
    "GET",
    f"{BASE_URL}/status-check",
    params={"device_id": DEVICE_ID, "device_name": DEVICE_NAME}
)

time.sleep(1)

# ──── 2. Send Text Message (POST JSON) ────
print("\n2. Send Text Message (POST JSON)")
test_endpoint(
    "POST /send-message",
    "POST",
    f"{BASE_URL}/send-message",
    json={
        "device_id": DEVICE_ID,
        "device_name": DEVICE_NAME,
        "receiver_number": RECEIVER,
        "message": f"Test 2: POST JSON Text - {MESSAGE}"
    }
)

time.sleep(2)

# ──── 3. Send Text Message (GET Query) ────
print("\n3. Send Text Message (GET Query)")
test_endpoint(
    "GET /send-message-query",
    "GET",
    f"{BASE_URL}/send-message-query",
    params={
        "device_id": DEVICE_ID,
        "device_name": DEVICE_NAME,
        "receiver_number": RECEIVER,
        "message": f"Test 3: GET Query Text - {MESSAGE}"
    }
)

time.sleep(2)

# ──── 4. Send File (POST Form) ────
print("\n4. Send File (POST Form) - README.md")
test_endpoint(
    "POST /send-file",
    "POST",
    f"{BASE_URL}/send-file",
    data={
        "device_id": DEVICE_ID,
        "device_name": DEVICE_NAME,
        "receiver_number": RECEIVER,
        "file_path": FILE_PATH
    }
)

time.sleep(2)

# ──── 5. Send File (GET Query) ────
print("\n5. Send File (GET Query)")
test_endpoint(
    "GET /send-file",
    "GET",
    f"{BASE_URL}/send-file",
    params={
        "device_id": DEVICE_ID,
        "device_name": DEVICE_NAME,
        "receiver_number": RECEIVER,
        "file_path": FILE_PATH
    }
)

time.sleep(2)

# ──── 6. Send File with Text (POST Form) ────
print("\n6. Send File with Text (POST Form)")
test_endpoint(
    "POST /send-file-text",
    "POST",
    f"{BASE_URL}/send-file-text",
    data={
        "device_id": DEVICE_ID,
        "device_name": DEVICE_NAME,
        "receiver_number": RECEIVER,
        "file_path": FILE_PATH,
        "message": f"Test 6: File + Text caption - {MESSAGE}"
    }
)

time.sleep(2)

# ──── 7. Send File with Text (GET Query) ────
print("\n7. Send File with Text (GET Query)")
test_endpoint(
    "GET /send-file-text",
    "GET",
    f"{BASE_URL}/send-file-text",
    params={
        "device_id": DEVICE_ID,
        "device_name": DEVICE_NAME,
        "receiver_number": RECEIVER,
        "file_path": FILE_PATH,
        "message": f"Test 7: File + Text GET - {MESSAGE}"
    }
)

time.sleep(2)

# ──── 8. Send File with Caption (POST Form) ────
print("\n8. Send File with Caption (POST Form)")
test_endpoint(
    "POST /send-file-caption",
    "POST",
    f"{BASE_URL}/send-file-caption",
    data={
        "device_id": DEVICE_ID,
        "device_name": DEVICE_NAME,
        "receiver_number": RECEIVER,
        "file_path": FILE_PATH,
        "caption": f"Test 8: File Caption POST - {MESSAGE}"
    }
)

time.sleep(2)

# ──── 9. Send File with Caption (GET Query) ────
print("\n9. Send File with Caption (GET Query)")
test_endpoint(
    "GET /send-file-caption",
    "GET",
    f"{BASE_URL}/send-file-caption",
    params={
        "device_id": DEVICE_ID,
        "device_name": DEVICE_NAME,
        "receiver_number": RECEIVER,
        "file_path": FILE_PATH,
        "caption": f"Test 9: File Caption GET - {MESSAGE}"
    }
)

time.sleep(2)

# ──── 10. Send File via Query alias ────
print("\n10. Send File via /send-file-query alias")
test_endpoint(
    "GET /send-file-query",
    "GET",
    f"{BASE_URL}/send-file-query",
    params={
        "device_id": DEVICE_ID,
        "device_name": DEVICE_NAME,
        "receiver_number": RECEIVER,
        "file_path": FILE_PATH
    }
)

time.sleep(2)

# ──── 11. Send Base64 File (Image) ────
print("\n11. Send Base64 File (Image)")
if os.path.exists(IMAGE_PATH):
    with open(IMAGE_PATH, "rb") as f:
        b64_data = base64.b64encode(f.read()).decode("utf-8")
    test_endpoint(
        "POST /send-base64-file (image)",
        "POST",
        f"{BASE_URL}/send-base64-file",
        data={
            "device_id": DEVICE_ID,
            "device_name": DEVICE_NAME,
            "receiver_number": RECEIVER,
            "base64_data": b64_data,
            "filename": "test_image.png"
        }
    )
else:
    print(f"  WARNING: Image file not found: {IMAGE_PATH}")
    log_result("POST /send-base64-file (image)", "POST", "/send-base64-file", 0, 0, "File not found", False)

time.sleep(2)

# ──── 12. Bulk Send Messages ────
print("\n12. Bulk Send Messages")
test_endpoint(
    "POST /bulk-send-messages",
    "POST",
    f"{BASE_URL}/bulk-send-messages",
    data={
        "device_id": DEVICE_ID,
        "device_name": DEVICE_NAME,
        "message": f"Test 12: Bulk Text - {MESSAGE}",
        "recipients": RECEIVER,
        "wait_for_delivery": "false",
        "max_wait_time": "10"
    }
)

time.sleep(2)

# ──── 13. Bulk Send Files ────
print("\n13. Bulk Send Files")
test_endpoint(
    "POST /bulk-send-files",
    "POST",
    f"{BASE_URL}/bulk-send-files",
    data={
        "device_id": DEVICE_ID,
        "device_name": DEVICE_NAME,
        "file_path": FILE_PATH,
        "recipients": RECEIVER,
        "wait_for_delivery": "false",
        "max_wait_time": "10"
    }
)

time.sleep(2)

# ──── 14. Bulk Send Files with Text ────
print("\n14. Bulk Send Files with Text")
test_endpoint(
    "POST /bulk-send-files-with-text",
    "POST",
    f"{BASE_URL}/bulk-send-files-with-text",
    data={
        "device_id": DEVICE_ID,
        "device_name": DEVICE_NAME,
        "message": f"Test 14: Bulk File+Text - {MESSAGE}",
        "recipients": RECEIVER,
        "file_path": FILE_PATH,
        "wait_for_delivery": "false",
        "max_wait_time": "10"
    }
)

time.sleep(2)

# ──── 15. Delivery Report ────
print("\n15. Delivery Report (dummy message_id)")
test_endpoint(
    "GET /delivery-report",
    "GET",
    f"{BASE_URL}/delivery-report",
    params={
        "device_id": DEVICE_ID,
        "device_name": DEVICE_NAME,
        "message_id": "test-message-id-000"
    }
)

# ══════════════════════════════════════════
# REPORT
# ══════════════════════════════════════════
print("\n" + "=" * 90)
print("  TEST REPORT")
print("=" * 90)

success_count = sum(1 for r in results if r["success"])
fail_count = sum(1 for r in results if not r["success"])

print(f"\n  Total: {len(results)} | Passed: {success_count} | Failed: {fail_count}")
print()

# Table header
header = f"{'#':<3} {'Test Name':<40} {'Method':<6} {'Status':<7} {'Time':<8} {'Result':<6}"
print(header)
print("-" * 90)

for i, r in enumerate(results, 1):
    icon = "PASS" if r["success"] else "FAIL"
    print(f"{i:<3} {r['test_name']:<40} {r['method']:<6} {r['status_code']:<7} {r['response_time_ms']:<8} {icon}")

print("-" * 90)
print(f"\nPassed: {success_count}/{len(results)}  |  Failed: {fail_count}/{len(results)}")

# Save CSV
csv_path = r"D:\whatsapp api project clone  data\whatsapp-api-backend\test_report_unofficial_api.csv"
with open(csv_path, "w") as f:
    f.write("Test #,Test Name,Method,Endpoint,Status Code,Response Time (ms),Success,Response Preview\n")
    for i, r in enumerate(results, 1):
        preview = r["response_preview"].replace('"', "'").replace(",", ";")
        f.write(f'{i},"{r["test_name"]}",{r["method"]},"{r["endpoint"]}",{r["status_code"]},{r["response_time_ms"]},{r["success"]},"{preview}"\n')

print(f"\nCSV report saved to: {csv_path}")
print("=" * 90)
