#!/usr/bin/env python3
"""GitHub API request with a JSON body read from a file (avoids arg-length limits).

Usage: ghpost.py <METHOD> <api-path> <payload-json-file>
Auth goes through authd's surrogate exchange; no raw secrets are handled here.
"""
import json
import sys
import urllib.request

sys.path.insert(0, "/home/hatch/workspace/skills/github/bin")
sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response  # noqa: E402

BASE = "https://api.github.com"
ALLOWED_HOSTS = ["api.github.com"]
CREDENTIAL_NAME = "custom.github"

method, path, payload_file = sys.argv[1].upper(), sys.argv[2], sys.argv[3]
with open(payload_file) as f:
    data = json.dumps(json.load(f)).encode()

req = urllib.request.Request(BASE + path, data=data, method=method)
req.add_header("Accept", "application/vnd.github+json")
req.add_header("X-GitHub-Api-Version", "2022-11-28")
req.add_header("Content-Type", "application/json")
add_surrogate_to_request(req, CREDENTIAL_NAME, allowed_hosts=ALLOWED_HOSTS)
try:
    with urllib.request.urlopen(req) as resp:
        print(json.dumps(read_json_response(resp), indent=2))
except urllib.error.HTTPError as exc:
    print(f"HTTP {exc.code}: {exc.read().decode('utf-8', 'replace')}", file=sys.stderr)
    sys.exit(1)
