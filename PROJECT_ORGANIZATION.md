# Project Organization Guide

## Overview

This document outlines the organized file structure of the Intelligent Business Analysis Using Free-Tier LLMs project.

## Directory Structure

```
Intelligent-Business-Analysis-Using-Free-Tier-LLMs-V2/
├── 📁 Core Application
│   ├── app.py                          # Main Streamlit application
│   ├── requirements.txt                 # Python dependencies
│   └── README.md                       # Project overview
│
├── 📁 Pages (Streamlit Pages)
│   ├── __init__.py
│   ├── analysis.py                     # Analysis dashboard
│   ├── blind_evaluation.py             # Human blind evaluation interface
│   ├── blind_evaluation_analysis.py    # Blind evaluation results analysis
│   ├── llm_health_check.py             # LLM connectivity testing
│   ├── provider_comparison.py          # Provider-level analysis
│   ├── rag_demo.py                     # RAG pipeline demonstration
│   ├── technical_metrics_analysis.py   # Technical performance analysis
│   └── technical_metrics_analysis_backup.py
│
├── 📁 Utils (Core Utilities)
│   ├── __init__.py
│   ├── auth.py                         # Authentication system
│   ├── chunking.py                     # Text chunking utilities
│   ├── data_loader.py                  # Data loading utilities
│   ├── data_store.py                   # Data storage management
│   ├── embedding.py                    # Embedding generation
│   ├── llm_clients.py                  # LLM API clients
│   ├── pregenerate_responses.py        # Response generation
│   ├── prompts.py                      # Prompt templates
│   ├── question_generator.py           # Question generation
│   ├── rag_pipeline.py                 # RAG pipeline orchestration
│   ├── registration.py                 # User registration
│   └── vector_db.py                    # Vector database operations
│
├── 📁 Analysis Scripts
│   ├── README.md                       # Analysis scripts documentation
│   ├── analyze_data.py                 # Comprehensive data analysis
│   ├── test_4_question_implementation.py # 4-question implementation testing
│   ├── question_reduction_impact_analysis.py # Question reduction analysis
│   ├── question_reduction_analysis.py  # General question reduction analysis
│   └── random_selection_analysis.py    # Random selection strategy analysis
│
├── 📁 Tests
│   ├── README.md                       # Testing documentation
│   ├── unit/                           # Unit tests
│   │   └── test_error_tracking.py      # Error tracking tests
│   └── integration/                    # Integration tests (to be added)
│
├── 📁 Documentation
│   ├── README.md                       # Documentation overview
│   ├── implementation/                 # Implementation documentation
│   │   ├── METHODOLOGY.md              # Academic thesis methodology
│   │   ├── 4_QUESTION_IMPLEMENTATION.md # 4-question implementation
│   │   ├── ERROR_TRACKING_ENHANCEMENTS.md # Error tracking system
│   │   ├── PROVIDER_ANALYSIS_ENHANCEMENTS.md # Provider analysis features
│   │   └── DATA_COLLECTION_SYSTEM.md   # Data collection architecture
│   ├── deployment/                     # Deployment documentation
│   │   ├── STREAMLIT_CLOUD_SETUP.md    # Streamlit Cloud setup
│   │   ├── STREAMLIT_CLOUD_DEPLOYMENT_CHECKLIST.md # Deployment checklist
│   │   ├── STREAMLIT_CLOUD_TROUBLESHOOTING.md # Troubleshooting guide
│   │   ├── DEPLOYMENT_READY_CHECKLIST.md # Pre-deployment checklist
│   │   └── SESSION_PERSISTENCE_IMPROVEMENTS.md # Session management
│   ├── analysis/                       # Analysis documentation
│   │   └── DATA_COLLECTION_REVIEW.md   # Data collection review
│   └── testing/                        # Testing documentation
│       ├── BATCH_TESTING_STATUS.md     # Batch testing status
│       ├── REGISTRATION_TESTING.md     # Registration testing
│       ├── local_test_checklist.md     # Local testing checklist
│       ├── HOW_TO_TEST_PHASE3.md       # Phase 3 testing guide
│       └── ISSUES_FIXED_SUMMARY.md     # Fixed issues summary
│
├── 📁 Automation
│   ├── batch_evaluator.py              # Automated batch evaluation
│   ├── dashboard.py                    # Monitoring dashboard
│   ├── local_scheduler.py              # Local task scheduling
│   ├── monitor.py                      # System monitoring
│   ├── real_world_simulator.py         # Real-world simulation
│   ├── run_real_world_sim.sh           # Simulation runner
│   ├── run_scheduler.sh                # Scheduler runner
│   ├── batch-evaluator.service         # System service
│   └── README.md                       # Automation documentation
│
├── 📁 Scripts
│   ├── README.md                       # Scripts documentation
│   ├── setup/                          # Setup scripts
│   │   ├── setup_gcs.py                # GCS setup
│   │   ├── setup_gcs.sh                # GCS setup shell script
│   │   └── configure_gcs.py            # GCS configuration
│   └── deployment/                     # Deployment scripts (to be added)
│
├── 📁 Data
│   ├── batch_eval_metrics.csv          # Batch evaluation metrics
│   ├── eval_questions.json             # Evaluation questions
│   └── evaluations.json                # Human evaluation data
│
├── 📁 Samples
│   ├── README.md                       # Sample data documentation
│   ├── create_sample_batch_data.py     # Sample batch data generator
│   ├── create_sample_blind_data.py     # Sample blind evaluation data
│   └── generate_sample_data.py         # General sample data generator
│
├── 📁 Debug
│   ├── README.md                       # Debug documentation
│   └── debug_session.py                # Debug session utilities
│
└── 📁 Configuration Files
    ├── .gitignore                      # Git ignore rules
    ├── .streamlit/                     # Streamlit configuration
    ├── .devcontainer/                  # Development container config
    ├── .github/                        # GitHub configuration
    ├── .cursor/                        # Cursor IDE configuration
    └── .pytest_cache/                  # Pytest cache
```

