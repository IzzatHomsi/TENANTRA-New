#!/usr/bin/env python3
"""Encrypt and set a GitHub Actions repository secret using PyNaCl.

Usage: set_repo_secret.py <owner> <repo> <secret_name> <secret_value>
It reads GITHUB_TOKEN from the environment.
"""
import base64
import os
import sys
import requests
from nacl import public, encoding, utils


def main():
    if len(sys.argv) < 5:
        print("Usage: set_repo_secret.py <owner> <repo> <secret_name> <secret_value>")
        return 2
    owner, repo, name, value = sys.argv[1:5]
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print('GITHUB_TOKEN env var is required')
        return 3

    headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/vnd.github+json'}
    key_url = f'https://api.github.com/repos/{owner}/{repo}/actions/secrets/public-key'
    r = requests.get(key_url, headers=headers)
    r.raise_for_status()
    j = r.json()
    key = j['key']
    key_id = j['key_id']

    # key is base64 encoded public key suitable for libsodium SealedBox
    public_key = public.PublicKey(base64.b64decode(key))
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(value.encode('utf-8'))
    encrypted_b64 = base64.b64encode(encrypted).decode('utf-8')

    put_url = f'https://api.github.com/repos/{owner}/{repo}/actions/secrets/{name}'
    payload = {'encrypted_value': encrypted_b64, 'key_id': key_id}
    pr = requests.put(put_url, headers=headers, json=payload)
    if pr.status_code in (201, 204):
        print(f'Successfully set secret {name} for {owner}/{repo}')
        return 0
    else:
        print('Failed to set secret:', pr.status_code, pr.text)
        return 4


if __name__ == '__main__':
    raise SystemExit(main())
