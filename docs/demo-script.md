# Five-minute demonstration script

Use this exact sequence for the demonstration described in the assignment.

## 1. Show the application

Run `python app.py` and open <http://127.0.0.1:5000>. Create an account, upload a small PDF or TXT file, and show it in the dashboard. Click the download icon and then delete it.

## 2. Show the repository

Open the GitHub repository and point out:

- `storage_app/` — Flask application and storage adapter
- `tests/` — automated tests
- `Dockerfile` — container packaging
- `.github/workflows/ci-cd.yml` — CI/CD pipeline

## 3. Make a visible code change

Change a harmless UI phrase in `storage_app/templates/landing.html`, for example `Your files,` to `Your files are ready,`. Then run:

```bash
git add .
git commit -m "Update landing page message"
git push origin main
```

## 4. Show GitHub Actions

Open the **Actions** tab. Show the workflow starting from the push, then open the **Test application** job and its `pytest` output. On a successful run, each job has a green check mark.

## 5. Show deployment

Open the Render service URL and refresh after deployment completes. Upload a file again to show the deployed application. When using AWS S3, the object will appear in the configured bucket.
