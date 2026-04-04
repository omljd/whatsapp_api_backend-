import requests
import time
import base64

to = "918767647149"
file_path = r"C:\Users\ASUS\Downloads\स्वराज्य_चर्चा_रायगड_दरबार.mp4"

# --- Unofficial API ---
unofficial_url = "http://127.0.0.1:8000/api/unofficial"
unofficial_device_id = "331180a5-f44e-45ad-8e1a-2aef18e634ac"
unofficial_device_name = "sas"

# --- Official API ---
official_url = "http://127.0.0.1:8000/api/official"
official_device_id = "126a7560-fc4f-47da-88f5-ce87eee976f6"

results = []

def test(name, method, url, **kwargs):
    start = time.time()
    try:
        if method == "POST":
            r = requests.post(url, timeout=120, **kwargs)
        else:
            r = requests.get(url, timeout=120, **kwargs)
        ms = int((time.time() - start) * 1000)
        tag = "PASS" if r.status_code < 500 else "FAIL"
        body = r.text[:150].replace('\n', ' ')
    except Exception as e:
        ms = int((time.time() - start) * 1000)
        tag = "FAIL"
        body = str(e)[:150]
        r = type('R', (), {'status_code': 0})()
    print(f"{name:<45} | {r.status_code:<6} | {ms:<8} | {tag}")
    results.append({"name": name, "status": r.status_code, "time_ms": ms, "result": tag, "response": body})

print(f"\n{'='*80}")
print(f"  SEND VIDEO FILE TEST")
print(f"  File: {file_path}")
print(f"  To:   {to}")
print(f"{'='*80}\n")
print(f"{'Test':<45} | {'Status':<6} | {'Time(ms)':<8} | Result")
print("-" * 75)

# 1. Unofficial: POST /send-file (local file path)
test("UNOFFICIAL POST /send-file", "POST",
     f"{unofficial_url}/send-file",
     json={"device_id": unofficial_device_id, "device_name": unofficial_device_name,
           "receiver_number": to, "file_path": file_path})

# 2. Unofficial: POST /send-file-text (local file + caption)
test("UNOFFICIAL POST /send-file-text", "POST",
     f"{unofficial_url}/send-file-text",
     json={"device_id": unofficial_device_id, "device_name": unofficial_device_name,
           "receiver_number": to, "file_path": file_path, "message": "Check this video!"})

# 3. Official: POST /send-file (local file path passed as query)
test("OFFICIAL POST /send-file", "POST",
     f"{official_url}/send-file",
     params={"device_id": official_device_id, "to": to, "file_path": file_path})

# 4. Official: POST /send-file-text (file + caption)
test("OFFICIAL POST /send-file-text", "POST",
     f"{official_url}/send-file-text",
     params={"device_id": official_device_id, "to": to, "file_path": file_path,
             "message": "Check this video!"})

passed = sum(1 for r in results if r['result'] == 'PASS')
total = len(results)

# Save report
with open("test_send_video_report.md", "w", encoding="utf-8") as f:
    f.write("# Video File Send Test Report\n\n")
    f.write(f"**File:** `{file_path}`\n")
    f.write(f"**Recipient:** `{to}`\n\n")
    f.write(f"## Summary\n- Total: {total}\n- Passed: {passed}\n- Failed: {total - passed}\n\n")
    f.write("## Results\n\n| Test | Status | Time(ms) | Result | Response |\n")
    f.write("|------|--------|----------|--------|----------|\n")
    for r in results:
        short = r['response'][:100].replace('|', '\\|')
        f.write(f"| {r['name']} | {r['status']} | {r['time_ms']} | {r['result']} | {short} |\n")

print(f"\n{'='*75}")
print(f"  SUMMARY: {passed}/{total} PASSED")
print(f"  Report: test_send_video_report.md")
print(f"{'='*75}\n")
