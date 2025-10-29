# Railway Deployment Guide

Deploy your Compliance Master API to Railway in minutes!

## 🚂 What is Railway?

Railway is a modern platform-as-a-service (PaaS) that makes deploying applications incredibly simple. It automatically detects your Dockerfile and handles the deployment.

## ✅ Your Project is Railway-Ready!

Your project includes:
- ✅ `Dockerfile` - Optimized for Railway with dynamic port support
- ✅ `railway.json` - Railway configuration file
- ✅ `.gitignore` - Protects sensitive files
- ✅ Health check endpoint at `/health`

## 🚀 Deployment Steps

### Option 1: Deploy via GitHub (Recommended)

This is the easiest method since your code is already on GitHub.

**Step 1: Sign Up for Railway**
1. Go to https://railway.app
2. Sign up with your GitHub account (mattcoast-sun)
3. Authorize Railway to access your GitHub repositories

**Step 2: Create New Project**
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose **"mattcoast-sun/Compliance_Master"**
4. Railway will automatically detect your Dockerfile

**Step 3: Configure Environment Variables**
1. In your Railway project, click on your service
2. Go to **"Variables"** tab
3. Add these required variables:
   ```
   WATSONX_API_KEY=your-ibm-cloud-api-key
   WATSONX_PROJECT_ID=your-watsonx-project-id
   WATSONX_URL=https://us-south.ml.cloud.ibm.com
   GRANITE_MODEL_ID=ibm/granite-13b-chat-v2
   ```
4. Railway automatically provides `PORT` - don't set it manually!

**Step 4: Deploy**
1. Railway will automatically build and deploy
2. Wait for the build to complete (~3-5 minutes)
3. Once deployed, you'll see a green "Active" status

**Step 5: Get Your Public URL**
1. Go to **"Settings"** tab
2. Click **"Generate Domain"** under "Domains"
3. Railway will give you a URL like: `https://compliance-master-production.up.railway.app`
4. Your API is now live! 🎉

**Step 6: Test Your Deployment**
```bash
# Replace with your Railway URL
curl https://your-app.up.railway.app/health

# Expected response:
# {"status":"healthy","version":"1.0.0"}
```

### Option 2: Deploy via Railway CLI

**Step 1: Install Railway CLI**
```bash
# macOS/Linux
brew install railway

# Or via npm
npm install -g @railway/cli
```

**Step 2: Login**
```bash
railway login
```

**Step 3: Initialize and Deploy**
```bash
cd /Users/mattiasacosta/Documents/Programming_Projects/Compliance_Master

# Link to Railway project (creates new one if doesn't exist)
railway link

# Add environment variables
railway variables set WATSONX_API_KEY="your-api-key"
railway variables set WATSONX_PROJECT_ID="your-project-id"
railway variables set WATSONX_URL="https://us-south.ml.cloud.ibm.com"
railway variables set GRANITE_MODEL_ID="ibm/granite-13b-chat-v2"

# Deploy
railway up
```

**Step 4: Open Your App**
```bash
railway open
```

## 🔧 Configuration

### Environment Variables

Railway requires these environment variables:

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `WATSONX_API_KEY` | IBM Cloud API Key | ✅ Yes | `abc123...` |
| `WATSONX_PROJECT_ID` | WatsonX Project ID | ✅ Yes | `project-123...` |
| `WATSONX_URL` | WatsonX API URL | ✅ Yes | `https://us-south.ml.cloud.ibm.com` |
| `GRANITE_MODEL_ID` | Model to use | No | `ibm/granite-13b-chat-v2` |
| `PORT` | Server port | Auto-set by Railway | `8765` (local) |

**Important:** Railway automatically sets `PORT` - don't override it!

### Custom Domain

1. In Railway dashboard, go to your service
2. Click **"Settings"** → **"Domains"**
3. Click **"Custom Domain"**
4. Add your domain (e.g., `api.yourdomain.com`)
5. Update your domain's DNS with Railway's CNAME

### Automatic Deployments

Railway automatically deploys when you push to GitHub:

