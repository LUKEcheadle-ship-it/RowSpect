# Deployment

RowSpect is local-first. The safest default is to run it on the same machine as the user and keep the Streamlit listener on loopback.

## Local production-style run

```bash
python -m venv .venv
# activate the environment
pip install -r requirements.txt
rowspect --doctor
streamlit run app.py --server.address=127.0.0.1 --server.port=8501
```

Then open `http://127.0.0.1:8501`.

## Docker

Build:

```bash
docker build -t rowspect:1.1.0 .
```

Run loopback-only:

```bash
docker run --rm -p 127.0.0.1:8501:8501 rowspect:1.1.0
```

The image runs as a non-root user and includes a health check against Streamlit's local health endpoint.

## Network deployment

If RowSpect is exposed beyond loopback, the operator owns authentication, TLS, reverse-proxy configuration, access control, logging policy, and data-retention policy. RowSpect does not provide multi-user authentication or tenant isolation.

Do not present an Internet-exposed Streamlit process as a hardened multi-tenant SaaS deployment without adding an authenticated application layer and a separate security review.

## File limits

V1.1 enforces:

- 50 MB compressed/upload size
- 250 MB maximum uncompressed XLSX archive size
- 10,000 maximum XLSX archive entries

These limits reduce accidental resource exhaustion and ZIP-bomb-style workbook expansion. They are not a malware sandbox.

## Health checks

With the app running locally:

```bash
python scripts/smoke_streamlit.py
```

The smoke test launches a temporary RowSpect server on an available loopback port, waits for Streamlit's health endpoint, requests the root page, and shuts the process down.
