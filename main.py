from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from google import genai
from database import create_users_table, get_connection

from pwdlib import PasswordHash

import os
import requests


# =========================
# LOAD ENVIRONMENT VARIABLES
# =========================

load_dotenv()


# =========================
# FASTAPI APP
# =========================

app = FastAPI(
    title="AgriGuardian AI Agent",
    description="AI-powered agriculture assistant for farmers",
    version="1.0.0"
)


# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# =========================
# DATABASE
# =========================

create_users_table()


# =========================
# PASSWORD HASHING
# =========================

password_hash = PasswordHash.recommended()


# =========================
# GEMINI
# =========================

gemini_api_key = os.getenv("GEMINI_API_KEY")

if gemini_api_key:
    client = genai.Client(api_key=gemini_api_key)
else:
    client = None


# =========================
# REQUEST MODELS
# =========================

class Question(BaseModel):
    question: str
    language: str = "en"


class SignupRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class CropRecommendationRequest(BaseModel):
    location: str
    soil_type: str
    season: str
    water_availability: str


class PestDiseaseRequest(BaseModel):
    crop: str
    symptoms: str
    location: str
    language: str = "en"


class IrrigationRequest(BaseModel):
    crop: str
    location: str
    soil_type: str
    growth_stage: str
    water_availability: str
    language: str = "en"


class MarketPriceRequest(BaseModel):
    crop: str
    location: str
    market1: str
    price1: float
    market2: str
    price2: float
    market3: str
    price3: float
    quantity: float = 100
    language: str = "en"


class NetReturnRequest(BaseModel):
    crop: str
    quantity: float
    price_per_unit: float
    transport_cost: float
    commission: float
    loading_cost: float
    other_costs: float = 0


class SmartMarketRecommendationRequest(BaseModel):
    crop: str
    quantity: float

    market1: str
    price1: float
    transport1: float
    commission1: float
    loading1: float
    other1: float = 0

    market2: str
    price2: float
    transport2: float
    commission2: float
    loading2: float
    other2: float = 0

    market3: str
    price3: float
    transport3: float
    commission3: float
    loading3: float
    other3: float = 0


# =========================
# FRONTEND PAGES
# =========================

@app.get("/")
def home():
    return FileResponse("index.html")


@app.get("/index.html")
def index_page():
    return FileResponse("index.html")


@app.get("/login.html")
def login_page():
    return FileResponse("login.html")


@app.get("/signup.html")
def signup_page():
    return FileResponse("signup.html")


@app.get("/dashboard.html")
def dashboard_page():
    return FileResponse("dashboard.html")


@app.get("/script.js")
def script_file():
    return FileResponse("script.js")


# =========================
# AI ASSISTANT
# =========================

@app.post("/ask")
def ask_ai(data: Question):

    if client is None:
        raise HTTPException(
            status_code=500,
            detail="Gemini API key is not configured."
        )

    prompt = f"""
You are AgriGuardian AI, an agriculture assistant.

Help farmers with practical and simple farming advice.

User question:
{data.question}

Language:
{data.language}

Give a clear, useful answer.

Avoid dangerous pesticide or chemical recommendations.
For serious crop disease or chemical decisions,
advise consulting a local agricultural expert.
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        return {
            "success": True,
            "answer": response.text
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


# =========================
# SIGNUP
# =========================

@app.post("/signup")
def signup(data: SignupRequest):

    connection = get_connection()

    existing_user = connection.execute(
        "SELECT id FROM users WHERE email = ?",
        (data.email,)
    ).fetchone()

    if existing_user:

        connection.close()

        raise HTTPException(
            status_code=400,
            detail="Email already registered."
        )

    hashed_password = password_hash.hash(data.password)

    cursor = connection.execute(
        """
        INSERT INTO users (name, email, password)
        VALUES (?, ?, ?)
        """,
        (
            data.name,
            data.email,
            hashed_password
        )
    )

    connection.commit()

    user_id = cursor.lastrowid

    connection.close()

    return {
        "success": True,
        "message": "Account created successfully.",
        "user_id": user_id
    }


# =========================
# LOGIN
# =========================

@app.post("/login")
def login(data: LoginRequest):

    connection = get_connection()

    user = connection.execute(
        """
        SELECT id, name, email, password
        FROM users
        WHERE email = ?
        """,
        (data.email,)
    ).fetchone()

    connection.close()

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    if not password_hash.verify(
        data.password,
        user["password"]
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    return {
        "success": True,
        "message": "Login successful.",
        "user_id": user["id"],
        "name": user["name"],
        "email": user["email"]
    }


# =========================
# WEATHER
# =========================

@app.get("/weather")
def weather(city: str):

    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:

        raise HTTPException(
            status_code=500,
            detail="OpenWeather API key is not configured."
        )

    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        data = response.json()

        if response.status_code != 200:

            raise HTTPException(
                status_code=response.status_code,
                detail=data.get(
                    "message",
                    "Unable to get weather."
                )
            )

        return {
            "city": data["name"],
            "country": data["sys"]["country"],
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "description": data["weather"][0]["description"]
        }

    except requests.RequestException as e:

        raise HTTPException(
            status_code=500,
            detail=f"Weather service error: {str(e)}"
        )


# =========================
# CROP RECOMMENDATION
# =========================

@app.post("/crop-recommendation")
def crop_recommendation(
    data: CropRecommendationRequest
):

    if client is None:

        raise HTTPException(
            status_code=500,
            detail="Gemini API key is not configured."
        )

    prompt = f"""
