# SplitPost — Architecture & Decisions

## Architecture
```
api/ (FastAPI routers)
  ├── auth.py      → JWT register/login/me
  ├── posts.py     → split, list, get, delete
  └── health.py    → healthcheck
services/
  ├── auth_service.py     → token creation, user auth
  ├── adapt_service.py    → LLM adaptation logic
  └── platform_rules.py   → platform specs & tones
repositories/
  ├── user_repo.py   → CRUD users, pbkdf2_hmac passwords
  └── post_repo.py   → CRUD posts + adaptations
schemas/
  ├── user.py   → RegisterRequest, LoginRequest, AuthResponse
  └── post.py   → SplitRequest, PostResponse, AdaptationResponse
core/
  ├── config.py    → Settings with SP_ env prefix
  ├── database.py  → aiosqlite init with WAL mode
  └── deps.py      → FastAPI deps (DbDep, UserDep)
```

## Key Decisions

### JWT sub must be string
PyJWT ≥2.10 validates `sub` claim as string. Passing int causes "Subject must be a string" error.
Fix: `str(user_id)` when encoding, `int(payload["sub"])` when decoding.

### Passwords: stdlib only
Using `hashlib.pbkdf2_hmac` + `hmac.compare_digest` instead of passlib/bcrypt.
Reason: passlib has compatibility issues with newer bcrypt versions.

### LLM: Gemini Flash via OpenRouter
Model: `google/gemini-2.0-flash-001`. Fast, free tier, good at structured JSON output.
Fallback: keyword-based truncation when no API key.

### Platform rules as data
Each platform defined with: char_limit, style description, hashtag_count, supports_threads.
Easy to add new platforms without code changes.

## Changelog
- v0.1.0 (2026-03-20): Initial release — auth, 5 platforms, 5 tones, dark editorial UI
