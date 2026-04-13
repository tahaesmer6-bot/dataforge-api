# DataForge API 🔧

> All-in-one data validation, analysis & generation API.  
> Built to sell on **RapidAPI Marketplace** — zero customer interaction, recurring revenue.

## Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/validate/email` | POST/GET | Full email validation (syntax, MX, disposable, score) |
| `/validate/email/bulk` | POST | Bulk email validation (up to 50) |
| `/validate/phone` | POST/GET | Phone validation, carrier, type, formatting |
| `/validate/url` | POST/GET | URL validation + optional live check |
| `/analyze/text` | POST | Full text analysis (readability, sentiment, stats) |
| `/analyze/text/word-count` | POST | Quick word count |
| `/analyze/text/reading-time` | POST | Reading/speaking time estimation |
| `/hash` | POST/GET | Generate hash (MD5, SHA256, SHA512, etc.) |
| `/hash/all` | POST | Hash with ALL algorithms at once |
| `/hash/hmac` | POST | Generate HMAC signature |
| `/hash/compare` | POST | Compare text against hash |
| `/generate/password` | POST/GET | Secure password generator |
| `/generate/uuid` | POST/GET | UUID v4 generator |
| `/generate/token` | POST/GET | Secure token generator |
| `/qr` | POST | Generate QR code (base64 response) |
| `/qr` | GET | Generate QR code (direct image response) |
| `/lookup/ip` | GET | IP geolocation & network info |
| `/lookup/ip/me` | GET | Lookup caller's own IP |

## Quick Start (Local)

```bash
# 1. Clone & install
cd MONEYISMONEYULAN
pip install -r requirements.txt

# 2. Run
uvicorn app.main:app --reload

# 3. Open docs
# http://localhost:8000/docs
```

## Quick Start (Docker)

```bash
docker-compose up --build
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

## Deploy to Render.com (FREE)

1. Push code to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Render auto-detects `render.yaml` — just click Deploy
5. Your API will be live at `https://dataforge-api.onrender.com`

## Publish to RapidAPI (Start Earning)

### Step 1: Get Your API URL
After deploying to Render, your URL will be:
```
https://dataforge-api.onrender.com
```

### Step 2: Create RapidAPI Account
1. Go to [rapidapi.com/provider](https://rapidapi.com/provider)
2. Sign up / log in

### Step 3: Add Your API
1. Click **"My APIs"** → **"Add New API"**
2. Fill in:
   - **Name:** DataForge API
   - **Description:** All-in-one data validation, analysis & generation. Email validation, text analysis, QR codes, hashing, password generation, IP geolocation, phone validation.
   - **Category:** Data
   - **Base URL:** `https://dataforge-api.onrender.com`

### Step 4: Define Endpoints
Add each endpoint from the table above. For each:
- Set the HTTP method (GET/POST)
- Add request parameters matching the Pydantic models
- Add example responses

**Pro tip:** Import from OpenAPI spec:
```
https://dataforge-api.onrender.com/openapi.json
```
RapidAPI can auto-generate all endpoints from this.

### Step 5: Set Pricing
Recommended pricing tiers:

| Plan | Price | Requests/month | Rate limit |
|---|---|---|---|
| **Basic** | FREE | 100 | 10/min |
| **Pro** | $9.99/mo | 5,000 | 30/min |
| **Ultra** | $29.99/mo | 25,000 | 60/min |
| **Mega** | $79.99/mo | 100,000 | 120/min |

### Step 6: Security
1. In RapidAPI dashboard, get your **Proxy Secret**
2. Set it in your `.env`:
   ```
   RAPIDAPI_PROXY_SECRET=your_secret_here
   ```
3. Redeploy — now only RapidAPI subscribers can access

### Step 7: Optimize Listing
- Write detailed descriptions for each endpoint
- Add code examples (cURL, Python, JavaScript, PHP)
- Add a logo/icon
- Write a comprehensive "About" section
- Add API changelog

## Revenue Expectations (Realistic)

| Subscribers | Plan | Monthly Revenue |
|---|---|---|
| 5 | Pro ($9.99) | $49.95 |
| 20 | Pro ($9.99) | $199.80 |
| 5 | Ultra ($29.99) | $149.95 |
| 50 mixed | Various | $500-1500 |

**RapidAPI takes 20% commission.** Net = 80% of above.

## Tech Stack

- **FastAPI** — High performance Python API framework
- **Pydantic** — Request/response validation
- **dnspython** — DNS/MX record lookups
- **phonenumbers** — Google's phone number library
- **qrcode** — QR code generation
- **slowapi** — Rate limiting
- **httpx** — Async HTTP client
- **uvicorn** — ASGI server

## Project Structure

```
├── app/
│   ├── main.py              # FastAPI app & router setup
│   ├── config.py            # Settings & environment
│   ├── middleware/
│   │   └── rate_limiter.py  # Rate limiting
│   ├── routers/
│   │   ├── email_validator.py
│   │   ├── phone_validator.py
│   │   ├── url_validator.py
│   │   ├── text_analyzer.py
│   │   ├── hash_tools.py
│   │   ├── generators.py
│   │   ├── qr_code.py
│   │   └── ip_lookup.py
│   └── services/
│       ├── email_service.py
│       ├── phone_service.py
│       ├── text_service.py
│       ├── hash_service.py
│       ├── qr_service.py
│       ├── url_service.py
│       ├── ip_service.py
│       └── disposable_domains.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── render.yaml
├── Procfile
├── .env.example
└── .gitignore
```

## License

MIT
