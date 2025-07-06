# 🤖 AI News Collector

A fully automated cloud-based system that collects, stores, and displays top AI news articles daily. The system features a clean, organized codebase with modular architecture, external CSS styling, and proper separation of concerns.

## 🌟 Features

- **Automated Daily Scraping**: Searches Google for latest AI news from trusted sources
- **Smart Classification**: Automatically categorizes articles by AI tool type (LLM, Computer Vision, Robotics, etc.)
- **Deduplication**: Prevents duplicate articles using URL-based indexing
- **Live Dashboard**: Beautiful Streamlit interface with external CSS styling
- **Modular Architecture**: Clean separation of concerns with organized folder structure
- **Cloud Deployment**: Ready for GitHub Actions, Streamlit Cloud, and MongoDB Atlas

## 🚀 **Quick Deploy for Public Access**

Want to share your AI News Collector with others? **See the complete [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** for step-by-step instructions on deploying to:

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
| Database | MongoDB Atlas | Cloud-hosted NoSQL database |
| Dashboard | Streamlit + Custom CSS | Live visualization of news entries |

## 📁 Project Structure

```
ai-news-collector/
├── 📱 app/                    # Main application code
│   ├── __init__.py           # Package initialization
│   ├── dashboard.py          # Streamlit dashboard
│   ├── database.py           # MongoDB integration
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
cp config/.env.example config/.env
# Edit config/.env with your MongoDB connection string
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
   - Copy the connection string and add to your `config/.env` file

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
   - Add secret: `MONGO_URI` with your MongoDB connection string

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
- Start command: `streamlit run app/dashboard.py --server.port $PORT`

## 📊 Dashboard Features

- **📰 Today's Headlines**: Prominently featured with special styling
- **🔥 Breaking News**: Real-time badges for recent articles
- **🔍 Advanced Filtering**: Filter by date range and AI tool type
- **📈 Analytics**: Visual charts and statistics
- **🎨 Beautiful Design**: External CSS with responsive layout
- **🔄 Live Updates**: Auto-refresh every 5 minutes
- **▶️ Manual Control**: Run scraper directly from dashboard

## 🎯 AI Tool Categories

The system automatically classifies articles into these categories:

- **LLM**: Large Language Models (GPT, Claude, Gemini, etc.)
- **Computer Vision**: Image recognition, object detection, visual AI
- **Robotics**: Autonomous systems, drones, self-driving cars
- **Machine Learning**: Neural networks, TensorFlow, PyTorch
- **AI Tools**: Midjourney, DALL-E, Copilot, AI assistants
- **General AI**: Artificial intelligence research and breakthroughs

## 🔧 Configuration

### Environment Variables (`config/.env`)

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

## 🎨 Code Organization

### Clean Architecture
- **Separation of Concerns**: Each module has a single responsibility
- **External Styling**: CSS separated from Python code
- **Modular Design**: Easy to extend and maintain
- **Proper Imports**: Clean import structure with path management

### Key Improvements
- **External CSS**: Moved all styling to `static/dashboard.css`
- **Folder Structure**: Organized code into logical directories
- **Configuration Management**: Centralized config in `config/` folder
- **Package Structure**: Proper Python package with `__init__.py`
- **Enhanced Testing**: Comprehensive test suite with structure validation

## 🔐 Security

- Environment variables for sensitive data
- MongoDB Atlas with proper authentication
- GitHub Secrets for CI/CD
- Rate limiting and respectful scraping
- Proper gitignore for sensitive files

## 🚦 Monitoring

- Check GitHub Actions logs for scraper status
- Monitor Streamlit Cloud dashboard for uptime
- MongoDB Atlas provides database monitoring
- Dashboard shows latest scrape timestamps
- Comprehensive test suite for system validation

## 🔄 Daily Workflow

1. **8:00 AM UTC**: GitHub Actions triggers the scraper
2. **Scraper**: Searches Google for recent AI news (up to 10 articles)
3. **Processing**: Extracts titles, URLs, and classifies AI tool types
4. **Storage**: Saves to MongoDB Atlas with deduplication
5. **Dashboard**: Automatically displays new articles with today's focus

## 🚀 Future Enhancements

- **Email/Telegram Notifications**: Get notified of top daily stories
- **Sentiment Analysis**: Analyze headline sentiment
- **Twitter Integration**: Scrape trending AI topics from X/Twitter
- **Advanced Filtering**: Keyword search and custom date ranges
- **Export Features**: CSV/JSON export of articles
- **Admin Panel**: Content management and configuration interface

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Follow the existing code structure and organization
4. Add tests for new features in `tests/`
5. Update documentation as needed
6. Commit changes: `git commit -am 'Add feature'`
7. Push to branch: `git push origin feature-name`
8. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

If you encounter any issues:

1. Run the test suite: `python3 tests/test_setup.py`
2. Check the [Issues](https://github.com/your-username/ai-news-collector/issues) page
3. Verify your MongoDB Atlas connection
4. Check GitHub Actions logs for scraper issues
5. Ensure all files are in the correct folders

### Common Issues

- **Import Errors**: Ensure you're running commands from the project root
- **Database Connection**: Check your `config/.env` file
- **Missing Files**: Run `python3 tests/test_setup.py` to verify structure
- **CSS Not Loading**: Ensure `static/dashboard.css` exists

---

**Created by**: Ziv Talyas  
**Date**: January 2025  
**Version**: 2.0.0 (Refactored & Organized)