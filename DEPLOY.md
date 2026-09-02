# Deploying the demo

A single-server Docker Compose deployment: Caddy terminates HTTPS and proxies to
the TanStack frontend, which talks to the FastAPI AI service over the internal
compose network. Postgres and Qdrant stay on that network and are never exposed.

Budget about 45 minutes end to end, most of it waiting on the AI image build.

## 0. What you need first

| Item | Notes |
|---|---|
| A server | 4 vCPU / **8 GB RAM** minimum. Torch plus the 300M embedding model needs ~3 GB resident before any request arrives; 4 GB leaves no headroom and the service gets OOM-killed mid-evaluation. |
| A domain name | Required. WorkOS will not accept a bare IP as a redirect URI, and Caddy cannot issue a certificate for one. A free DuckDNS subdomain works. |
| `GROQ_API_KEY` | Evaluation model. |
| `OPENROUTER_API_KEY` | Only used by the LLM framework-extraction path. The NDI catalog is already built, so this is optional for the demo. |
| `HF_TOKEN` | `google/embeddinggemma-300m` is gated. **Needed at image build time**, not just at runtime. |
| WorkOS credentials | Client ID, API key, cookie password. |

### Why 8 GB

Render's free tier is 512 MB and Fly's is 256 MB. Neither can hold torch, and no
amount of image slimming changes that. Hetzner CX32 (~€7/mo) is the low-drama
option. Oracle Cloud's Always Free ARM instance (4 cores / 24 GB) is genuinely
free and this repo builds for ARM, but A1 capacity is often unavailable and the
signup is slow — not what you want the week of a conference.

## 1. Prepare the server

```bash
ssh root@YOUR_SERVER_IP

curl -fsSL https://get.docker.com | sh
apt-get update && apt-get install -y git

# Only 22, 80 and 443 should be reachable. Compose binds Postgres and Qdrant to
# the host in the base file; the prod overlay closes them, but a firewall means
# a mistake in the overlay is not immediately an exposed database.
ufw allow 22/tcp && ufw allow 80/tcp && ufw allow 443/tcp && ufw --force enable
```

## 2. Point the domain at the server

Create an **A record** for your domain pointing at the server's IPv4 address.
Confirm it resolves before continuing — Caddy's certificate request fails if the
domain does not yet reach this machine:

```bash
dig +short YOUR_DOMAIN     # must print the server IP
```

If you use Cloudflare, set the record to **DNS only** (grey cloud). Cloudflare's
proxy caps a response at 100 seconds and that limit cannot be raised on the free
plan; a full evaluation runs longer and would be cut off mid-request.

## 3. Clone and configure

```bash
git clone <your-repo-url> /opt/governance-agent
cd /opt/governance-agent
cp example.env .env
nano .env
```

Set these — the rest of `example.env` can stay as shipped:

```bash
PUBLIC_DOMAIN=grc-demo.example.com          # no https://, no trailing slash
WORKOS_REDIRECT_URI=https://grc-demo.example.com/api/auth/callback

GROQ_API_KEY=gsk_...
HF_TOKEN=hf_...
WORKOS_CLIENT_ID=client_...
WORKOS_API_KEY=sk_...

# openssl rand -base64 24
WORKOS_COOKIE_PASSWORD=...
# openssl rand -hex 32
AI_SERVICE_KEY=...
# openssl rand -base64 18
POSTGRES_PASSWORD=...

NODE_ENV=production
```

`AI_SERVICE_KEY` is what stops anyone from calling the AI service directly. If
it is empty the service starts **unauthenticated on purpose** and only logs a
warning, so do not leave it blank.

## 4. Build and start

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

The AI image build downloads torch and the embedding model. Expect 15-30 minutes
the first time and a few GB of disk. Watch it with:

```bash
docker compose logs -f
```

Startup order is handled for you: Postgres becomes healthy, the one-shot
`migrate` service creates the tables, then the frontend starts. If `migrate`
fails the frontend will not start — that is deliberate, because a frontend on an
empty database fails confusingly on the first query instead of at boot.

