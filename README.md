# String Analyzer API

A RESTful API that analyzes strings and stores their computed properties.  
Built with **Python (FastAPI)** and **SQLite** for Backend Wizards Stage 1.

## 🚀 Features

- Analyze a string and compute:
  - Length
  - Palindrome check
  - Unique character count
  - Word count
  - SHA256 hash
  - Character frequency map
- Retrieve one or all strings
- Filter strings by properties
- Natural language filtering
- Delete a string

## 🧰 Tech Stack
- FastAPI
- SQLite
- SQLAlchemy
- Uvicorn

## ⚙️ Setup Instructions

```bash
# 1. Clone the repo
git clone https://github.com/IniPrec/String-Analyzer-Service.git
cd String Analyzer REST API

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # (Windows: venv\Scripts\activate)

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
uvicorn main:app --reload
