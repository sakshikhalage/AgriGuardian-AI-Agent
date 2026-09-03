# 🌾 AgriGuardian AI Agent

AgriGuardian AI Agent is an AI-powered farming assistant designed to help farmers make better decisions about crops, weather, irrigation, pest and disease management, and agricultural markets.

The project combines **AI, weather data, market analysis, and simple farming tools** in one easy-to-use web application.

## 🚀 Features

* 🌦️ **Weather Information** — Get current weather conditions for a location.
* 🌱 **AI Crop Recommendation** — Get crop suggestions based on location, soil, season, and water availability.
* 🐛 **Pest & Disease Guidance** — Get AI-assisted information about possible crop pests and diseases.
* 💧 **Irrigation Guidance** — Get practical irrigation recommendations based on crop and growing conditions.
* 📊 **Market Price Comparison** — Compare prices from multiple markets.
* 💰 **Net Return Calculator** — Calculate expected revenue, costs, and net return.
* 🏪 **Smart Market Recommendation** — Recommend the market with the best expected net return rather than simply the highest selling price.
* 🤖 **AI Farming Assistant** — Ask farming-related questions using Gemini AI.
* 🔐 **User Authentication** — Signup and login using securely hashed passwords.
* 🌍 **Multiple Languages** — Supports language selection for AI responses.

## ⭐ Smart Market Recommendation

One of the main features of AgriGuardian is its **net-return-based market recommendation**.

The system considers:

**Gross Revenue − Total Selling Costs = Expected Net Return**

Selling costs can include:

* Transportation
* Commission
* Loading charges
* Other expenses

This means the market offering the **highest price is not always the most profitable market**.

## 🧠 AI

AgriGuardian uses **Google Gemini** to provide AI-generated farming guidance and recommendations.

AI responses are designed to provide practical information while encouraging farmers to consult qualified agricultural experts when professional diagnosis or treatment is required.

## 🛠️ Technology Stack

### Backend

* Python
* FastAPI
* SQLite
* Google Gemini API
* OpenWeather API
* Requests
* Argon2 password hashing

### Frontend

* HTML
* CSS
* JavaScript

### Additional Technologies

* LangChain
* ChromaDB
* Sentence Transformers
* PyMuPDF

The project contains preparation for a future RAG-based knowledge system, but RAG is currently not enabled in the main application.

## 📁 Project Structure

```text
AgriGuardian-AI-Agent/
│
├── main.py
├── database.py
├── rag.py
├── requirements.txt
├── .gitignore
├── README.md
│
├── index.html
├── login.html
├── signup.html
├── dashboard.html
└── script.js
```

## ▶️ Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/sakshikhalage/AgriGuardian-AI-Agent.git
```

### 2. Open the project

```bash
cd AgriGuardian-AI-Agent
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure environment variables

Create a `.env` file and add your own API keys:

```text
GEMINI_API_KEY=your_gemini_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
```

**Never commit your `.env` file or API keys to GitHub.**

### 7. Start the FastAPI server

```bash
uvicorn main:app --reload
```

The application will run locally at:

```text
http://127.0.0.1:8000
```

## 🔮 Future Improvements

* 📷 AI-based crop disease image detection
* 🌍 Improved Marathi and Hindi support
* 📈 Market price charts and analytics
* 🌦️ More detailed weather forecasts
* 👨‍🌾 Personalized farmer profiles
* 🎤 Voice-based farming assistant
* 📚 RAG-based agricultural knowledge system
* ☁️ Cloud deployment
* 📱 Mobile-friendly improvements

## ⚠️ Disclaimer

AgriGuardian AI provides AI-generated information for assistance and educational purposes. It should not replace advice from qualified agricultural officers, agronomists, veterinarians, or other relevant experts.

## 👩‍💻 Author

**Sakshi Khalage**

GitHub: https://github.com/sakshikhalage

---

⭐ If you find this project useful, consider giving the repository a star!

````

