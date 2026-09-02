
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel
from dotenv import load_dotenv

from google import genai

from backend.database import create_users_table, get_connection

from pwdlib import PasswordHash

import os
import requests


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="AgriGuardian AI Agent",
    description="AI-powered farming assistant",
    version="1.0.0"
)


# ============================================================
# FRONTEND
# ============================================================

app.mount(
    "/frontend",
    StaticFiles(directory="frontend"),
    name="frontend"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ============================================================
# DATABASE
# ============================================================

create_users_table()


# ============================================================
# PASSWORD HASHING
# ============================================================

password_hash = PasswordHash.recommended()


# ============================================================
# GEMINI
# ============================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# REQUEST MODELS
# ============================================================

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


# ============================================================
# NEW SMART MARKET REQUEST
# ============================================================

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


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "message": "AgriGuardian AI Agent is running!"
    }


# ============================================================
# FRONTEND ROUTES
# ============================================================

@app.get("/index.html")
def index_page():

    return {
        "message": "AgriGuardian frontend is available at /frontend/index.html"
    }


@app.get("/login.html")
def login_page():

    return {
        "message": "AgriGuardian login page is available at /frontend/login.html"
    }


@app.get("/signup.html")
def signup_page():

    return {
        "message": "AgriGuardian signup page is available at /frontend/signup.html"
    }


@app.get("/dashboard.html")
def dashboard_page():

    return {
        "message": "AgriGuardian dashboard is available at /frontend/dashboard.html"
    }


# ============================================================
# AI ASSISTANT
# ============================================================

@app.post("/ask")
def ask_ai(data: Question):

    try:

        prompt = f"""
You are AgriGuardian AI, an agricultural assistant for farmers.

Answer the farmer's question clearly and practically.

Question:
{data.question}

Language:
{data.language}

Give simple farming advice.

Do not claim certainty when expert inspection is needed.
Do not recommend dangerous pesticide use without proper label
instructions and local agricultural expert guidance.
"""

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


# ============================================================
# SIGNUP
# ============================================================

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
            detail="Email already registered"
        )

    hashed_password = password_hash.hash(
        data.password
    )

    connection.execute(
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

    connection.close()

    return {
        "success": True,
        "message": "Signup successful"
    }


# ============================================================
# LOGIN
# ============================================================

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
            detail="Invalid email or password"
        )

    if not password_hash.verify(
        data.password,
        user["password"]
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    return {

        "success": True,

        "message": "Login successful",

        "user": {

            "id": user["id"],

            "name": user["name"],

            "email": user["email"]

        }

    }


# ============================================================
# WEATHER
# ============================================================

@app.get("/weather")
def weather(city: str):

    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:

        raise HTTPException(
            status_code=500,
            detail="OpenWeather API key not configured"
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

        if response.status_code != 200:

            return {
                "success": False,
                "error": response.json()
            }

        data = response.json()

        return {

            "success": True,

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
            detail=f"Weather API error: {str(e)}"
        )


# ============================================================
# CROP RECOMMENDATION
# ============================================================

@app.post("/crop-recommendation")
def crop_recommendation(
    data: CropRecommendationRequest
):

    try:

        prompt = f"""
You are AgriGuardian AI.

Recommend suitable crops for a farmer.

Location:
{data.location}

Soil type:
{data.soil_type}

Season:
{data.season}

Water availability:
{data.water_availability}

Provide:

1. Top 3 suitable crops
2. Why each crop is suitable
3. Basic farming advice
4. Important precautions
5. Best overall crop
6. General advice

Keep the answer practical and easy for a farmer to understand.
"""

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


# ============================================================
# PEST & DISEASE
# ============================================================

@app.post("/pest-disease")
def pest_disease(
    data: PestDiseaseRequest
):

    try:

        prompt = f"""
You are AgriGuardian AI, an agricultural assistant.

Analyze the following crop problem.

Crop:
{data.crop}

Location:
{data.location}

Symptoms:
{data.symptoms}

Language:
{data.language}

Provide:

1. Possible pest or disease
2. Why it may be occurring
3. Common signs
4. Immediate steps
5. Prevention
6. When to contact an agricultural expert

Diagnosis is not certain without proper inspection.

Do not recommend dangerous pesticide use without
proper product-label instructions and local expert guidance.
"""

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


# ============================================================
# IRRIGATION
# ============================================================

@app.post("/irrigation")
def irrigation(
    data: IrrigationRequest
):

    try:

        prompt = f"""
You are AgriGuardian AI.

Give practical irrigation guidance.

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

Explain:

1. Suggested irrigation frequency
2. Suitable timing
3. Signs of overwatering
4. Signs of underwatering
5. Water-saving methods
6. Important precautions

Avoid false precision. Mention that actual irrigation
depends on rainfall, soil moisture, crop condition,
temperature and local conditions.
"""

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


# ============================================================
# MARKET PRICE COMPARISON
# ============================================================

@app.post("/market-prices")
def market_prices(
    data: MarketPriceRequest
):

    if data.quantity <= 0:

        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero"
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
                detail="Market prices cannot be negative"
            )

        item["gross_revenue"] = (
            item["price"] * data.quantity
        )

    prices.sort(
        key=lambda x: x["price"],
        reverse=True
    )

    try:

        prompt = f"""
You are AgriGuardian AI.

Analyze these market prices.

Crop:
{data.crop}

Location:
{data.location}

Quantity:
{data.quantity}

Market data:
{prices}

Explain:

1. Which market has the highest listed price
2. Gross revenue at each market
3. Why the highest price does not always mean highest profit
4. Transport costs
5. Commission
6. Loading/unloading costs
7. Other selling costs

The farmer should consider net return rather than price alone.

Language:
{data.language}
"""

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        return {

            "success": True,

            "crop": data.crop,

            "location": data.location,

            "quantity": data.quantity,

            "markets": prices,

            "analysis": response.text

        }

    except Exception as e:

        return {

            "success": False,

            "error": str(e)

        }


# ============================================================
# NET RETURN CALCULATOR
# ============================================================

@app.post("/net-return")
def net_return(
    data: NetReturnRequest
):

    if data.quantity <= 0:

        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero"
        )

    if data.price_per_unit < 0:

        raise HTTPException(
            status_code=400,
            detail="Price cannot be negative"
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
            detail="Costs cannot be negative"
        )

    gross_revenue = (
        data.quantity *
        data.price_per_unit
    )

    total_costs = sum(costs)

    net_return = (
        gross_revenue -
        total_costs
    )

    if gross_revenue > 0:

        net_return_percentage = (
            net_return /
            gross_revenue
        ) * 100

    else:

        net_return_percentage = 0

    return {

        "success": True,

        "crop": data.crop,

        "quantity": data.quantity,

        "price_per_unit": data.price_per_unit,

        "gross_revenue": round(
            gross_revenue,
            2
        ),

        "transport_cost": round(
            data.transport_cost,
            2
        ),

        "commission": round(
            data.commission,
            2
        ),

        "loading_cost": round(
            data.loading_cost,
            2
        ),

        "other_costs": round(
            data.other_costs,
            2
        ),

        "total_costs": round(
            total_costs,
            2
        ),

        "net_return": round(
            net_return,
            2
        ),

        "net_return_percentage": round(
            net_return_percentage,
            2
        )

    }


