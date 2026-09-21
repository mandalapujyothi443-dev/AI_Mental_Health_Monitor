# Deployment Guide

This guide deploys the AI Mental Health Monitor as a Flask application. It is a
wellbeing-monitoring prototype, not a medical device or emergency service. Do
not deploy it with real patient data unless the appropriate privacy, security,
clinical, and legal reviews have been completed.

## What the application needs

- Python 3.10 or later (3.11 is a good production baseline)
- The files in `models/` (`distress_model.pkl` and `scaler.pkl`), or the data
  and tooling needed to generate them
- A writable, persistent location for the SQLite database
- A strong `SECRET_KEY`
- Optional: a Groq API key for AI text analysis, chat, and speech-to-text

The application works without a Groq key; it uses local rule-based fallbacks
for the relevant features. The API key is kept server-side and is never sent to
browser JavaScript.

## 1. Prepare the release

From the project directory:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

On Windows PowerShell, activate the environment with:

```powershell
.\.venv\Scripts\Activate.ps1
```

Confirm that the model artifacts are present:

```bash
ls models/distress_model.pkl models/scaler.pkl
```

If they are not included in the release, generate them before deployment:

```bash
python ml/train_model.py
```

Run the test suite before shipping:

```bash
pytest
```

## 2. Configure environment variables

Use your platform's secret manager or environment-variable settings. For local
testing, create a `.env` file beside `app.py`; it must not be committed.

```dotenv
SECRET_KEY=replace-with-a-long-random-value
GROQ_API_KEY=optional-groq-api-key
GROQ_MODEL=openai/gpt-oss-20b
GROQ_STT_MODEL=whisper-large-v3-turbo
```

Generate a secret key, for example:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

`SECRET_KEY` protects Flask sessions. The default value in `config.py` is for
development only and must never be used in a public deployment. Rotate the
Groq key if it is ever exposed.

## 3. Database and persistence

The default database is `database/database.db`. It is created and initialized
automatically the first time the app starts, including two demo accounts.

- Attach a persistent disk/volume and keep the `database/` directory on it.
- Back up the database regularly, encrypt backups, and restrict access.
- Do not run multiple application instances against this SQLite file. SQLite is
  appropriate for a small single-instance deployment, not horizontal scaling.
- The included demo accounts are intended only for demonstrations. Remove or
  change them before any non-demo deployment.

For a multi-instance or real-user deployment, migrate the data layer to a
managed database such as PostgreSQL before scaling.

## 4. Run in production

Do not use `python app.py` in production because it starts Flask's development
server with debug mode enabled. Install a WSGI server instead:

```bash
pip install gunicorn
gunicorn --bind 0.0.0.0:8000 --workers 1 --access-logfile - --error-logfile - app:app
```

Keep `--workers 1` when using the default SQLite database. Put a TLS-terminating
reverse proxy or your hosting platform's HTTPS endpoint in front of port 8000.

### systemd example (Linux)

Create `/etc/systemd/system/mental-health-monitor.service`, replacing the paths
and service account:

```ini
[Unit]
Description=AI Mental Health Monitor
After=network.target

[Service]
User=appuser
Group=appuser
WorkingDirectory=/srv/ai_mental_health_monitor
EnvironmentFile=/etc/ai-mental-health-monitor.env
ExecStart=/srv/ai_mental_health_monitor/.venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 1 app:app
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Store secrets in `/etc/ai-mental-health-monitor.env`, readable only by the
service account. Then enable and inspect the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now mental-health-monitor
sudo systemctl status mental-health-monitor
```

### Nginx reverse proxy example

Point an HTTPS-enabled virtual host at the local Gunicorn service:

```nginx
server {
    listen 443 ssl;
    server_name wellbeing.example.com;

    # Configure certificates here (for example, via Certbot).

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 5. Hosting-platform settings

For a managed Python host, configure:

- **Build command:** `pip install -r requirements.txt`
- **Start command:** `gunicorn --bind 0.0.0.0:$PORT --workers 1 app:app`
- **Working directory:** the directory containing `app.py`
- **Secrets:** `SECRET_KEY` and, if enabled, `GROQ_API_KEY`
- **Persistent storage:** mounted at the application directory (or adjust the
  database configuration before deployment)

If the platform has an ephemeral filesystem, its SQLite database will be lost
on redeploy or restart. Use its persistent-volume feature or move to a managed
database first.

## 6. Post-deployment checks

1. Visit the HTTPS URL and confirm it redirects to the application home page.
2. Register a test account and complete an assessment.
3. Confirm the dashboard/history data survives a service restart.
4. If Groq is enabled, test chat and a short audio transcription; otherwise
   confirm the fallback responses work.
5. Check application and reverse-proxy logs for errors, while ensuring logs do
   not retain check-in text, passwords, API keys, or other sensitive data.
6. Confirm that a backup can be restored in a separate test environment.

## Operational security checklist

- Enforce HTTPS and redirect HTTP to HTTPS.
- Set a unique `SECRET_KEY`; never commit `.env` or production databases.
- Limit database, backup, log, and secret-manager access to authorized staff.
- Establish a retention and deletion policy for wellbeing check-ins.
- Add monitoring, incident response, and a clear human escalation process
  before collecting real-user data.
- Review applicable privacy and health-data obligations for the deployment
  location and intended users.

