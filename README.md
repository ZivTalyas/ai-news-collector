# 🤖 AI News Collector

A fully automated cloud-based system that collects, stores, and displays top AI news articles daily. The system scrapes trusted websites via Google search, stores data in MongoDB Atlas, and visualizes it through a live Streamlit dashboard.

## 🌟 Features

- **Automated Daily Scraping**: Searches Google for latest AI news from trusted sources
- **Smart Classification**: Automatically categorizes articles by AI tool type (LLM, Computer Vision, Robotics, etc.)
- **Deduplication**: Prevents duplicate articles using URL-based indexing
- **Live Dashboard**: Beautiful Streamlit interface with filtering and visualization
- **Cloud Deployment**: Ready for GitHub Actions, Streamlit Cloud, and MongoDB Atlas

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Scraper Bot | Python + BeautifulSoup + googlesearch-python | Extract data from web articles |
| Scheduler | GitHub Actions | Run scraper daily automatically |
| Database | MongoDB Atlas | Cloud-hosted NoSQL database |
| Dashboard | Streamlit | Live visualization of news entries |

## 📦 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/ai-news-collector.git
cd ai-news-collector
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
```bash
# Copy the environment template
cp env_template.txt .env

# Edit .env with your MongoDB Atlas connection string
# MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/ai_news?retryWrites=true&w=majority
```

## 🗄️ Database Setup (MongoDB Atlas)

1. **Create MongoDB Atlas Account**: Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
2. **Create a Cluster**: Choose the free tier
3. **Create Database User**: 
   - Database Access → Add New Database User
   - Choose password authentication
4. **Whitelist IP Address**: 
   - Network Access → Add IP Address → Allow Access from Anywhere (0.0.0.0/0)
5. **Get Connection String**: 
   - Clusters → Connect → Connect your application
   - Copy the connection string and add to your `.env` file

## 🚀 Usage

### Running the Scraper Locally
```bash
python scraper.py
```

### Running the Dashboard Locally
```bash
streamlit run dashboard.py
```
Access the dashboard at `http://localhost:8501`

### Testing Database Connection
```bash
python database.py
```

## ☁️ Cloud Deployment

### 1. GitHub Actions Setup (Automated Scraping)

1. **Add Secrets to Repository**:
   - Go to your GitHub repository
   - Settings → Secrets and variables → Actions
   - Add secret: `MONGO_URI` with your MongoDB connection string

2. **Enable Actions**:
   - The workflow is already configured in `.github/workflows/daily_scraper.yml`
   - It runs daily at 8:00 AM UTC
   - You can also trigger it manually from the Actions tab

### 2. Streamlit Cloud Deployment (Dashboard)

1. **Deploy to Streamlit Cloud**:
   - Go to [Streamlit Cloud](https://share.streamlit.io/)
   - Connect your GitHub repository
   - Set the main file path: `dashboard.py`

2. **Add Secrets in Streamlit Cloud**:
   - In your Streamlit Cloud app settings
   - Add `MONGO_URI` in the secrets section:
   ```toml
   MONGO_URI = "your_mongodb_connection_string"
   ```

### 3. Alternative Deployment Options

**Railway (for scraper):**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway add
railway deploy
```

**Render (for dashboard):**
- Connect your GitHub repository
- Choose "Web Service"
- Build command: `pip install -r requirements.txt`
- Start command: `streamlit run dashboard.py --server.port $PORT`

## 📊 Dashboard Features

- **📰 Latest Articles**: View recent AI news with smart categorization
- **🔍 Filtering**: Filter by AI tool type (LLM, Computer Vision, Robotics, etc.)
- **📈 Statistics**: View article counts and distribution charts
- **🔄 Live Updates**: Data refreshes automatically every 5 minutes
- **▶️ Manual Scraping**: Run the scraper directly from the dashboard

## 🎯 AI Tool Categories

The system automatically classifies articles into these categories:

- **LLM**: Large Language Models (GPT, Claude, Gemini, etc.)
- **Computer Vision**: Image recognition, object detection, visual AI
- **Robotics**: Autonomous systems, drones, self-driving cars
- **Machine Learning**: Neural networks, TensorFlow, PyTorch
- **AI Tools**: Midjourney, DALL-E, Copilot, AI assistants
- **General AI**: Artificial intelligence research and breakthroughs

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `MONGO_URI` | MongoDB Atlas connection string | Yes |
| `SCRAPER_MAX_ARTICLES` | Maximum articles to scrape per run | No (default: 10) |
| `SCRAPER_SLEEP_INTERVAL` | Sleep time between requests (seconds) | No (default: 2) |

### Trusted News Sources

The scraper focuses on these trusted AI news sources:
- TechCrunch
- VentureBeat  
- The Verge
- Ars Technica
- Wired

## 📅 Data Schema

Each article is stored with the following structure:
```json
{
  "title": "OpenAI Launches GPT-5",
  "url": "https://example.com/openai-gpt5", 
  "type_of_ai_tool": "LLM",
  "scraped_at": "2025-01-06T08:00:00Z"
}
```

## 🔐 Security

- Environment variables for sensitive data
- MongoDB Atlas with proper authentication
- GitHub Secrets for CI/CD
- Rate limiting and respectful scraping

## 🚦 Monitoring

- Check GitHub Actions logs for scraper status
- Monitor Streamlit Cloud dashboard for uptime
- MongoDB Atlas provides database monitoring
- Dashboard shows latest scrape timestamps

## 🔄 Daily Workflow

1. **8:00 AM UTC**: GitHub Actions triggers the scraper
2. **Scraper**: Searches Google for recent AI news (up to 10 articles)
3. **Processing**: Extracts titles, URLs, and classifies AI tool types
4. **Storage**: Saves to MongoDB Atlas with deduplication
5. **Dashboard**: Automatically displays new articles

## 🚀 Future Enhancements

- **Email/Telegram Notifications**: Get notified of top daily stories
- **Sentiment Analysis**: Analyze headline sentiment
- **Twitter Integration**: Scrape trending AI topics from X/Twitter
- **Advanced Filtering**: Date ranges, keyword search
- **Export Features**: CSV/JSON export of articles
- **Analytics**: Trending topics and source analysis

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

If you encounter any issues:

1. Check the [Issues](https://github.com/your-username/ai-news-collector/issues) page
2. Verify your MongoDB Atlas connection
3. Check GitHub Actions logs for scraper issues
4. Ensure all environment variables are set correctly

---

**Created by**: Ziv Talyas  
**Date**: January 2025  
**Version**: 1.0.0