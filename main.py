import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from risk_analyzer import analyze_visitor_risk

app = FastAPI(title="GateGenius AI Service")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Model
class VisitorRiskRequest(BaseModel):
    visitor_name: str
    phone: str
    organization: str = ""
    purpose: str = ""
    number_of_visitors: int = 1
    entry_hour: int = 12
    recent_visits_count: int = 0

# Health Check
@app.get("/")
def health_check():
    return {"status": "GateGenius AI Service Running!"}

# Risk Analysis
@app.post("/ai/analyze-risk")
async def analyze_risk(request: VisitorRiskRequest):
    try:
        result = analyze_visitor_risk({
            "visitor_name": request.visitor_name,
            "phone": request.phone,
            "organization": request.organization,
            "purpose": request.purpose,
            "number_of_visitors": request.number_of_visitors,
            "entry_hour": request.entry_hour,
            "recent_visits_count": request.recent_visits_count
        })
        return result
    except Exception as e:
        return {
            "riskScore": 50,
            "riskLevel": "MEDIUM",
            "reasons": ["AI analysis failed - manual verification required"],
            "recommendation": "Verify Identity"
        }