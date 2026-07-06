# Security & Infrastructure Checklist

## Completed

### Authentication & Authorization

* JWT authentication enabled.
* Refresh token rotation configured.
* Token blacklist enabled.
* Secure authentication settings reviewed.

### Database Security

* ORM used instead of unsafe raw SQL.
* SQL injection scan completed.
* No unsafe `cursor.execute()` usage found.
* AuditLog optimized with indexes.

### Dependency Scanning

* Bandit integrated.
* pip-audit integrated.
* Security workflow added to GitHub Actions.

### CI/CD

* GitHub Actions configured.
* Automatic migrations in CI.
* Automated Django tests.
* Automated security scans.

### Caching

* Redis cache toggle implemented.
* Local development uses LocMemCache.
* Production automatically uses Redis when `REDIS_URL` is configured.

### Performance

* Slow Query Middleware added.
* Query execution time logging enabled.

### Logging

* Security logging enabled.
* Database logging configured.
* Rotating log files configured.

---

## Production Environment Variables

Required:

* SECRET_KEY
* ALLOWED_HOSTS
* DATABASE_URL (or DB_HOST / DB_NAME / DB_USER / DB_PASSWORD)
* REDIS_URL
* VODAFONE_WEBHOOK_SECRET_TOKEN
* VODAFONE_RECEIVER_NUMBER

Optional:

* LOG_FILE
* SECURITY_LOG_FILE
* SLOW_QUERY_THRESHOLD_MS

---

## Verification Commands

Run migrations:

```bash
python manage.py migrate
```

Run tests:

```bash
python manage.py test
```

Security scan:

```bash
bandit -r backend -n 5
pip-audit
```

Run locally:

```bash
python manage.py runserver
```
