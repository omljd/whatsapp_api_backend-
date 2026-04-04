import requests
import time
import csv
import base64

base_url = "http://127.0.0.1:8000/api/unofficial"
device_id = "331180a5-f44e-45ad-8e1a-2aef18e634ac"
device_name = "sas"
to = "918767647149"
message = "hey sagar how are you"
file_path = r"D:\whatsapp api project clone  data\whatsapp-api-backend\DEVICE_CONNECTION_FIX_SUMMARY.md"

# Read the local file and encode as base64
with open(file_path, "rb") as f:
    base64_data = base64.b64encode(f.read()).decode()

routes = [
    # POST endpoints
    {
        "name": "POST /send-message",
        "method": "POST",
        "url": f"{base_url}/send-message",
        "kwargs": {"json": {"device_id": device_id, "device_name": device_name, "receiver_number": to, "message": message}},
    },
    {
        "name": "POST /send-file",
        "method": "POST",
        "url": f"{base_url}/send-file",
        "kwargs": {"json": {"device_id": device_id, "device_name": device_name, "receiver_number": to, "file_path": file_path}},
    },
    {
        "name": "POST /send-file-text",
        "method": "POST",
        "url": f"{base_url}/send-file-text",
        "kwargs": {"json": {"device_id": device_id, "device_name": device_name, "receiver_number": to, "file_path": file_path, "message": message}},
    },
    {
        "name": "POST /send-base64-file",
        "method": "POST",
        "url": f"{base_url}/send-base64-file",
        "kwargs": {"json": {"device_id": device_id, "device_name": device_name, "receiver_number": to, "base64_data": base64_data, "filename": "DEVICE_CONNECTION_FIX_SUMMARY.md"}},
    },
    # GET endpoints
    {
        "name": "GET /send-file",
        "method": "GET",
        "url": f"{base_url}/send-file",
        "kwargs": {"params": {"device_id": device_id, "device_name": device_name, "receiver_number": to, "file_path": file_path}},
    },
    {
        "name": "GET /send-file-text",
        "method": "GET",
        "url": f"{base_url}/send-file-text",
        "kwargs": {"params": {"device_id": device_id, "device_name": device_name, "receiver_number": to, "file_path": file_path, "message": message}},
    },
    {
        "name": "GET /send-file-caption",
        "method": "GET",
        "url": f"{base_url}/send-file-caption",
        "kwargs": {"params": {"device_id": device_id, "device_name": device_name, "receiver_number": to, "file_path": file_path, "caption": message}},
    },
    {
        "name": "GET /send-message-query",
        "method": "GET",
        "url": f"{base_url}/send-message-query",
        "kwargs": {"params": {"device_id": device_id, "device_name": device_name, "receiver_number": to, "message": message}},
    },
    {
        "name": "GET /send-file-query",
        "method": "GET",
        "url": f"{base_url}/send-file-query",
        "kwargs": {"params": {"device_id": device_id, "device_name": device_name, "receiver_number": to, "file_path": file_path}},
    },
    {
        "name": "GET /send-message-file-query",
        "method": "GET",
        "url": f"{base_url}/send-message-file-query",
        "kwargs": {"params": {"device_id": device_id, "device_name": device_name, "receiver_number": to, "message": message, "file_path": file_path}},
    },
    {
        "name": "GET /delivery-report",
        "method": "GET",
        "url": f"{base_url}/delivery-report",
        "kwargs": {"params": {"device_id": device_id, "device_name": device_name, "message_id": "test-msg-001"}},
    },
    {
        "name": "GET /status-check",
        "method": "GET",
        "url": f"{base_url}/status-check",
        "kwargs": {"params": {"device_id": device_id, "device_name": device_name}},
    },
]

results = []
errors = []

print(f"\n{'='*90}")
print(f"  UNOFFICIAL PUBLIC API REAL-TIME TEST (UPDATED)")
print(f"  Device ID:  {device_id}")
print(f"  Device:     {device_name}")
print(f"  Recipient:  {to}")
print(f"  Message:    {message}")
print(f"  File:       {file_path}")
print(f"{'='*90}\n")
print(f"{'Endpoint':<35} | {'Method':<6} | {'Status':<6} | {'Time(ms)':<9} | {'Result':<6} |")
print("-" * 75)

for route in routes:
    start_time = time.time()
    try:
        if route["method"] == "POST":
            response = requests.post(route["url"], timeout=60, **route["kwargs"])
        else:
            response = requests.get(route["url"], timeout=60, **route["kwargs"])
        
        status = response.status_code
        elapsed_ms = int((time.time() - start_time) * 1000)
        body = response.text[:200].replace('\n', ' ')
        result_tag = "PASS" if status < 500 else "FAIL"
        if status >= 500:
            errors.append({"name": route["name"], "status": status, "error": body})
    except Exception as e:
        status = 0
        elapsed_ms = int((time.time() - start_time) * 1000)
        body = str(e)[:200]
        result_tag = "FAIL"
        errors.append({"name": route["name"], "status": "Exception", "error": str(e)})

    print(f"{route['name']:<35} | {route['method']:<6} | {status:<6} | {elapsed_ms:<9} | {result_tag:<6} |")
    results.append({
        "Endpoint": route["name"],
        "Method": route["method"],
        "Status": status,
        "Time(ms)": elapsed_ms,
        "Result": result_tag,
        "Response": body
    })

csv_file = "test_report_unofficial_realtime_final.csv"
with open(csv_file, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=["Endpoint", "Method", "Status", "Time(ms)", "Result", "Response"])
    writer.writeheader()
    writer.writerows(results)

md_file = "test_report_unofficial_realtime_final.md"
passed = sum(1 for r in results if r['Result'] == 'PASS')
total = len(results)
failed = total - passed
success_rate = (passed / total) * 100 if total > 0 else 0

with open(md_file, mode='w', encoding='utf-8') as f:
    f.write("# Unofficial Public API Real-Time Test Report (Updated)\n\n")
    f.write(f"**Device ID:** `{device_id}`\n")
    f.write(f"**Device Name:** `{device_name}`\n")
    f.write(f"**Recipient:** `{to}`\n")
    f.write(f"**Message:** `{message}`\n")
    f.write(f"**File:** `{file_path}`\n\n")
    f.write("## Summary\n")
    f.write(f"- **Total tested:** {total}\n")
    f.write(f"- **Passed:** {passed}\n")
    f.write(f"- **Failed:** {failed}\n")
    f.write(f"- **Success Rate:** {success_rate:.2f}%\n\n")
    f.write("## Test Results Table\n\n")
    f.write("| Endpoint | Method | Status | Time(ms) | Result | Response (short) |\n")
    f.write("|----------|--------|--------|----------|--------|------------------|\n")
    for r in results:
        short_resp = r['Response'][:120].replace('|', '\\|')
        f.write(f"| {r['Endpoint']} | {r['Method']} | {r['Status']} | {r['Time(ms)']} | {r['Result']} | {short_resp} |\n")
    if errors:
        f.write("\n## Errors and Probable Causes\n\n")
        for err in errors:
            f.write(f"### {err['name']}\n")
            f.write(f"- **Status Code:** {err['status']}\n")
            f.write(f"- **Error Response:** `{err['error'][:200]}`\n\n")

print(f"\n{'='*75}")
print(f"  SUMMARY: {passed}/{total} PASSED  |  {failed} FAILED  |  {success_rate:.1f}% Success Rate")
print(f"  Reports saved: {csv_file}, {md_file}")
print(f"{'='*75}\n")