## File Categories

### **Core Application Files**
- **`app.py`**: Main Streamlit application entry point
- **`requirements.txt`**: Python package dependencies
- **`README.md`**: Project overview and setup instructions

### **Streamlit Pages**
- **Analysis Pages**: Data analysis and visualization interfaces
- **Evaluation Pages**: Human blind evaluation system
- **Demo Pages**: System demonstration and testing interfaces

### **Utility Modules**
- **Authentication**: User authentication and access control
- **Data Processing**: Data loading, storage, and manipulation
- **LLM Integration**: API clients and response handling
- **RAG Pipeline**: Retrieval-augmented generation system
- **Vector Database**: Embedding storage and retrieval

### **Analysis Scripts**
- **Data Analysis**: Comprehensive analysis of evaluation results
- **Question Analysis**: Analysis of question selection strategies
- **Implementation Testing**: Validation of system features

### **Testing**
- **Unit Tests**: Individual component testing
- **Integration Tests**: System integration testing
- **Error Tracking**: Error handling and classification testing

### **Documentation**
- **Implementation**: Core system implementation guides
- **Deployment**: Deployment and infrastructure guides
- **Analysis**: Research and analysis documentation
- **Testing**: Testing procedures and validation guides

### **Automation**
- **Batch Evaluation**: Automated LLM performance testing
- **Monitoring**: System monitoring and health checks
- **Scheduling**: Task scheduling and automation

### **Scripts**
- **Setup**: Infrastructure and environment setup
- **Deployment**: Deployment and maintenance automation
- **Configuration**: System configuration management

### **Data**
- **Evaluation Data**: Human evaluation results
- **Metrics Data**: Technical performance metrics
- **Question Data**: Evaluation question definitions

### **Samples**
- **Sample Data**: Test data generators
- **Example Data**: Sample datasets for testing

## Organization Benefits

### **Improved Navigation**
- Logical grouping of related files
- Clear separation of concerns
- Easy-to-follow directory structure

### **Better Maintenance**
- Organized documentation by category
- Separated testing and analysis scripts
- Clear distinction between core and utility files

### **Enhanced Development**
- Easy to locate specific functionality
- Clear module dependencies
- Simplified testing and debugging

### **Scalability**
- Easy to add new features
- Organized space for future components
- Clear patterns for new additions

## Usage Guidelines

### **Adding New Files**
1. **Core Features**: Add to appropriate `utils/` module
2. **New Pages**: Add to `pages/` directory
3. **Analysis Scripts**: Add to `analysis_scripts/`
4. **Tests**: Add to appropriate `tests/` subdirectory
5. **Documentation**: Add to appropriate `docs/` subdirectory

### **File Naming Conventions**
- **Python Files**: Use snake_case (e.g., `data_loader.py`)
- **Documentation**: Use UPPERCASE with underscores (e.g., `METHODOLOGY.md`)
- **Scripts**: Use descriptive names with clear purpose
- **Tests**: Prefix with `test_` (e.g., `test_error_tracking.py`)

### **Documentation Standards**
- Each directory has a `README.md` explaining its purpose
- Implementation details documented in `docs/implementation/`
- Deployment procedures documented in `docs/deployment/`
- Testing procedures documented in `docs/testing/`

This organization provides a clean, maintainable, and scalable structure for the LLM evaluation system. 