#!/usr/bin/env python3
"""Push the local cwi-sync workdir to GitHub via the Git Data API.

Steps:
  1. If refs/heads/main is missing: create it with README.md + .nojekyll.
  2. Create refs/heads/funnel from main (if missing).
  3. Commit the full workdir tree onto funnel.

Auth goes through authd's surrogate exchange; no raw secrets are handled here.
"""
import base64
import json
import os
import sys
import urllib.request

sys.path.insert(0, "/home/hatch/workspace/skills/github/bin")
sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response  # noqa: E402

BASE = "https://api.github.com"
REPO = "CumulativeWebInc/cwi-sync"
CRED = "custom.github"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BINARY_EXTS = {".pdf", ".jpg", ".jpeg", ".png", ".mp4"}


def api(method, path, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    add_surrogate_to_request(req, CRED, allowed_hosts=["api.github.com"])
    try:
        with urllib.request.urlopen(req) as resp:
            code = resp.status
            body = read_json_response(resp) if code != 204 else None
            return code, body
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        return exc.code, {"error": raw[:400]}


def ref_sha(branch):
    code, body = api("GET", f"/repos/{REPO}/git/ref/heads/{branch}")
    if code == 200:
        return body["object"]["sha"]
    return None


def make_blob(abs_path):
    with open(abs_path, "rb") as fh:
        raw = fh.read()
    ext = os.path.splitext(abs_path)[1].lower()
    if ext in BINARY_EXTS:
        payload = {"content": base64.b64encode(raw).decode(), "encoding": "base64"}
    else:
        payload = {"content": raw.decode("utf-8"), "encoding": "utf-8"}
    code, body = api("POST", f"/repos/{REPO}/git/blobs", payload)
    assert code == 201, body
    return body["sha"]


def workdir_files(subset=None):
    out = []
    for dirpath, _dirs, files in os.walk(ROOT):
        for fn in sorted(files):
            abs_p = os.path.join(dirpath, fn)
            rel = os.path.relpath(abs_p, ROOT)
            if rel.startswith(".git/"):
                continue
            if subset is not None and rel not in subset:
                continue
            out.append(rel)
    return out


def commit_tree(rel_paths, base_tree=None):
    tree = []
    for rel in rel_paths:
        sha = make_blob(os.path.join(ROOT, rel))
        tree.append({"path": rel, "mode": "100644", "type": "blob", "sha": sha})
        print("  blob", rel, sha[:8])
    payload = {"tree": tree}
    if base_tree:
        payload["base_tree"] = base_tree
    code, body = api("POST", f"/repos/{REPO}/git/trees", payload)
    assert code == 201, body
    return body["sha"]


def commit(tree_sha, message, parents):
    code, body = api("POST", f"/repos/{REPO}/git/commits",
                     {"message": message, "tree": tree_sha, "parents": parents})
    assert code == 201, body
    return body["sha"]


def main():
    # 1. init main if missing
    main_sha = ref_sha("main")
    if not main_sha:
        print("creating refs/heads/main ...")
        tree = commit_tree(["README.md", ".nojekyll"])
        c = commit(tree, "chore: initialize cwi-sync repo", [])
        code, _ = api("POST", f"/repos/{REPO}/git/refs",
                      {"ref": "refs/heads/main", "sha": c})
        assert code == 201, code
        main_sha = c
        print("main =", main_sha[:8])
    else:
        print("main exists at", main_sha[:8])

    # 2. create funnel branch if missing
    funnel_sha = ref_sha("funnel")
    if not funnel_sha:
        code, _ = api("POST", f"/repos/{REPO}/git/refs",
                      {"ref": "refs/heads/funnel", "sha": main_sha})
        assert code == 201, code
        funnel_sha = main_sha
        print("created refs/heads/funnel at", funnel_sha[:8])
    else:
        print("funnel exists at", funnel_sha[:8])

    # 3. commit full workdir onto funnel
    print("building funnel tree ...")
    rels = workdir_files()
    code, main_commit = api("GET", f"/repos/{REPO}/git/commits/{main_sha}")
    base_tree = main_commit["tree"]["sha"]
    tree_sha = commit_tree(rels, base_tree=base_tree)
    c = commit(tree_sha,
               "feat: sync/licensing funnel — 3 one-sheets, /license/ page, inquiry template",
               [funnel_sha])
    code, _ = api("PATCH", f"/repos/{REPO}/git/refs/heads/funnel", {"sha": c})
    assert code == 200, code
    print("funnel now at", c[:8])


if __name__ == "__main__":
    main()
