# TimeShift
Car History Repository

## Running the upload server

A simple Python server is included to allow password protected uploads that
commit changes back to this repository. To start it:

```bash
export UPLOAD_PASSWORD=yourpassword
export GITHUB_TOKEN=yourtoken # token with repo push access
python3 server.py
```

The server listens on port 8000 by default. Visit `http://localhost:8000` and
use the password to upload a file. The file is saved to the repository,
committed, and pushed to the configured `origin` remote if `GITHUB_TOKEN` is
set.