```bash
# Make changes locally
git add .
git commit -m "Update API endpoints"
git push origin main

# Railway automatically detects the push and redeploys! 🚀
```

## 📊 Monitoring

### View Logs
```bash
# Via CLI
railway logs

# Or in the dashboard:
# Click your service → "Deployments" → Click latest deployment
```

### Metrics
- Railway provides built-in metrics for CPU, Memory, and Network usage
- Access via dashboard under "Metrics" tab

### Health Checks
- Railway automatically monitors `/health` endpoint
- Service restarts automatically if health check fails

## 💰 Pricing

Railway offers:
- **Free Tier**: $5 of free usage per month (sufficient for testing)
- **Pay As You Go**: ~$5-20/month for this API depending on usage
- **Pro Plan**: $20/month with more resources

Estimated costs for Compliance Master API:
- Hobby/Testing: ~$5-10/month
- Production: ~$15-30/month

## 🔄 Updates and Rollbacks

### Deploy New Version
```bash
git push origin main  # Automatic deployment
```

### Rollback to Previous Version
1. Go to Railway dashboard
2. Click **"Deployments"**
3. Find a previous successful deployment
4. Click **"⋮"** menu → **"Redeploy"**

## 🔐 Security Best Practices

1. **Never commit `.env` file** - ✅ Already configured in `.gitignore`
2. **Use Railway environment variables** - Set sensitive data in Railway dashboard
3. **Enable HTTPS** - Railway provides HTTPS by default
4. **Restrict access** - Consider adding API key authentication for production

## 🐛 Troubleshooting

### Build Fails

**Problem:** Docker build fails
- Check Railway logs for specific error
- Ensure all dependencies in `requirements.txt` are compatible
- Try building locally first: `docker build -t test .`

### Service Crashes on Start

**Problem:** Service starts but immediately crashes
- Check environment variables are set correctly
- View logs: `railway logs`
- Ensure `WATSONX_API_KEY` and `WATSONX_PROJECT_ID` are valid

### Health Check Fails

**Problem:** Railway shows "Unhealthy"
- Check `/health` endpoint returns 200 status
- Verify WatsonX credentials are working
- Check logs for startup errors

### Port Issues

**Problem:** "Port already in use" or connection errors
- Don't set `PORT` environment variable manually
- Railway automatically provides it
- The Dockerfile uses `${PORT:-8765}` for compatibility

## 🎯 Post-Deployment Tasks

### 1. Update watsonx Orchestrate
```bash
# Get your Railway URL
railway open

# Update openapi_orchestrate.json with your Railway URL:
# "servers": [{"url": "https://your-app.up.railway.app"}]

# Upload the updated spec to watsonx Orchestrate
```

### 2. Test All Endpoints
```bash
# Get your Railway URL
export RAILWAY_URL="https://your-app.up.railway.app"

# Test health
curl $RAILWAY_URL/health

# Test with a document (replace with your file)
curl -X POST "$RAILWAY_URL/api/v1/parse-document" \
  -F "file=@sample_device_calibration_procedure.docx"
```

### 3. Update Documentation
Update your `openapi_orchestrate.json`:
```json
{
  "servers": [
    {
      "url": "https://your-app.up.railway.app",
      "description": "Production server on Railway"
    }
  ]
}
```

## 📚 Additional Resources

- **Railway Docs**: https://docs.railway.app
- **Railway Discord**: https://discord.gg/railway
- **Railway Status**: https://status.railway.app

## 🆘 Need Help?

1. Check Railway logs: `railway logs`
2. Review this guide's troubleshooting section
3. Check Railway documentation
4. Post in Railway Discord community

## ✨ Success Checklist

- [ ] Railway account created
- [ ] Project deployed from GitHub
- [ ] Environment variables configured
- [ ] Domain generated and accessible
- [ ] `/health` endpoint returns healthy status
- [ ] Test document upload works
- [ ] OpenAPI spec updated with Railway URL
- [ ] Imported to watsonx Orchestrate
- [ ] Tested end-to-end workflow

---

🎉 **Congratulations!** Your Compliance Master API is now deployed on Railway and ready for production use!