# ============================================================
# SMART MARKET RECOMMENDATION
# ============================================================

@app.post("/smart-market-recommendation")
def smart_market_recommendation(
    data: SmartMarketRecommendationRequest
):

    # --------------------------------------------------------
    # BASIC VALIDATION
    # --------------------------------------------------------

    if data.quantity <= 0:

        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero"
        )


    # --------------------------------------------------------
    # MARKET DATA
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # CALCULATE EACH MARKET
    # --------------------------------------------------------

    for market in markets:

        if market["price"] < 0:

            raise HTTPException(
                status_code=400,
                detail="Price cannot be negative"
            )

        costs = [

            market["transport"],

            market["commission"],

            market["loading"],

            market["other"]

        ]

        if any(cost < 0 for cost in costs):

            raise HTTPException(
                status_code=400,
                detail="Costs cannot be negative"
            )

        gross_revenue = (
            data.quantity *
            market["price"]
        )

        total_costs = sum(costs)

        net_return = (
            gross_revenue -
            total_costs
        )

        market["gross_revenue"] = round(
            gross_revenue,
            2
        )

        market["total_costs"] = round(
            total_costs,
            2
        )

        market["net_return"] = round(
            net_return,
            2
        )


    # --------------------------------------------------------
    # FIND BEST MARKET
    # --------------------------------------------------------

    best_market = max(
        markets,
        key=lambda x: x["net_return"]
    )


    # --------------------------------------------------------
    # FIND HIGHEST PRICE MARKET
    # --------------------------------------------------------

    highest_price_market = max(
        markets,
        key=lambda x: x["price"]
    )


    # --------------------------------------------------------
    # GEMINI EXPLANATION
    # --------------------------------------------------------

    try:

        prompt = f"""
You are AgriGuardian AI.

Help a farmer choose the best market based on expected net return.

Crop:
{data.crop}

Quantity:
{data.quantity}

Market calculations:
{markets}

Best market according to calculated net return:
{best_market["market"]}

Highest price market:
{highest_price_market["market"]}

Explain clearly:

1. Recommended market
2. Expected net return
3. Why this market is recommended
4. Difference between highest price and highest net return
5. Main costs affecting the result
6. Practical advice for the farmer

Important:
The recommendation is based only on the costs and prices
provided by the user. Actual market conditions may change.

Do not claim that this is a guaranteed profit.
"""

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        analysis = response.text

    except Exception as e:

        analysis = (
            "Market recommendation was calculated successfully, "
            "but AI explanation was unavailable."
        )


    # --------------------------------------------------------
    # RETURN RESULT
    # --------------------------------------------------------

    return {

        "success": True,

        "crop": data.crop,

        "quantity": data.quantity,

        "markets": markets,

        "recommended_market":
            best_market["market"],

        "recommended_net_return":
            best_market["net_return"],

        "highest_price_market":
            highest_price_market["market"],

        "highest_price":
            highest_price_market["price"],

        "analysis":
            analysis

    }