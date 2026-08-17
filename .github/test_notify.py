import hmac
import hashlib
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import notify


def test_hmac_signature():
    secret = "s3cret"
    body, signature = notify.build_payload(
        repo="org/student-repo",
        run_id="12345",
        branch="main",
        commit="abc123",
        status="success",
        secret=secret,
    )
    expected = "sha256=" + hmac.new(
        secret.encode(), body, hashlib.sha256
    ).hexdigest()
    assert signature == expected, (signature, expected)
    payload = json.loads(body.decode())
    assert payload == {
        "repo": "org/student-repo",
        "run_id": "12345",
        "branch": "main",
        "commit": "abc123",
        "status": "success",
    }


if __name__ == "__main__":
    test_hmac_signature()
    print("PASS")
