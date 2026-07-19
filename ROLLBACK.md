
---

## Section 1: Code Rollback

Roll back the code to the last known-good commit without touching the database.

### Prerequisites
- SSH access to the production server
- sudo access on `/opt/vitmain/`
- The last known-good git commit hash

### Steps

1. **Identify the last known-good commit:**
   ```bash
   cd /opt/vitmain
   git log --oneline -10
   # Find the commit before the deployment that caused the issue