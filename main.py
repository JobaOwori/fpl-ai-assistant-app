from fastapi import FastAPI
from pydantic import BaseModel
import os
from langchain.agents import initialize_agent, AgentType
from langchain_community.tools import Tool
from langchain_community.llms import OpenAI
import requests

app = FastAPI()

# Set OpenAI API key (Use an environment variable in production)
os.environ["OPENAI_API_KEY"] = "your_openai_api_key"

# FPL Data Fetcher Tool
def get_fpl_top_scorers():
    response = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/")
    data = response.json()
    players = sorted(data["elements"], key=lambda x: x["total_points"], reverse=True)[:5]
    return ", ".join([player["web_name"] for player in players])

fpl_tool = Tool(
    name="FPL Top Scorers",
    func=get_fpl_top_scorers,
    description="Fetches top FPL scorers"
)

# Initialize AI Agent with OpenAI Functions
llm = OpenAI(model_name="gpt-3.5-turbo")
agent = initialize_agent(
    tools=[fpl_tool],
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True
)

# Define API Model
class UserQuery(BaseModel):
    query: str

@app.post("/ask")
def ask_fpl_agent(user_query: UserQuery):
    response = agent.run(user_query.query)
    return {"response": response}

@app.get("/")
def root():
    return {"message": "FPL AI Agent is Running!"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Default to 8000
    uvicorn.run(app, host="0.0.0.0", port=port)
