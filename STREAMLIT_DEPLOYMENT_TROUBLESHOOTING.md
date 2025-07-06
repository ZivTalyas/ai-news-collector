# 🔧 Streamlit Cloud Deployment Troubleshooting

## Issue: "Your database is empty" on Streamlit Cloud

If your deployed app shows "Your database is empty" but MongoDB is connected, follow these steps:

### 1. ✅ Check Streamlit Secrets Configuration

**In your Streamlit Cloud app:**
1. Go to your app dashboard on [share.streamlit.io](https://share.streamlit.io)
2. Click on your app
3. Go to "Settings" → "Secrets"
4. Add your MongoDB connection string:

```toml
MONGO_URI = "mongodb+srv://username:password@cluster.mongodb.net/ai_news?retryWrites=true&w=majority"
```

**Important:** 
- Use the exact same connection string that works locally
- Don't include quotes around the value in Streamlit secrets
- Make sure there are no extra spaces or characters

### 2. ✅ Verify MongoDB Atlas Settings

**Network Access:**
1. Go to [MongoDB Atlas](https://cloud.mongodb.com)
2. Network Access → IP Access List
3. Make sure `0.0.0.0/0` is whitelisted (Allow access from anywhere)

**Database User:**
1. Database Access → Database Users
2. Verify your user has `readWrite` permissions to the database

### 3. ✅ Test Your Connection String

**Locally test with the exact same connection string:**
```bash
python3 scripts/debug_deployment.py
```

### 4. ✅ Check Database Name and Collection

Your app expects:
- **Database name**: `ai_news`
- **Collection name**: `articles`

**Verify in MongoDB Atlas:**
1. Go to "Browse Collections"
2. Check if you have `ai_news` database with `articles` collection
3. Check if the collection has documents

### 5. ✅ Force Refresh the App

**In Streamlit Cloud:**
1. Click "Reboot app" in your app dashboard
2. Or push a small change to your GitHub repository

**In the app:**
1. Click "🔄 Refresh Data" button
2. Try the debug checkbox if available

### 6. ✅ Check App Logs

**In Streamlit Cloud:**
1. Go to your app dashboard
2. Click "View logs"
3. Look for error messages about MongoDB connection

**Common error messages:**
- "SSL handshake failed" → Update pymongo in requirements.txt
- "Authentication failed" → Check username/password in connection string
- "ServerSelectionTimeoutError" → Check IP whitelist

### 7. ✅ Update Dependencies

**In requirements.txt, ensure you have:**
```
pymongo>=4.6.0
certifi>=2023.7.22
```

### 8. ✅ Test Data Collection

**If database is truly empty:**
1. Use the "🚀 Get Started - Collect AI News" button in the app
2. Or run GitHub Actions manually to collect data

### 9. ✅ MongoDB Atlas Troubleshooting

**Check cluster status:**
1. Go to MongoDB Atlas dashboard
2. Verify cluster is running (not paused)
3. Check if cluster version is 4.4+ (recommended)

**Connection string format:**
```
mongodb+srv://username:password@cluster.mongodb.net/ai_news?retryWrites=true&w=majority
```

### 10. ✅ GitHub Actions Status

**Check if your scraper is running:**
1. Go to your GitHub repository
2. Click "Actions" tab
3. Check if "Daily AI News Scraper" is running successfully
4. If it's failing, check the logs

### 🔍 Quick Debug Steps

1. **Check secrets**: Go to Streamlit Cloud → Settings → Secrets
2. **Reboot app**: Click "Reboot app" in Streamlit Cloud
3. **Check logs**: Look for error messages in app logs
4. **Test locally**: Use the same connection string locally
5. **Verify IP whitelist**: Ensure 0.0.0.0/0 is allowed in MongoDB Atlas

### 💡 Pro Tips

1. **Use the debug checkbox** in the app to see detailed connection info
2. **Test connection string** in MongoDB Compass before deployment
3. **Monitor app logs** during deployment for real-time error messages
4. **Check GitHub Actions** to ensure data is being collected

### 🚨 Still Having Issues?

1. **Check the exact error message** in Streamlit Cloud logs
2. **Verify your MongoDB Atlas cluster** is not paused
3. **Test with MongoDB Compass** using the same connection string
4. **Run the debug script** locally: `python3 scripts/debug_deployment.py`

### 📞 Common Solutions

| Issue | Solution |
|-------|----------|
| "Database is empty" | Check Streamlit secrets configuration |
| SSL handshake failed | Update pymongo version |
| Authentication failed | Check username/password in connection string |
| Network timeout | Check IP whitelist (0.0.0.0/0) |
| App won't load | Reboot app in Streamlit Cloud |

---

**Remember:** The same connection string that works locally should work in Streamlit Cloud. The main difference is using Streamlit secrets instead of environment variables. 