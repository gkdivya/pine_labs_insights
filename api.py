from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
from backend.pipeline import BusinessAssistant

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
    time_period: str
    
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
    response = business_assistant.query(request.question, request.merchant, request.time_period)
    
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