## 5. Index the NDI framework into Qdrant

The control catalog ships in `services/ai-service/config/frameworks/NDI/`, but
the vector store starts empty and has to be populated once:

```bash
docker compose exec ai_service python -c \
  "from src.rag import index_framework; index_framework('NDI')"
```

Verify it landed:

```bash
docker compose exec ai_service python -c \
  "import os; from qdrant_client import QdrantClient; \
   c = QdrantClient(url=os.environ['QDRANT_URL'], api_key=os.getenv('QDRANT_API_KEY') or None); \
   print('points:', c.get_collection('NDI_rag').points_count)"
```

A non-zero count means retrieval will work. **Zero means every evaluation will
come back empty** — the agent will still answer, it just will not be grounded in
any control.

## 6. Configure WorkOS

In the WorkOS dashboard:

1. **Redirect URI** — add `https://YOUR_DOMAIN/api/auth/callback`, exactly
   matching `WORKOS_REDIRECT_URI`.
2. **Role permissions** — create them with these exact slugs:

   ```
   submitions:read
   submitions:write
   submitions:delete
   ```

   The missing `s` is not a typo to fix right now. The application checks that
   spelling in both `packages/api/src/lib/workos.ts` and
   `apps/tanstack-start/src/lib/permissions.ts`; changing the code and the
   dashboard at the same time is a good way to lock everyone out the day before
   a demo. Match the code now, rename both together afterwards.
3. Assign the role to the accounts that will log in during the demo.

## 7. Verify before the demo

```bash
curl https://YOUR_DOMAIN/                       # 200, HTTPS valid
docker compose ps                               # every service up, migrate exited 0
```

Then, in a browser, do a real end-to-end run:

1. Log in.
2. Submit **one** small PDF under a single domain.
3. Confirm the report shows control IDs like `DG.1.1` with a decision and
   rationale — not generic prose and not an empty table.
4. Download the PDF and check any Arabic renders as joined right-to-left text.

Do this at least a day early. It is the only check that exercises WorkOS, the
database, Groq, Qdrant and PDF generation together.

## Operations

```bash
docker compose logs -f ai_service          # evaluation and retrieval logs
docker compose logs -f caddy               # certificate issues
docker compose restart frontend
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build   # redeploy
```

## Troubleshooting

**Build fails downloading the model** — `HF_TOKEN` is missing or has not
accepted the `google/embeddinggemma-300m` licence. Accept it on the model page
while signed in, then rebuild. Runtime env vars do not reach a build; the token
is passed through `build.args` in `docker-compose.yml`.

**No certificate / Caddy retries** — the A record does not point here yet, or
port 80 is blocked. Let's Encrypt validates over port 80 even for an HTTPS site.

**Login loops or "insufficient permissions"** — the WorkOS redirect URI does not
match `WORKOS_REDIRECT_URI` character for character, or the role permissions are
spelled `submissions:*` instead of `submitions:*`.

**Evaluation returns an empty report** — step 5 was skipped or reported zero
points. Re-run the indexing command.

**Request dies after ~100 seconds** — Cloudflare's proxy is on. Switch the DNS
record to grey cloud.

**AI service killed during evaluation** — out of memory. `docker stats` while a
submission runs; if `ai_service` approaches the limit, move to a larger server.

## Known limits for this build

Worth knowing before someone asks during the demo:

- An evaluation is synchronous: the browser holds the request open until every
  LLM call and the PDF are done. There is no queue and no progress indicator.
- Any signed-in user with read permission can see every submission. There is no
  per-tenant filtering.
- Uploaded documents are stored base64-encoded in Postgres, unencrypted.
- Results are attached to files by list position, so a missing per-file result
  shifts the rest onto the wrong files.
- Domain scoring in the dashboard is an unweighted average of the model's
  decisions. It is not the weighted NDI OE formula in `src/Tools/oe.py`, which
  is not wired into this path.
