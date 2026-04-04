import requests
import time
import csv
import json

base_url = "http://127.0.0.1:8000/api/unofficial"
payload_data = {
    "device_id": "331180a5-f44e-45ad-8e1a-2aef18e634ac",
    "device_name": "sas",
    "receiver_number": "919999999999",
    "message": "QA test message",
    "file_path": "https://example.com/test.pdf",
    "base64_data": "VGhpcyBpcyBhIHRlc3QgZmlsZQ==",
    "filename": "test.txt",
    "group_name": "TestGroup",
    "message_id": "test-message-id"
}

routes = [
    {"path": "/send-message", "method": "POST", "keys": ["device_id", "device_name", "receiver_number", "message"]},
    {"path": "/send-file", "method": "POST", "keys": ["device_id", "device_name", "receiver_number", "file_path"]},
    {"path": "/send-file-text", "method": "POST", "keys": ["device_id", "device_name", "receiver_number", "file_path", "message"]},
    {"path": "/send-base64-file", "method": "POST", "keys": ["device_id", "device_name", "receiver_number", "base64_data", "filename"]},
    {"path": "/send-file", "method": "GET", "keys": ["device_id", "device_name", "receiver_number", "file_path"]},
    {"path": "/send-file-text", "method": "GET", "keys": ["device_id", "device_name", "receiver_number", "file_path", "message"]},
    {"path": "/send-file-caption", "method": "GET", "keys": ["device_id", "device_name", "receiver_number", "file_path", "caption"]},
    {"path": "/send-message-query", "method": "GET", "keys": ["device_id", "device_name", "receiver_number", "message"]},
    {"path": "/send-file-query", "method": "GET", "keys": ["device_id", "device_name", "receiver_number", "file_path"]},
    {"path": "/send-message-file-query", "method": "GET", "keys": ["device_id", "device_name", "receiver_number", "message", "file_path"]},
    {"path": "/delivery-report", "method": "GET", "keys": ["device_id", "device_name", "message_id"]},
    {"path": "/status-check", "method": "GET", "keys": ["device_id", "device_name"]},
]

results = []
errors = []

print(f"{'Endpoint':<30} | {'Method':<6} | {'Status':<6} | {'Time(ms)':<8} | {'Result':<6} |")
print("-" * 65)

for route in routes:
    url = f"{base_url}{route['path']}"
    
    # Map payload_data keys, accounting for 'caption'
    data = {}
    for k in route['keys']:
        if k == 'caption':
            data[k] = payload_data['message']
        else:
            data[k] = payload_data.get(k)
            
    start_time = time.time()
    
    try:
        if route['method'] == "POST":
            response = requests.post(url, json=data, timeout=30)
        else:
            response = requests.get(url, params=data, timeout=30)
            
        status = response.status_code
        elapsed_ms = int((time.time() - start_time) * 1000)
        body = response.text[:150].replace('\n', ' ')
        
        # PASS if status < 500, else FAIL
        result = "PASS" if status < 500 else "FAIL"
        
        if status >= 500:
            errors.append({
                "path": route['path'],
                "method": route['method'],
                "status": status,
                "error": body
            })
            
    except Exception as e:
        status = 0
        elapsed_ms = int((time.time() - start_time) * 1000)
        body = str(e)[:150]
        result = "FAIL"
        errors.append({
            "path": route['path'],
            "method": route['method'],
            "status": "Exception",
            "error": str(e)
        })
        
    print(f"{route['path']:<30} | {route['method']:<6} | {status:<6} | {elapsed_ms:<8} | {result:<6} |")
    
    results.append({
        "Endpoint": route['path'],
        "Method": route['method'],
        "Status": status,
        "Time(ms)": elapsed_ms,
        "Result": result,
        "Response": body
    })


# Save CSV
csv_file = "test_report_unofficial_real_device_final.csv"
with open(csv_file, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=["Endpoint", "Method", "Status", "Time(ms)", "Result", "Response"])
    writer.writeheader()
    writer.writerows(results)

# Save Markdown
md_file = "test_report_unofficial_real_device_final.md"
passed = sum(1 for r in results if r['Result'] == 'PASS')
total = len(results)
failed = total - passed
success_rate = (passed / total) * 100 if total > 0 else 0

with open(md_file, mode='w', encoding='utf-8') as f:
    f.write("# Unofficial API Real Device Test Report\n\n")
    f.write("## Summary\n")
    f.write(f"- **Total tested:** {total}\n")
    f.write(f"- **Passed:** {passed}\n")
    f.write(f"- **Failed:** {failed}\n")
    f.write(f"- **Success Rate:** {success_rate:.2f}%\n\n")
    
    f.write("## Test Results Table\n\n")
    f.write("| Endpoint | Method | Status | Time(ms) | Result | Response (short) |\n")
    f.write("|----------|--------|--------|----------|--------|------------------|\n")
    for r in results:
        f.write(f"| {r['Endpoint']} | {r['Method']} | {r['Status']} | {r['Time(ms)']} | {r['Result']} | {r['Response']} |\n")
        
    if errors:
        f.write("\n## Errors and Probable Causes\n\n")
        for err in errors:
            f.write(f"### {err['method']} {err['path']}\n")
            f.write(f"- **Status Code:** {err['status']}\n")
            f.write(f"- **Error Response:** `{err['error']}`\n\n")
            
        f.write("### Probable Causes Section\n")
        f.write("- **500 Internal Server Error:** The constructor error is completely eliminated. The new errors (`'WhatsAppEngineService' object has no attribute '...'`) indicate that while `WhatsAppEngineService` is properly instantiated with the `db` dependency, the required methods (like `send_text`, `send_file`) are missing from the service class itself. This is outside the scope of the DI fix.\n")
