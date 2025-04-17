# Deploying to Google Cloud Run

This guide helps you deploy the Real Estate Property Chatbot API to Google Cloud Run.

## Prerequisites

1. [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed and configured
2. Docker installed on your local machine
3. A Google Cloud project with billing enabled
4. Enable required APIs:
   - Cloud Run API
   - Container Registry API
   - Artifact Registry API

## Steps to Deploy

### 1. Authenticate with Google Cloud

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### 2. Build the Docker Image

```bash
# Build the image locally
docker build -t gcr.io/YOUR_PROJECT_ID/real-estate-chatbot:latest .
```

### 3. Configure Docker for Google Cloud

```bash
# Configure Docker to use gcloud as a credential helper
gcloud auth configure-docker
```

### 4. Push the Image to Google Container Registry

```bash
# Push the image to Google Container Registry
docker push gcr.io/YOUR_PROJECT_ID/real-estate-chatbot:latest
```

### 5. Deploy to Cloud Run

```bash
gcloud run deploy real-estate-chatbot \
  --image gcr.io/YOUR_PROJECT_ID/real-estate-chatbot:latest \
  --platform managed \
  --allow-unauthenticated \
  --region us-central1 \
  --port 8002
```

### 6. Access Your Deployed Service

After deployment is complete, the command will display the service URL. You can also find it in the Google Cloud Console under Cloud Run.

Your API will be available at:
```
https://real-estate-chatbot-HASH.a.run.app
```

## Environment Variables

If needed, you can set environment variables during deployment:

```bash
gcloud run deploy real-estate-chatbot \
  --image gcr.io/YOUR_PROJECT_ID/real-estate-chatbot:latest \
  --platform managed \
  --allow-unauthenticated \
  --region us-central1 \
  --port 8002 \
  --set-env-vars="GEMINI_API_KEY=your_api_key"
```

## Updating Your Deployment

To update your deployed service after making changes:

1. Build a new image with a new tag
   ```bash
   docker build -t gcr.io/YOUR_PROJECT_ID/real-estate-chatbot:v2 .
   ```

2. Push the new image
   ```bash
   docker push gcr.io/YOUR_PROJECT_ID/real-estate-chatbot:v2
   ```

3. Update the Cloud Run service
   ```bash
   gcloud run deploy real-estate-chatbot \
     --image gcr.io/YOUR_PROJECT_ID/real-estate-chatbot:v2 \
     --platform managed \
     --region us-central1
   ```

## Troubleshooting

### Viewing Logs

```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=real-estate-chatbot" --limit 20
```

### Checking Service Status

```bash
gcloud run services describe real-estate-chatbot --platform managed --region us-central1
``` 