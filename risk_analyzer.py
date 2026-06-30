import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json

load_dotenv()

def get_llm():
    return ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.3-70b-versatile",
        temperature=0.1
    )

def analyze_visitor_risk(visitor_data: dict) -> dict:
    llm = get_llm()

    prompt = PromptTemplate.from_template("""
You are a security AI agent for a residential society called GateGenius.
Analyze the visitor information and provide a risk assessment.

Visitor Information:
- Name: {visitor_name}
- Phone: {phone}
- Organization: {organization}
- Purpose: {purpose}
- Number of Visitors: {number_of_visitors}
- Entry Hour (24hr): {entry_hour}
- Recent Visits in Last 7 Days: {recent_visits_count}

Risk Scoring Rules:
1. Entry between 10PM-6AM = +30 points (suspicious timing)
2. Recent visits > 3 in 7 days = +25 points (frequent unknown visitor)
3. Large group (5+ people) = +20 points
4. Unknown organization = +15 points
5. No purpose mentioned = +10 points
6. Known delivery org (Zomato/Swiggy/Amazon) = -10 points
7. First time visitor = +5 points

Risk Levels:
- 0-40: LOW
- 41-70: MEDIUM  
- 71-100: HIGH

You MUST respond ONLY with a valid JSON object, no other text:
{{
    "riskScore": <number between 0-100>,
    "riskLevel": "<LOW or MEDIUM or HIGH>",
    "reasons": ["<reason 1>", "<reason 2>", "<reason 3>"],
    "recommendation": "<Allow Entry / Verify Identity / Deny Entry>"
}}
""")

    chain = prompt | llm | StrOutputParser()

    result = chain.invoke({
        "visitor_name": visitor_data.get("visitor_name", "Unknown"),
        "phone": visitor_data.get("phone", ""),
        "organization": visitor_data.get("organization", "Not specified"),
        "purpose": visitor_data.get("purpose", "Not specified"),
        "number_of_visitors": visitor_data.get("number_of_visitors", 1),
        "entry_hour": visitor_data.get("entry_hour", 12),
        "recent_visits_count": visitor_data.get("recent_visits_count", 0)
    })

    # Clean response
    result = result.strip()
    if "```json" in result:
        result = result.split("```json")[1].split("```")[0].strip()
    elif "```" in result:
        result = result.split("```")[1].split("```")[0].strip()

    return json.loads(result)