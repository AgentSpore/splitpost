"""Quick smoke test for SplitPost API."""
import httpx
import sys

BASE = "http://localhost:8000"

def main():
    c = httpx.Client(base_url=BASE, timeout=30)

    # Health
    r = c.get("/health")
    assert r.status_code == 200, f"Health failed: {r.text}"
    print("✓ Health OK")

    # Register
    r = c.post("/auth/register", json={
        "username": "smoke", "email": "smoke@test.com",
        "display_name": "Smoke", "password": "smoke123"
    })
    if r.status_code == 409:
        r = c.post("/auth/login", json={"email": "smoke@test.com", "password": "smoke123"})
    assert r.status_code == 200, f"Auth failed: {r.text}"
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✓ Auth OK")

    # Me
    r = c.get("/auth/me", headers=headers)
    assert r.status_code == 200, f"Me failed: {r.text}"
    print("✓ Me OK")

    # Split (fallback mode if no API key)
    r = c.post("/posts/split", headers=headers, json={
        "text": "Testing SplitPost smoke test.",
        "tone": "casual",
        "platforms": ["twitter", "linkedin"],
    })
    assert r.status_code == 200, f"Split failed: {r.text}"
    data = r.json()
    assert len(data["adaptations"]) == 2
    print(f"✓ Split OK ({len(data['adaptations'])} adaptations)")

    # History
    r = c.get("/posts/", headers=headers)
    assert r.status_code == 200
    print(f"✓ History OK ({len(r.json())} posts)")

    print("\n🎉 All smoke tests passed!")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"✗ FAILED: {e}", file=sys.stderr)
        sys.exit(1)
