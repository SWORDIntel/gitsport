# Docker Usage Guide for GitLab Mass Exporter

## Overview

The Docker setup provides two main deployment options:
1. **Batch Mode** - Runs once and exits (good for CI/CD or manual runs)
2. **Scheduled Mode** - Runs continuously on a schedule (good for automated backups)

## Current Issues with Default Docker Setup

The original `Dockerfile` and `docker-compose.yml` are configured for the async TUI version which is just a placeholder. Use the secure versions instead:
- `Dockerfile.secure` - For the working secure implementation
- `docker-compose.secure.yml` - Provides both batch and scheduled modes

## Setup Options

### Option 1: Environment Variables (Recommended for CI/CD)

Create a `.env` file:
```bash
GITLAB_PROD_URL=https://gitlab.company.com
GITLAB_PROD_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx
```

Run batch export:
```bash
docker-compose -f docker-compose.secure.yml up gitlab-exporter-batch
```

### Option 2: Encrypted Credentials (Recommended for Production)

1. Generate encrypted credentials:
```bash
./setup-docker-credentials.py
```

2. Run scheduled exports (every 24 hours):
```bash
docker-compose -f docker-compose.secure.yml up -d gitlab-exporter-scheduled
```

## Docker Commands

### Build the image
```bash
docker build -f Dockerfile.secure -t gitlab-exporter:secure .
```

### Run one-time export with env vars
```bash
docker run --rm \
  -e GITLAB_USE_ENV_VARS=true \
  -e GITLAB_INSTANCE_0_NAME=production \
  -e GITLAB_INSTANCE_0_URL=https://gitlab.example.com \
  -e GITLAB_INSTANCE_0_TOKEN=glpat-xxxxxxxxxxxx \
  -v $(pwd)/exports:/app/exports \
  gitlab-exporter:secure
```

### Run with encrypted credentials
```bash
docker run --rm \
  -v $(pwd)/credentials.enc:/app/credentials.enc:ro \
  -v $(pwd)/exports:/app/exports \
  gitlab-exporter:secure
```

## Kubernetes Deployment

For Kubernetes, use environment variables with secrets:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: gitlab-exporter
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: gitlab-exporter
            image: gitlab-exporter:secure
            env:
            - name: GITLAB_USE_ENV_VARS
              value: "true"
            - name: GITLAB_INSTANCE_0_NAME
              value: "production"
            - name: GITLAB_INSTANCE_0_URL
              value: "https://gitlab.example.com"
            - name: GITLAB_INSTANCE_0_TOKEN
              valueFrom:
                secretKeyRef:
                  name: gitlab-tokens
                  key: production-token
            volumeMounts:
            - name: exports
              mountPath: /app/exports
          volumes:
          - name: exports
            persistentVolumeClaim:
              claimName: gitlab-exports-pvc
          restartPolicy: OnFailure
```

## Monitoring Exports

Check logs:
```bash
docker-compose -f docker-compose.secure.yml logs -f gitlab-exporter-scheduled
```

Check export status:
```bash
ls -la exports/*/
cat exports/*/export.log
```

## Security Notes

1. **Never include tokens in docker-compose.yml** - Use environment variables or .env files
2. **Add to .gitignore**:
   ```
   .env
   credentials.enc
   exports/
   ```
3. **Use read-only mounts** for credentials (`:ro`)
4. **Set resource limits** to prevent runaway containers

## Troubleshooting

### Container exits immediately
- Check if credentials are properly configured
- View logs: `docker logs gitlab-exporter-batch`

### No exports created
- Verify GitLab URL and token are correct
- Check network connectivity from container
- Ensure export directory has proper permissions

### Out of memory
- Increase memory limits in docker-compose.yml
- Reduce concurrent exports in export_settings.json