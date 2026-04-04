import requests
import time
import csv
import base64

base_url = "http://127.0.0.1:8000/api/official"
device_id = "ec62e36a-ce8a-4257-b0e9-6707b8c4f662"
to = "917887640770"
message = "vikas kailas kambale"
file_path = r"D:\whatsapp api project clone  data\whatsapp-api-backend\SYSTEM_STATUS.md"

# Read file for base64
with open(file_path, "rb") as f:
    raw = f.read()
base64_data = base64.b64encode(raw).decode()
print(f"File: {file_path} ({len(raw)} bytes)")

routes = [
    # POST endpoints
    {"name": "POST /send-message", "method": "POST", "url": f"{base_url}/send-message",
     "kwargs": {"params": {"device_id": device_id, "to": to, "message": message}}},
    {"name": "POST /send-file", "method": "POST", "url": f"{base_url}/send-file",
     "kwargs": {"params": {"device_id": device_id, "to": to, "file_path": file_path}}},
    {"name": "POST /send-file-text", "method": "POST", "url": f"{base_url}/send-file-text",
     "kwargs": {"params": {"device_id": device_id, "to": to, "file_path": file_path, "message": message}}},
    {"name": "POST /send-base64-file", "method": "POST", "url": f"{base_url}/send-base64-file",
     "kwargs": {"params": {"device_id": device_id, "to": to, "base64_data": base64_data, "filename": "SYSTEM_STATUS.md"}}},
    {"name": "POST /send-template", "method": "POST", "url": f"{base_url}/send-template",
     "kwargs": {"params": {"device_id": device_id, "to": to, "template_name": "hello_world", "language_code": "en_US"}}},
    {"name": "POST /bulk-send", "method": "POST", "url": f"{base_url}/bulk-send",
     "kwargs": {"params": {"device_id": device_id, "message": message, "recipients": to}}},
    # GET endpoints
    {"name": "GET /send-message", "method": "GET", "url": f"{base_url}/send-message",
     "kwargs": {"params": {"device_id": device_id, "to": to, "message": message}}},
    {"name": "GET /send-file", "method": "GET", "url": f"{base_url}/send-file",
     "kwargs": {"params": {"device_id": device_id, "to": to, "file_path": file_path}}},
    {"name": "GET /send-file-text", "method": "GET", "url": f"{base_url}/send-file-text",
     "kwargs": {"params": {"device_id": device_id, "to": to, "file_path": file_path, "message": message}}},
    {"name": "GET /send-file-caption", "method": "GET", "url": f"{base_url}/send-file-caption",
     "kwargs": {"params": {"device_id": device_id, "to": to, "file_path": file_path, "caption": message}}},
    {"name": "GET /send-message-query", "method": "GET", "url": f"{base_url}/send-message-query",
     "kwargs": {"params": {"device_id": device_id, "to": to, "message": message}}},
    {"name": "GET /send-file-query", "method": "GET", "url": f"{base_url}/send-file-query",
     "kwargs": {"params": {"device_id": device_id, "to": to, "file_path": file_path}}},
    {"name": "GET /send-message-file-query", "method": "GET", "url": f"{base_url}/send-message-file-query",
     "kwargs": {"params": {"device_id": device_id, "to": to, "file_path": file_path, "message": message}}},
    {"name": "GET /delivery-report", "method": "GET", "url": f"{base_url}/delivery-report",
     "kwargs": {"params": {"device_id": device_id, "message_id": "test-001"}}},
    {"name": "GET /public/check-config", "method": "GET", "url": f"{base_url}/public/check-config",
     "kwargs": {"params": {"device_id": device_id}}},
    {"name": "GET /templates", "method": "GET", "url": f"{base_url}/templates",
     "kwargs": {"params": {"device_id": device_id}}},
]

results = []

print(f"\n{'='*95}")
print(f"  OFFICIAL PUBLIC API TEST — DEVICE: {device_id}")
print(f"  Recipient: {to}  |  Message: {message}")
print(f"  File: {file_path}")
print(f"{'='*95}\n")
print(f"{'#':<3} {'Endpoint':<35} {'Method':<7} {'Status':<7} {'Time(ms)':<10} {'Result':<7} {'Delivered':<10}")
print("-" * 90)

for i, route in enumerate(routes, 1):
    start = time.time()
    try:
        if route["method"] == "POST":
            r = requests.post(route["url"], timeout=60, **route["kwargs"])
        else:
            r = requests.get(route["url"], timeout=60, **route["kwargs"])
        status = r.status_code
        ms = int((time.time() - start) * 1000)
        body = r.text[:200].replace('\n', ' ')
        tag = "PASS" if status < 500 else "FAIL"
        try:
            j = r.json()
            delivered = "YES" if j.get("success") == True else "NO"
        except:
            delivered = "?"
    except Exception as e:
        status = 0
        ms = int((time.time() - start) * 1000)
        body = str(e)[:200]
        tag = "FAIL"
        delivered = "ERROR"

    print(f"{i:<3} {route['name']:<35} {route['method']:<7} {status:<7} {ms:<10} {tag:<7} {delivered:<10}")
    results.append({"#": i, "Endpoint": route["name"], "Method": route["method"],
                     "Status": status, "Time(ms)": ms, "Result": tag,
                     "Delivered": delivered, "Response": body})

# Save CSV
csv_file = "test_report_official_final.csv"
with open(csv_file, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=["#", "Endpoint", "Method", "Status", "Time(ms)", "Result", "Delivered", "Response"])
    w.writeheader()
    w.writerows(results)

# Save Markdown
md_file = "test_report_official_final.md"
passed = sum(1 for r in results if r['Result'] == 'PASS')
delivered = sum(1 for r in results if r['Delivered'] == 'YES')
total = len(results)

with open(md_file, 'w', encoding='utf-8') as f:
    f.write("# Official Public API — Final Test Report\n\n")
    f.write(f"**Device ID:** `{device_id}`\n")
    f.write(f"**Recipient:** `{to}`\n")
    f.write(f"**Message:** `{message}`\n")
    f.write(f"**File:** `{file_path}`\n\n")
    f.write(f"## Summary\n- **Total:** {total}\n- **HTTP Passed:** {passed}/{total}\n- **Real-Time Delivered:** {delivered}/{total}\n\n")
    f.write("## Results\n\n")
    f.write("| # | Endpoint | Method | Status | Time(ms) | Result | Delivered | Response |\n")
    f.write("|---|----------|--------|--------|----------|--------|-----------|----------|\n")
    for r in results:
        short = r['Response'][:80].replace('|', '\\|')
        f.write(f"| {r['#']} | {r['Endpoint']} | {r['Method']} | {r['Status']} | {r['Time(ms)']} | {r['Result']} | {r['Delivered']} | {short} |\n")

print(f"\n{'='*90}")
print(f"  TOTAL: {total} | PASSED: {passed} | DELIVERED: {delivered}")
print(f"  Reports: {csv_file}, {md_file}")
print(f"{'='*90}\n")
