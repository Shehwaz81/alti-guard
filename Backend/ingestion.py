import os
from typing import Annotated
from fastapi import FastAPI, Header, HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel
from supabase import create_client, Client

load_dotenv()
# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase URL and Key must be set in .env file")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY) # I must change this later to include type checking for deployment

# define the shape of data
class LogRequest(BaseModel):
    input: str
    output: str

app = FastAPI()

@app.post('/api/v1/log')
def log_data(
    payload : LogRequest,
    authorization: Annotated[str, Header(alias="Authorization")]
):
    # verify that this is acutally an api_key (valid auth)
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401)
    
    api_key = authorization.split(" ")[1] # removes "Bearer " from the header

    # make dict with everything needed so we can insert into sql table
    sql_data = {
        "api_key": api_key,
        "input": payload.input,
        "output": payload.output
    }
    response = supabase.table("AltiLogger").insert(sql_data).execute()
    
    if response.data:
        return {
            "message": "Data successfully sent to Supabase!",
            "data": response.data[0]
        }
    else:
        return {
            "message": "Warning: No data returned from Supabase insert", 
        } 
    