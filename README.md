# CloudBox — cloud-based file storage

CloudBox is a complete mini-project for demonstrating cloud computing and DevOps. It provides a responsive browser application where users can register, upload, list, download, and delete files. Local development uses SQLite and a local uploads folder; production uses PostgreSQL metadata and Amazon S3-compatible object storage.

## What is included

| Area | Implementation |
| --- | --- |
| Web application | Flask, Jinja templates, responsive HTML/CSS |
| Authentication | Registration, login, logout, hashed passwords |
| File features | Upload, list, download, delete, per-user ownership |
| Metadata | SQLite locally or PostgreSQL in production |
| Object storage | Local disk, Amazon S3, or MinIO through one adapter |
| Testing | pytest lifecycle and access-control tests |
| Packaging | Dockerfile and Docker Compose |
| CI/CD | GitHub Actions: test → Docker build/publish → Render hook |
| Deployment | Render blueprint with managed PostgreSQL |

## Fastest Windows setup

Open **PowerShell** in this folder.

### 1. Create a virtual environment

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

If PowerShell blocks activation, run PowerShell once as your user and execute:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### 2. Configure local development

```powershell
Copy-Item .env.example .env
```

The default `.env` uses local storage, so no AWS account is needed for the first demo. Change `SECRET_KEY` to a long random value if the application will be shared.

### 3. Run and test

```powershell
python app.py
```

Open <http://127.0.0.1:5000>. In a second PowerShell window:

```powershell
pytest
```

## Docker run

With Docker Desktop running:

```powershell
```

Open <http://localhost:8000>. Local database and uploads are persisted in the `data` folder.

To run against an S3-compatible local MinIO service instead:

```powershell
```

Then use:

- App: <http://localhost:8000>
- MinIO console: <http://localhost:9001>
- MinIO login: `minioadmin` / `minioadmin123`

## Configure Amazon S3

1. Create an S3 bucket in the AWS console, for example `manthan-cloudbox-files`.
2. Keep **Block Public Access** enabled. The application streams downloads through authenticated routes, so objects do not need to be public.
3. Create an IAM user with a policy scoped to only this bucket. Replace `YOUR_BUCKET` below:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:ListBucket"],
      "Resource": "arn:aws:s3:::YOUR_BUCKET"
    },
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
      "Resource": "arn:aws:s3:::YOUR_BUCKET/*"
    }
  ]
}
```

4. Put these values in `.env` (never commit them):

```dotenv
STORAGE_BACKEND=s3
S3_BUCKET=manthan-cloudbox-files
S3_REGION=ap-south-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
S3_ENDPOINT_URL=
```

5. Restart the app and upload a file. Verify the object appears in S3. AWS credentials are read by boto3 from environment variables.

## GitHub setup

The public profile currently has `Manthan-s-prj`. To create a separate repository for this project:

```powershell
git init
git add .
git commit -m "Create CloudBox file storage project"
git branch -M main
git remote add origin https://github.com/Manthan-Birwadkar/devops-mini-project.git
git push -u origin main
```

The `devops-mini-project` repository is already created for this project. If you are setting it up from a fresh local folder, run the commands above from the project root.

The workflow runs automatically for pull requests and pushes to `main`:

1. Install dependencies and run `pytest`.
2. On `main`, build and publish a Docker image to GitHub Container Registry.
3. If `RENDER_DEPLOY_HOOK` is configured, trigger a Render deployment.

The workflow does not require AWS secrets because the tests use local storage. Production secrets belong in the hosting platform, not in GitHub source code.

## Deploy to Render

1. Push this project to GitHub.
2. In Render, choose **New → Blueprint** and select the repository. Render reads `render.yaml`, creates the web service and PostgreSQL database, and builds the Dockerfile.
3. In the Render service environment variables, set:
   - `S3_BUCKET` — your bucket name
   - `AWS_ACCESS_KEY_ID` — IAM access key
   - `AWS_SECRET_ACCESS_KEY` — IAM secret key
   - `S3_REGION` — bucket region, such as `ap-south-1`
4. Open the service URL and verify `/healthz` returns `{"status":"ok"}`.
5. In Render service settings, create a **Deploy Hook**. Add it to GitHub as a repository secret named `RENDER_DEPLOY_HOOK`. You can leave the secret absent while demonstrating CI only; the workflow will safely skip deployment.

## Project structure

```text
cloud-file-storage/
├── .github/workflows/ci-cd.yml
├── docs/architecture.md
├── docs/demo-script.md
├── storage_app/
│   ├── templates/
│   ├── static/css/style.css
│   ├── auth.py
│   ├── config.py
│   ├── files.py
│   ├── models.py
│   └── storage.py
├── tests/
├── Dockerfile
├── docker-compose.yml
├── render.yaml
├── requirements.txt
└── README.md
```

## Troubleshooting

- **Port already in use:** run `flask --app wsgi run --port 5001` or change the Docker port mapping.
- **S3 upload fails:** verify the bucket region, IAM policy, and environment variable names. Do not add spaces or quotes around values in `.env`.
- **Render database URL error:** redeploy after the managed database finishes provisioning. The application automatically converts a legacy `postgres://` URL.
- **Files disappear locally:** use Docker Compose, which mounts `./data` to `/app/instance`; plain temporary containers do not preserve container files.

## Security and scope

This is an educational mini-project. It demonstrates authenticated ownership checks, private object storage, hashed passwords, upload limits, allowed extensions, automated tests, containerization, and deployment automation. For a larger production system, add CSRF protection, virus scanning, rate limiting, object lifecycle policies, and centralized logging.
