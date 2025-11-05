#!/usr/bin/env python3
import os
import time
import requests
import base64
import zipfile
from io import BytesIO

OWNER = 'IzzatHomsi'
REPO = 'Tenantra-Platform'
WORKFLOW_FILE = 'backend-ci.yml'

TOKEN = os.environ.get('GITHUB_TOKEN')
if not TOKEN:
    raise SystemExit('GITHUB_TOKEN required in env')

HEADERS = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github+json'}

def list_runs():
    url = f'https://api.github.com/repos/{OWNER}/{REPO}/actions/workflows/{WORKFLOW_FILE}/runs?per_page=10'
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    return r.json().get('workflow_runs', [])

def rerun(run_id):
    url = f'https://api.github.com/repos/{OWNER}/{REPO}/actions/runs/{run_id}/rerun'
    r = requests.post(url, headers=HEADERS)
    if r.status_code not in (201, 202):
        print('Rerun request status:', r.status_code, r.text)
        r.raise_for_status()
    print('Rerun requested')

def download_logs(run_id, dest_dir):
    url = f'https://api.github.com/repos/{OWNER}/{REPO}/actions/runs/{run_id}/logs'
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    z = zipfile.ZipFile(BytesIO(r.content))
    z.extractall(dest_dir)
    print('Logs extracted to', dest_dir)

def find_verify_file(dest_dir):
    for root, _, files in os.walk(dest_dir):
        for f in files:
            if 'Verify migrations applied' in f or 'check_migrations' in f:
                return os.path.join(root, f)
    # fallback: search file contents
    for root, _, files in os.walk(dest_dir):
        for f in files:
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
                    txt = fh.read()
                    if "to_regclass('public.roles')" in txt or 'roles table is missing' in txt:
                        return path
            except Exception:
                continue
    return None

def main():
    runs = list_runs()
    if not runs:
        raise SystemExit('No workflow runs found')
    latest = sorted(runs, key=lambda r: r['created_at'], reverse=True)[0]
    latest_id = latest['id']
    latest_time = latest['created_at']
    print('Latest run id', latest_id, 'created_at', latest_time, 'status', latest['status'])
    rerun(latest_id)

    # wait for a new run to appear
    start = time.time()
    new_run = None
    while time.time() - start < 600:
        time.sleep(5)
        runs = list_runs()
        for r in sorted(runs, key=lambda r: r['created_at'], reverse=True):
            if r['created_at'] > latest_time:
                new_run = r
                break
        if new_run:
            break
    if not new_run:
        raise SystemExit('Timed out waiting for new run')
    print('New run id', new_run['id'], 'created_at', new_run['created_at'])

    # wait for completion
    run_id = new_run['id']
    while True:
        time.sleep(5)
        r = requests.get(f'https://api.github.com/repos/{OWNER}/{REPO}/actions/runs/{run_id}', headers=HEADERS)
        r.raise_for_status()
        run = r.json().get('workflow_run')
        print('Run status', run['status'], 'conclusion', run.get('conclusion'))
        if run['status'] == 'completed':
            break

    download_logs(run_id, f'run-{run_id}-logs')
    vf = find_verify_file(f'run-{run_id}-logs')
    if vf:
        print('\n=== Verify step file content ===\n')
        print(open(vf, 'r', encoding='utf-8', errors='ignore').read())
    else:
        print('Could not find verify step file; listing candidate files:')
        for root, _, files in os.walk(f'run-{run_id}-logs'):
            for f in files:
                if any(k in f for k in ['Run database migrations', 'Seed database']):
                    print(os.path.join(root, f))

if __name__ == '__main__':
    main()
