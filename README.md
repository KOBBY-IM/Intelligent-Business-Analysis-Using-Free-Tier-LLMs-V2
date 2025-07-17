# Intelligent Business Analysis Using Free-Tier LLMs

A comprehensive framework for comparing free-tier Large Language Models (LLMs) in business intelligence applications, specifically for the retail and finance industries.

## 🎯 Project Overview

This system provides evidence-based guidance for organizations selecting optimal free LLMs through:
- **Systematic RAG-enabled performance evaluation**
- **Blind user assessment by external testers**
- **Automated technical performance monitoring**
- **Focus on Retail & Finance business contexts**

## 🏗️ System Architecture

- **4 Free-Tier LLMs**: Integration with Groq, Google Gemini, and OpenRouter
- **RAG Pipeline**: 70% context coverage from provided datasets
- **Blind Evaluation**: Anonymous testing by external evaluators
- **Cloud-First**: Designed for Streamlit Cloud deployment
- **Automated Monitoring**: 14 evaluations per 12-hour period over 4 days

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Git
- Streamlit Cloud account (for deployment)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Intelligent-Business-Analysis-Using-Free-Tier-LLMs-V2
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure secrets** (optional for initial testing)
   ```bash
   # Edit .streamlit/secrets.toml with your API keys
   # See the template for required configuration
   ```

4. **Run locally**
   ```bash
   streamlit run app.py
   ```

### Streamlit Cloud Deployment

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial project setup"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Configure secrets in the Streamlit Cloud dashboard
   - Deploy the application

## 📁 Project Structure

```
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .streamlit/
│   └── secrets.toml      # Configuration template
├── utils/                # Utility modules (future)
├── pages/                # Streamlit pages (future)
├── data/                 # Industry datasets (future)
└── README.md            # This file
```

## 🔧 Configuration

### Required Secrets (Streamlit Cloud)

Configure these in your Streamlit Cloud dashboard under "Secrets":

```toml
[api_keys]
groq_api_key = "your-groq-api-key"
google_gemini_api_key = "your-google-api-key"
openrouter_api_key = "your-openrouter-api-key"

[auth]
admin_password = "your-admin-password"
tester_access_token = "your-tester-token"
```

## 🛠️ Development Guidelines

### Cloud-First Development
- All development must consider Streamlit Cloud as the primary environment
- No local file system persistence
- Use `st.session_state` for temporary data
- Regular deployment testing on Streamlit Cloud

### Code Quality
- Modular, well-commented code
- Robust error handling for API calls
- Secure handling of API keys and user data
- Unit tests for critical components

## 📋 Development Roadmap

- [x] **Phase 1**: Project initialization and Streamlit Cloud setup
- [ ] **Phase 2**: LLM integration and API configuration
- [ ] **Phase 3**: RAG pipeline implementation
- [ ] **Phase 4**: Blind evaluation system
- [ ] **Phase 5**: Automated performance monitoring
- [ ] **Phase 6**: Analysis dashboard and reporting

## 🔒 Security & Privacy

- All API keys handled via Streamlit secrets
- User data (names, emails) collected with explicit consent
- One evaluation per email address to ensure data integrity
- Secure storage of evaluation data

## 📊 Performance Requirements

- **RAG Coverage**: 70% of LLM responses grounded in retrieved data
- **Evaluation Frequency**: 14 runs per 12-hour period over 4 days
- **Response Time**: <200ms for retrieval operations
- **Resource Efficiency**: Optimized for Streamlit Cloud free tier

## 🤝 Contributing

1. Follow the "Cloud-First Development Paradigm"
2. Test all changes on Streamlit Cloud before submitting
3. Maintain modular code structure
4. Document all new features and APIs

## 📄 License

This project is developed for academic research purposes as part of an MSC thesis on intelligent business analysis systems.

## 🆘 Support

For questions or issues:
1. Check the deployment status on Streamlit Cloud
2. Verify all secrets are properly configured
3. Review the logs for any API rate limit issues
4. Ensure all dependencies are compatible with Streamlit Cloud 