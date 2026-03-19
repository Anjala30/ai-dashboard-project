from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from google import genai

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API client
client = genai.Client(api_key="YOUR_API_KEY")

# Load dataset
df = pd.read_csv("students.csv")


@app.post("/ask")
def ask(query: str):
    try:
        # ---- RULE BASED LOGIC ----
        if "Pune" in query:
            result = df[df["city"] == "Pune"]

        elif "above 80" in query:
            result = df[df["marks"] > 80]

        elif "top" in query:
            result = df.sort_values(by="marks", ascending=False).head(3)

        else:
            result = df

        # ---- OPTIONAL AI ----
        try:
            ai_response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"Convert this into SQL: {query}"
            )
            ai_text = ai_response.text
        except:
            ai_text = "AI unavailable (quota exceeded)"

        return {
            "query": query,
            "ai_generated_query": ai_text,
            "data": result.to_dict(orient="records")
        }

    except Exception as e:
        return {"error": str(e)}