You are an agriculture expert helping a farmer.

Location:
{data.location}

Soil type:
{data.soil_type}

Season:
{data.season}

Water availability:
{data.water_availability}

Recommend the top 3 suitable crops.

For each crop explain:

1. Why it is suitable
2. Basic farming advice
3. Important precautions

Also provide:

- Best overall crop
- General advice for the farmer

Keep the answer simple and practical.
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        return {
            "success": True,
            "recommendation": response.text
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


# =========================
# PEST & DISEASE
# =========================

@app.post("/pest-disease")
def pest_disease(data: PestDiseaseRequest):

    if client is None:

        raise HTTPException(
            status_code=500,
            detail="Gemini API key is not configured."
        )

    prompt = f"""
You are an agriculture assistant.

Crop:
{data.crop}

Observed symptoms:
{data.symptoms}

Location:
{data.location}

Language:
{data.language}

Provide:

1. Possible pest or disease
2. Why it may match the symptoms
3. Common signs to check
4. Immediate safe steps
5. Prevention
6. When to contact an agricultural expert

Important:

Do not claim the diagnosis is certain.

Do not recommend dangerous pesticide use.

If chemical control is discussed,
advise following the product label
and local agricultural expert guidance.

Use simple language.
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        return {
            "success": True,
            "answer": response.text
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


# =========================
# IRRIGATION
# =========================

@app.post("/irrigation")
def irrigation(data: IrrigationRequest):

    if client is None:

        raise HTTPException(
            status_code=500,
            detail="Gemini API key is not configured."
        )

    prompt = f"""
You are an agriculture irrigation advisor.

Crop:
{data.crop}

Location:
{data.location}

Soil:
{data.soil_type}

Growth stage:
{data.growth_stage}

Water availability:
{data.water_availability}

Language:
{data.language}

Provide:

1. Recommended irrigation frequency
2. General amount and timing guidance
3. Best time of day to irrigate
4. Signs of overwatering
5. Signs of underwatering
6. Water-saving practices
7. Important precautions

Do not give false precision.

Consider weather, soil and crop stage.

Use simple practical language.
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        return {
            "success": True,
            "answer": response.text
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


# =========================
# MARKET PRICE COMPARISON
# =========================

@app.post("/market-prices")
def market_prices(data: MarketPriceRequest):

    if data.quantity <= 0:

        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero."
        )

    prices = [
        {
            "market": data.market1,
            "price": data.price1
        },
        {
            "market": data.market2,
            "price": data.price2
        },
        {
            "market": data.market3,
            "price": data.price3
        }
    ]

    for item in prices:

        if item["price"] < 0:

            raise HTTPException(
                status_code=400,
                detail="Market price cannot be negative."
            )

    prices.sort(
        key=lambda x: x["price"],
        reverse=True
    )

    highest_price = prices[0]

    gross_revenue = (
        highest_price["price"]
        * data.quantity
    )

    analysis = ""

    if client:

        prompt = f"""
Analyze these market prices for a farmer.

Crop:
{data.crop}

Location:
{data.location}

Quantity:
{data.quantity}

Markets:
{prices}

Explain:

1. Which market has the highest listed price
2. Expected gross revenue at that price
3. Important factors affecting actual profit
4. Why the highest price does not always mean the highest profit
5. Transport, commission, loading and unloading costs

Give practical advice.
"""

        try:

            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt
            )

            analysis = response.text

        except Exception:

            analysis = (
                "Highest listed price may not always result "
                "in the highest profit because transport "
                "and selling costs can differ."
            )

    return {
        "success": True,
        "crop": data.crop,
        "location": data.location,
        "quantity": data.quantity,
        "markets": prices,
        "analysis": analysis
    }


