from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
from backend.pipeline import BusinessAssistant
from openai import OpenAI
import pandas as pd
from dotenv import load_dotenv
import os
load_dotenv()


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Business Assistant API",
    description="API for running business queries through the data analysis pipeline",
    version="1.0.0"
)

# Initialize the BusinessAssistant
business_assistant = BusinessAssistant()

# Pydantic models for request/response
class QueryRequest(BaseModel):
    question: str
    merchant: str
    
class QueryResponse(BaseModel):
    question: str
    response: str
    success: bool
    error: Optional[str] = None


class CardsDataRequest(BaseModel):
    merchant: str

class CardsDataResponse(BaseModel):
    totalTransactions: float
    totalRefundAmount: float
    averageSettlementAmount: float
    successRate: float

class BusinessInsightsResponse(BaseModel):
    insights: str

class BusinessInsightsRequest(BaseModel):
    merchant: str

@app.post("/business-insights", response_model=BusinessInsightsResponse)
async def get_business_insights(request: BusinessInsightsRequest):
    # Initialize OpenAI client
    client = OpenAI()

    # Craft a prompt for analyzing sample 2 data
    data = pd.read_csv('data/data_cleaned.csv')
    merchant = request.merchant
    df = data[data['Merchant Display Name'] == merchant]
    sample2_summary = df[df['Date'] == '2025-05-01']
    analysis_prompt = f"""You are a business intelligence analyst specializing in payment systems and transaction analysis.

    Do not include any recommendations. JUST SIMPLE EDA ANALYSIS

    I have data from a subset of our payment transactions that shows unusual or potentially anomalous patterns. Here is a summary of the key metrics and their distributions:
    Make sure that you only do data analysis and do not make any assumptions. Keep the analysis as concise as possible. It should be on point. 

    {sample2_summary}

    Please provide a detailed business analysis that include a simple basic EDA on the values in each column. 


    Please structure your response in clear sections and avoid technical jargon, as this will be presented to senior business stakeholders.
    Do not include a seperate section for conclusion or summary or anything like that.
    """

    # Make the API call
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a business intelligence analyst providing insights on payment transaction patterns."},
            {"role": "user", "content": analysis_prompt}
        ],
        temperature=0.7,
        max_tokens=1000
    )
    response = str(response.choices[0].message.content)
    return BusinessInsightsResponse(insights=response)
    

@app.post("/get-cards-data", response_model=CardsDataResponse)
async def get_cards_data(request: CardsDataRequest):
    # Specify the merchant type (e.g., 'Merchant A')
    merchant_type = request.merchant
    
    import pandas as pd
    df = pd.read_csv('data/data_cleaned.csv')

    # Filter data for the given merchant type
    df_merchant = df[df['Merchant Display Name'] == merchant_type]

    # Insight 1: Total number of transactions
    total_transactions = df_merchant.shape[0]

    # Insight 2: Total refund amount
    total_refund_amount = abs(df_merchant['Refund Amount'].sum())

    # Insight 3: Average settlement amount per transaction
    average_settlement_amount = df_merchant['Settlement Amount'].mean()

    # Insight 4: Success rate (proportion of captured transactions)
    success_rate = (df_merchant['Transaction Status Name'] == 'CAPTURED').mean()

    # Assemble insights into a DataFrame for display
    insights = CardsDataResponse(
        totalTransactions=total_transactions,
        totalRefundAmount=total_refund_amount,
        averageSettlementAmount=average_settlement_amount,
        successRate=success_rate
    )

    return insights

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Business Assistant API is running", "status": "healthy"}

@app.post("/query", response_model=QueryResponse)
async def run_assistant_query(request: QueryRequest):
    """
    Run a business query through the assistant pipeline.
    
    Args:
        request: QueryRequest containing the question
        
    Returns:
        QueryResponse with the assistant response
    """
    # try:
    logger.info(f"Processing query: {request.question}")
    
    # Run the query through the assistant
    response = business_assistant.query(request.question, request.merchant)
    
    if response is None:
        raise HTTPException(status_code=500, detail="Assistant returned no response")
    
    logger.info("Query processed successfully")
    
    return QueryResponse(
        question=request.question,
        response=response,
        success=True
    )
    
    # except Exception as e:
    #     logger.error(f"Error processing query: {str(e)}")
    #     return QueryResponse(
    #         question=request.question,
    #         response="",
    #         success=False,
    #         error=str(e)
    #     )

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Endpoint not found", "status_code": 404}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Internal server error", "status_code": 500}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
