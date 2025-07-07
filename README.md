# 🤖 AI News Collector

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Streamlit_Cloud-FF4B4B?style=for-the-badge)](https://ai-news-collector-dvxmuud3qoqmgohkecvqks.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)

> 🔥 **[Try it live!](https://ai-news-collector-dvxmuud3qoqmgohkecvqks.streamlit.app/)** - See today's AI news automatically updated daily

## 📸 Dashboard Preview

![AI News Collector Dashboard](media/web_demo.jpg)
*Modern AI news dashboard with today's headlines, smart filtering, and real-time updates*

### ✨ **What You'll Find in the Live Demo**
- 🔥 **Today's AI Headlines** - Fresh articles updated every morning
- 🏷️ **Smart Categories** - LLM, Computer Vision, Robotics, Machine Learning, AI Tools
- 📊 **Live Analytics** - Article counts, category breakdowns, and trends  
- 🎨 **Beautiful Design** - Modern, responsive interface with dark mode support
- 🔍 **Advanced Filtering** - Filter by date, category, or search terms
- ⚡ **Real-time Updates** - Auto-refresh every 5 minutes

---

A fully automated cloud-based system that collects, stores, and displays top AI news articles daily. The system features a clean, organized codebase with modular architecture, external CSS styling, and proper separation of concerns.

## 🌟 Features

- **Automated Daily Scraping**: Searches Google for latest AI news from trusted sources
- **Smart Classification**: Automatically categorizes articles by AI tool type (LLM, Computer Vision, Robotics, etc.)
- **Deduplication**: Prevents duplicate articles using URL-based indexing
- **Live Dashboard**: Beautiful Streamlit interface with external CSS styling
- **Modular Architecture**: Clean separation of concerns with organized folder structure
- **Cloud Deployment**: Ready for GitHub Actions, Streamlit Cloud, and PostgreSQL

## 🚀 **Live Demo & Deployment**

### 🌐 **Try the Live Dashboard**
**👉 [ai-news-collector-dvxmuud3qoqmgohkecvqks.streamlit.app](https://ai-news-collector-dvxmuud3qoqmgohkecvqks.streamlit.app/)** 

*Updates daily at 8:00 AM UTC with fresh AI news articles*

### 📋 **Deploy Your Own**
Want to create your own AI News Collector? **See the complete [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** for step-by-step instructions on deploying to:

- **Streamlit Community Cloud** (Recommended - Free & Easy)
- **Railway** (Modern platform with GitHub integration)
- **Render** (Great Heroku alternative)
- **Docker** (Any cloud platform)

Your dashboard will be automatically updated daily by GitHub Actions!

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Scraper Bot | Python + BeautifulSoup + googlesearch-python | Extract data from web articles |
| Scheduler | GitHub Actions | Run scraper daily automatically |
| Database | PostgreSQL | Reliable relational database |
| Dashboard | Streamlit + Custom CSS | Live visualization of news entries |

## 📁 Project Structure

```
ai-news-collector/
├── 📱 app/                    # Main application code
│   ├── __init__.py           # Package initialization
│   ├── dashboard.py          # Streamlit dashboard
│   ├── database.py           # PostgreSQL integration
│   └── scraper.py            # Google search scraper
│
├── 🎨 static/                 # Static assets
│   └── dashboard.css         # External CSS styling
│
├── ⚙️ config/                 # Configuration files
│   ├── .env                  # Environment variables
│   └── .streamlit/           # Streamlit configuration
│       └── config.toml
│
├── 🧪 tests/                  # Test files
│   └── test_setup.py         # System verification tests
│
├── 🛠️ scripts/               # Utility scripts
│   └── quick_start.py        # Interactive setup script
│
├── 🚀 .github/workflows/      # GitHub Actions
│   └── daily_scraper.yml     # Daily automation
│
├── 📄 requirements.txt        # Python dependencies
├── 📚 README.md              # This file
└── 🚫 .gitignore             # Git ignore rules
```

## 📦 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/ai-news-collector.git
cd ai-news-collector
```

### 2. Quick Setup (Recommended)
```bash
# Run the interactive setup script
python3 scripts/quick_start.py
```

### 3. Manual Setup
```bash
# Install dependencies
pip3 install -r requirements.txt

# Create and configure environment
mkdir -p config
echo 'DATABASE_URL=postgresql://username:password@host:port/database_name?sslmode=require' > config/.env
# Edit config/.env with your PostgreSQL connection string
```

## 🗄️ Database Setup (PostgreSQL)

### Free PostgreSQL Providers (Recommended)

1. **Neon** (Recommended - Best free tier): 
   - Go to [neon.tech](https://neon.tech)
   - Sign up and create a new project
   - Copy the connection string
   - Add to your `config/.env` file

2. **Supabase** (Great alternative):
   - Go to [supabase.com](https://supabase.com)
   - Create a new project
   - Go to Settings → Database
   - Copy the connection string
   - Add to your `config/.env` file

### Local PostgreSQL Setup (Optional)

```bash
# Install PostgreSQL (macOS)
brew install postgresql
brew services start postgresql

# Create database
createdb ai_news

# Connection string for local setup:
# DATABASE_URL=postgresql://postgres:password@localhost:5432/ai_news
```

### Environment Configuration

Create `config/.env` file:
```bash
# Replace with your actual PostgreSQL connection string
DATABASE_URL=postgresql://username:password@host:port/database_name?sslmode=require

# Examples:
# Neon: postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require
# Supabase: postgresql://postgres:password@db.xxx.supabase.co:5432/postgres
# Local: postgresql://postgres:password@localhost:5432/ai_news

# Optional scraper settings
SCRAPER_MAX_ARTICLES=10
SCRAPER_SLEEP_INTERVAL=2
```

## 🚀 Usage

### Running Components

```bash
# Test your setup
python3 tests/test_setup.py

# Run the scraper manually
python3 app/scraper.py

# Start the dashboard
python3 -m streamlit run app/dashboard.py
```

Access the dashboard at `http://localhost:8501`

### Project Commands

```bash
# Test system setup
python3 tests/test_setup.py

# Quick setup (interactive)
python3 scripts/quick_start.py

# Run individual components
python3 app/scraper.py          # Scrape news
python3 app/database.py         # Test database
python3 -m streamlit run app/dashboard.py  # Start dashboard
```

## ☁️ Cloud Deployment

### 1. GitHub Actions Setup (Automated Scraping)

1. **Add Secrets to Repository**:
   - Go to your GitHub repository
   - Settings → Secrets and variables → Actions
   - Add secret: `DATABASE_URL` with your PostgreSQL connection string

2. **Enable Actions**:
   - The workflow is already configured in `.github/workflows/daily_scraper.yml`
   - It runs daily at 8:00 AM UTC
   - You can also trigger it manually from the Actions tab

### 2. Streamlit Cloud Deployment (Dashboard)

1. **Deploy to Streamlit Cloud**:
   - Go to [Streamlit Cloud](https://share.streamlit.io/)
   - Connect your GitHub repository
   - Set the main file path: `app/dashboard.py`

2. **Add Secrets in Streamlit Cloud**:
   - In your Streamlit Cloud app settings
   - Add `DATABASE_URL` in the secrets section:
   ```toml
   DATABASE_URL = "postgresql://username:password@host:port/database_name?sslmode=require"
   ```

### 3. Alternative Deployment Options

**Railway (for scraper):**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up
```

### 🎯 **Why PostgreSQL?**
- **Better Cloud Compatibility**: No SSL/TLS issues with Streamlit Cloud
- **Reliable & Mature**: Industry-standard relational database
- **Great Free Tiers**: Neon and Supabase offer generous free plans
- **Better Performance**: Optimized for cloud deployment scenarios
- **SQL Familiarity**: Standard SQL queries and excellent tooling

## 🔧 Configuration

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string (required)
- `SCRAPER_MAX_ARTICLES`: Max articles per scrape session (default: 10)
- `SCRAPER_SLEEP_INTERVAL`: Sleep between requests in seconds (default: 2)

### Adding New AI Categories
Edit `app/scraper.py` to add new AI tool categories:
```python
self.ai_tool_keywords = {
    'Your Category': ['keyword1', 'keyword2', 'keyword3'],
    # ... existing categories
}
```

## 📊 Dashboard Features

- **Today's Headlines**: Featured section for articles from today
- **Smart Filtering**: Filter by date range, AI category, or custom terms
- **Live Analytics**: Real-time stats and category breakdown charts
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Auto-refresh**: Data updates every 5 minutes
- **Manual Actions**: Refresh data or collect fresh news on demand

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/) for the beautiful dashboard
- Powered by [PostgreSQL](https://postgresql.org) for reliable data storage
- News sources: TechCrunch, VentureBeat, The Verge, Ars Technica, Wired
- Deployed on [Streamlit Cloud](https://streamlit.io/cloud) and automated with GitHub Actions

---

⭐ **Star this repo** if you found it useful! 

🐛 **Found a bug?** Open an issue and I'll fix it ASAP.

💡 **Have a feature idea?** Submit a pull request or create an issue.
