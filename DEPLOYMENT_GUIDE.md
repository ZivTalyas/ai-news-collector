# 🚀 AI News Collector - Deployment Guide

This guide will help you deploy your AI News Collector dashboard so others can access it online, with automatic daily updates.

## 🌟 **Option 1: Streamlit Community Cloud (Recommended)**

**Free, easy, and perfect for this project!**

### **Why Streamlit Community Cloud?**
- ✅ **Free hosting** for public repositories
- ✅ **Direct GitHub integration** - auto-deploys on push
- ✅ **Built for Streamlit apps**
- ✅ **Easy secrets management**
- ✅ **Automatic SSL/HTTPS**
- ✅ **No server management required**

### **Step-by-Step Deployment:**

#### **1. Push Your Code to GitHub**
```bash
# If not already done
git add .
git commit -m "Ready for deployment"
git push origin main
```

#### **2. Deploy to Streamlit Community Cloud**

1. **Go to**: [share.streamlit.io](https://share.streamlit.io)
2. **Sign in** with your GitHub account
3. **Click "New app"**
4. **Configure deployment**:
   - **Repository**: `your-username/ai-news-collector`
   - **Branch**: `main`
   - **Main file path**: `app/dashboard.py`
   - **App URL**: Choose a custom URL (e.g., `ai-news-today`)

#### **3. Add Your Secrets**

In your Streamlit Cloud app settings, add your secrets:

```toml
# Secrets section in Streamlit Cloud
MONGO_URI = "mongodb+srv://username:password@cluster.mongodb.net/ai_news?retryWrites=true&w=majority"
```

#### **4. Deploy!**
- Click **"Deploy!"**
- Your app will be live at: `https://your-app-name.streamlit.app`

### **Automatic Updates**
Your GitHub Actions will run daily and update the database. The dashboard will automatically show new data because it connects to the same MongoDB database!

---

## 🚀 **Option 2: Railway (Alternative)**

Modern, developer-friendly platform with great GitHub integration.

### **Steps:**

#### **1. Create Railway Account**
- Go to [railway.app](https://railway.app)
- Sign up with GitHub

#### **2. Deploy from GitHub**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway link
railway up
```

#### **3. Add Environment Variables**
In Railway dashboard:
- Add `MONGO_URI` with your MongoDB connection string
- Set `PORT` to `8501`

#### **4. Configure Build**
Create `railway.toml`:
```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "streamlit run app/dashboard.py --server.port $PORT --server.address 0.0.0.0"
```

---

## 🔧 **Option 3: Render (Heroku Alternative)**

Great free tier with automatic deployments.

### **Steps:**

#### **1. Create Render Account**
- Go to [render.com](https://render.com)
- Connect your GitHub account

#### **2. Create Web Service**
- **Repository**: Select your `ai-news-collector` repo
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `streamlit run app/dashboard.py --server.port $PORT --server.address 0.0.0.0`

#### **3. Environment Variables**
Add in Render dashboard:
```
MONGO_URI=your_mongodb_connection_string
```

---

## 🐳 **Option 4: Docker + Any Cloud Platform**

For more control and scalability.

### **Create Dockerfile:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run the application
CMD ["streamlit", "run", "app/dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### **Deploy to:**
- **Google Cloud Run**: `gcloud run deploy`
- **AWS ECS/Fargate**: Using AWS CLI
- **DigitalOcean App Platform**: Connect GitHub repo
- **Azure Container Instances**: Using Azure CLI

---

## ⚙️ **Deployment Configuration Files**

### **For Vercel (Next.js-style platforms):**

Create `vercel.json`:
```json
{
  "build": {
    "env": {
      "PYTHON_VERSION": "3.11"
    }
  },
  "functions": {
    "app/dashboard.py": {
      "runtime": "python3.11"
    }
  }
}
```

---

## 🔐 **Environment Variables Setup**

### **Required Variables:**
```bash
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/ai_news?retryWrites=true&w=majority
```

### **Optional Variables:**
```bash
SCRAPER_MAX_ARTICLES=10
SCRAPER_SLEEP_INTERVAL=2
STREAMLIT_SERVER_PORT=8501
```

---

## 🔄 **How Automatic Updates Work**

### **Your Current Setup:**
1. **GitHub Actions** runs daily at 8:00 AM UTC
2. **Scraper** collects fresh AI news
3. **Database** gets updated with new articles
4. **Dashboard** shows new data automatically (no redeployment needed!)

### **Deployment + GitHub Actions Flow:**
```
Daily 8:00 AM UTC
├── GitHub Actions triggers
├── Scraper runs in GitHub runner
├── New articles saved to MongoDB
├── Your deployed dashboard automatically shows new data
└── Users see fresh content!
```

---

## 🌐 **Custom Domain (Optional)**

### **For Streamlit Cloud:**
- Free plan: `your-app.streamlit.app`
- Custom domain: Not available on free tier

### **For Railway/Render:**
- Free custom domain: `your-app.railway.app` / `your-app.onrender.com`
- Custom domain: Available on paid plans

### **DNS Setup for Custom Domain:**
```
CNAME record: your-domain.com → your-app.platform.com
```

---

## 📊 **Monitoring Your Deployment**

### **Things to Monitor:**
- **App Uptime**: Use UptimeRobot (free)
- **Database Usage**: MongoDB Atlas dashboard
- **GitHub Actions**: Check daily scraper logs
- **Error Tracking**: Streamlit logs in deployment platform

### **Health Check Endpoint:**
Your Streamlit app automatically has:
- Health check: `https://your-app.streamlit.app/_stcore/health`
- Metrics: Available in platform dashboards

---

## 🚨 **Troubleshooting Common Issues**

### **1. App Won't Start:**
```bash
# Check your requirements.txt has correct versions
# Ensure config/.env is not being deployed (use secrets instead)
# Verify app/dashboard.py path is correct
```

### **2. Database Connection Failed:**
```bash
# Verify MONGO_URI secret is set correctly
# Check MongoDB Atlas IP whitelist (allow 0.0.0.0/0 for cloud deployment)
# Ensure database user has correct permissions
```

### **3. GitHub Actions Not Working:**
```bash
# Check GitHub repository secrets
# Verify MONGO_URI secret exists
# Check Actions logs for errors
```

### **4. CSS Not Loading:**
```bash
# Ensure static/dashboard.css exists in repository
# Check file paths are correct for deployment
# Verify CSS file is being served properly
```

---

## 🎯 **Recommended Deployment Strategy**

### **For Personal/Demo Projects:**
1. **Streamlit Community Cloud** (Free, easy)

### **For Production/Team Use:**
1. **Railway** or **Render** (More control, custom domains)
2. **Google Cloud Run** (Scalable, pay-per-use)

### **For Enterprise:**
1. **AWS ECS/Fargate** or **Azure Container Instances**
2. **Kubernetes** deployment

---

## 📋 **Deployment Checklist**

- [ ] ✅ Code pushed to GitHub
- [ ] ✅ MongoDB Atlas connection string ready
- [ ] ✅ Requirements.txt updated
- [ ] ✅ Streamlit config optimized
- [ ] ✅ Choose deployment platform
- [ ] ✅ Set up environment variables/secrets
- [ ] ✅ Deploy application
- [ ] ✅ Test live deployment
- [ ] ✅ Verify GitHub Actions still work
- [ ] ✅ Share URL with others!

---

## 🔗 **Quick Links**

- **Streamlit Cloud**: [share.streamlit.io](https://share.streamlit.io)
- **Railway**: [railway.app](https://railway.app)
- **Render**: [render.com](https://render.com)
- **MongoDB Atlas**: [cloud.mongodb.com](https://cloud.mongodb.com)
- **GitHub Actions**: [github.com/your-repo/actions](https://github.com)

---

## 💡 **Pro Tips**

1. **Use Streamlit Community Cloud** for the easiest deployment
2. **Set up monitoring** to ensure your scraper keeps working
3. **Consider custom domain** for professional look
4. **Monitor database usage** to stay within free tiers
5. **Test deployment thoroughly** before sharing with others

---

**Your AI News Collector is ready to serve the world! 🌍📰** 