import hashlib
import hmac
import json
import os
import sys
import urllib.error
import urllib.request


def build_payload(repo, run_id, branch, commit, status, secret):
    payload = {
        "repo": repo,
        "run_id": run_id,
        "branch": branch,
        "commit": commit,
        "status": status,
    }
    body = json.dumps(payload, separators=(",", ":")).encode()
    return body, sign(body, secret)


def sign(body, secret):
    return "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def main():
    secret = os.environ["WEBHOOK_SECRET"]
    url = os.environ["WEBHOOK_URL"]
    body, signature = build_payload(
        repo=os.environ["REPO"],
        run_id=os.environ["RUN_ID"],
        branch=os.environ["BRANCH"],
        commit=os.environ["COMMIT"],
        status=os.environ["STATUS"],
        secret=secret,
    )
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": signature,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            print(response.status, response.read().decode(errors="replace"))
    except urllib.error.URLError as exc:
        print(f"webhook notify failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
