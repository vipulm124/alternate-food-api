import os
from typing import Annotated
from fastapi import Body, FastAPI, HTTPException, Query, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from middlewares import CustomAuthMiddleware
from fastapi import APIRouter, Depends, Request
from supabase_handler import login_magic_link

# Load environment variables from .env file
load_dotenv()

SUPABASE_URL = str(os.environ.get("SUPABASE_URL"))
SUPABASE_PUBLISHABLE_DEFAULT_KEY = str(os.environ.get("SUPABASE_PUBLISHABLE_DEFAULT_KEY"))


app = FastAPI(title="Nutrition Assistant API")
security = HTTPBearer()
origins = ['http://localhost:5173']


app.add_middleware(CustomAuthMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the structured output model
class FoodAnalysis(BaseModel):
    calories: str = Field(description="Estimated calories of the food item")
    notes: str = Field(description="Short notes about the health impact of the food item")
    healthier_alternatives: list[str] = Field(description="Suggested healthier alternatives for the food item")

# Set up the JSON output parser
parser = JsonOutputParser(pydantic_object=FoodAnalysis)

# Define the prompt template as requested
prompt = PromptTemplate(
    template="""You are a nutrition assistant. Please make sure that the input is a genuine cuisine. 
        If it is a genuine cuisine then return the response in the below format
        For the given item, provide:
        - estimated calories
        - short health notes
        - healthier alternatives 
        
        Item: {food}
        
        {format_instructions}. If it is not a cuisine, then return error in the same format, with an additional bool called is_error""",
    input_variables=["food"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

# Initialize the OpenAI model (gpt-4o-mini)
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Create the LangChain chain
chain = prompt | model | parser

@app.get("/analyze")
async def analyze_food(
    request: Request,
    food_item: str = Query(..., description="The food item to analyze"),
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Endpoint to analyze a food item and provide nutritional information.
    """
    try:
        # Invoke the chain with the food item
        print("Food item triggered.")
        result = chain.invoke({"food": food_item})
        print(f"Result: {result}")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/login")
async def login(email: str = Body(embed=True)):
    await login_magic_link(email=email)
    



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)


