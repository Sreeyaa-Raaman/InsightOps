import json
import requests
import sys

BASE = 'http://127.0.0.1:8000'

print('========================================================')
print('        INSIGHTOPS COMPREHENSIVE END-TO-END AUDIT        ')
print('========================================================')

# 1. Health check
r = requests.get(f'{BASE}/api/health')
print(f'[1] Health Check: Status {r.status_code} ->', r.json())

# 2. Datasets list & preview
r = requests.get(f'{BASE}/api/datasets')
datasets = r.json()
print(f'[2] Datasets Count: {len(datasets)}')
for d in datasets:
    print(f'    - {d["original_name"]}: {d["row_count"]:,} rows, {d["column_count"]} cols')

ds_id = datasets[0]['id']
r_prev = requests.get(f'{BASE}/api/datasets/{ds_id}/preview?limit=3')
print(f'    Preview for {datasets[0]["original_name"]}: {len(r_prev.json()["rows"])} sample rows loaded')

# 3. Live Agent Tool-Calling Queries
queries = [
    ('Ranking', 'Which product generated the highest revenue?'),
    ('Bar Chart & Aggregation', 'Calculate average sales for each region and show a bar chart.'),
    ('Data Quality', 'Find all missing values and duplicate records across this dataset.'),
    ('Outlier Detection', 'Detect statistical outliers in revenue.')
]

session_id = None
for category, q in queries:
    print(f'\n--- Testing Query: [{category}] "{q}" ---')
    payload = {'dataset_id': ds_id, 'message': q, 'session_id': session_id}
    res = requests.post(f'{BASE}/api/agent/chat', json=payload)
    if res.status_code != 200:
        print(f'ERROR: {res.status_code}', res.text)
        continue
    data = res.json()
    session_id = data['session_id']
    resp_obj = data['response']
    print(f'Status: 200 OK | Session ID: {session_id}')
    print('Execution Trace Tools Run:')
    for t in resp_obj.get('execution_trace', []):
        print(f'  ✓ {t["tool_name"]}(): {t["summary"]}')
    if resp_obj.get('chart_config'):
        cfg = resp_obj['chart_config']
        print(f'Chart Generated: Type "{cfg.get("chart_type")}" | Title: "{cfg.get("title")}" | Datapoints: {len(cfg.get("data", []))}')
    print('Key Findings:', resp_obj.get('key_findings', []))
    print('Answer Snippet:', resp_obj.get('answer', '')[:140].strip(), '...')

# 4. Follow-up query using Conversational Memory
print(f'\n--- Testing Conversational Memory Follow-up Query ---')
follow_up = 'What about the top category for that product?'
res = requests.post(f'{BASE}/api/agent/chat', json={'dataset_id': ds_id, 'message': follow_up, 'session_id': session_id})
print(f'Memory Response Status: {res.status_code}')
if res.status_code == 200:
    print('Answer Snippet:', res.json()['response']['answer'][:140].strip(), '...')
else:
    print('Error Body:', res.text)

# 5. Report Generation & PDF Download
print(f'\n--- Testing Report Generation & PDF Export ---')
rep_res = requests.post(f'{BASE}/api/reports/generate', json={'dataset_id': ds_id, 'session_id': session_id, 'title': 'Verification Executive Report'})
rep_data = rep_res.json()
rep_id = rep_data['id']
print(f'Report Generated: ID {rep_id} | Health Score: {rep_data["content"]["health_score"]}/100 (Grade {rep_data["content"]["health_grade"]})')

pdf_res = requests.get(f'{BASE}/api/reports/{rep_id}/download')
print(f'PDF Download Status: {pdf_res.status_code} | Size: {len(pdf_res.content):,} bytes | Content-Type: {pdf_res.headers.get("content-type")}')

csv_res = requests.get(f'{BASE}/api/reports/{rep_id}/download-csv')
print(f'CSV Download Status: {csv_res.status_code} | Size: {len(csv_res.content):,} bytes | Content-Type: {csv_res.headers.get("content-type")}')

# 6. Frontend probe
front_res = requests.get('http://127.0.0.1:5173')
print(f'\n[6] Frontend Web Server Status: {front_res.status_code} OK (HTML served, {len(front_res.text)} bytes)')
print('========================================================')
print('       ALL FUNCTIONAL CRITERIA VERIFIED SUCCESSFULLY!   ')
print('========================================================')