# =========================
# NET RETURN CALCULATOR
# =========================

@app.post("/net-return")
def net_return(data: NetReturnRequest):

    if data.quantity <= 0:

        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero."
        )

    if data.price_per_unit < 0:

        raise HTTPException(
            status_code=400,
            detail="Price cannot be negative."
        )

    costs = [
        data.transport_cost,
        data.commission,
        data.loading_cost,
        data.other_costs
    ]

    if any(cost < 0 for cost in costs):

        raise HTTPException(
            status_code=400,
            detail="Costs cannot be negative."
        )

    gross_revenue = (
        data.quantity
        * data.price_per_unit
    )

    total_costs = sum(costs)

    net_return = (
        gross_revenue
        - total_costs
    )

    if gross_revenue > 0:

        net_return_percentage = (
            net_return
            / gross_revenue
            * 100
        )

    else:

        net_return_percentage = 0

    return {
        "success": True,
        "crop": data.crop,
        "quantity": round(data.quantity, 2),
        "price_per_unit": round(
            data.price_per_unit, 2
        ),
        "gross_revenue": round(
            gross_revenue, 2
        ),
        "transport_cost": round(
            data.transport_cost, 2
        ),
        "commission": round(
            data.commission, 2
        ),
        "loading_cost": round(
            data.loading_cost, 2
        ),
        "other_costs": round(
            data.other_costs, 2
        ),
        "total_costs": round(
            total_costs, 2
        ),
        "net_return": round(
            net_return, 2
        ),
        "net_return_percentage": round(
            net_return_percentage, 2
        )
    }


# =========================
# SMART MARKET RECOMMENDATION
# =========================

@app.post("/smart-market-recommendation")
def smart_market_recommendation(
    data: SmartMarketRecommendationRequest
):

    if data.quantity <= 0:

        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero."
        )

    markets = [
        {
            "market": data.market1,
            "price": data.price1,
            "transport": data.transport1,
            "commission": data.commission1,
            "loading": data.loading1,
            "other": data.other1
        },
        {
            "market": data.market2,
            "price": data.price2,
            "transport": data.transport2,
            "commission": data.commission2,
            "loading": data.loading2,
            "other": data.other2
        },
        {
            "market": data.market3,
            "price": data.price3,
            "transport": data.transport3,
            "commission": data.commission3,
            "loading": data.loading3,
            "other": data.other3
        }
    ]

    for market in markets:

        if market["price"] < 0:

            raise HTTPException(
                status_code=400,
                detail="Price cannot be negative."
            )

        if any(
            market[cost] < 0
            for cost in [
                "transport",
                "commission",
                "loading",
                "other"
            ]
        ):

            raise HTTPException(
                status_code=400,
                detail="Costs cannot be negative."
            )

        market["gross_revenue"] = (
            data.quantity
            * market["price"]
        )

        market["total_costs"] = (
            market["transport"]
            + market["commission"]
            + market["loading"]
            + market["other"]
        )

        market["net_return"] = (
            market["gross_revenue"]
            - market["total_costs"]
        )

    best_market = max(
        markets,
        key=lambda x: x["net_return"]
    )

    highest_price_market = max(
        markets,
        key=lambda x: x["price"]
    )

    analysis = ""

    if client:

        prompt = f"""
You are an agriculture market advisor.

Crop:
{data.crop}

Quantity:
{data.quantity}

Market comparison:

{markets}

The market with the highest net return is:
{best_market["market"]}

The market with the highest price is:
{highest_price_market["market"]}

Explain:

1. Why the recommended market has the best net return
2. Its expected net return
3. Difference between highest price and highest profit
4. Main costs affecting the decision
5. Practical advice for the farmer

Use simple language.
"""

        try:

            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt
            )

            analysis = response.text

        except Exception:

            analysis = (
                f"{best_market['market']} is recommended "
                "because it provides the highest expected "
                "net return after considering selling costs."
            )

    else:

        analysis = (
            f"{best_market['market']} is recommended "
            "because it provides the highest expected "
            "net return after considering selling costs."
        )

    return {
        "success": True,
        "crop": data.crop,
        "quantity": data.quantity,
        "markets": markets,
        "recommended_market": best_market["market"],
        "recommended_net_return": round(
            best_market["net_return"],
            2
        ),
        "highest_price_market": highest_price_market["market"],
        "highest_price": round(
            highest_price_market["price"],
            2
        ),
        "analysis": analysis
    }
