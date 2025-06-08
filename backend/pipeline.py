from cgitb import reset
import os
from openai import OpenAI
from .prompts import EXTRACT_KPI_PROMPT, CLASSIFY_QUESTION_PROMPT, FALLBACK_PROMPT
from .assistant import DataAnalysisAssistant
from .execute_llm import process_query
from dotenv import load_dotenv

load_dotenv()

def call_openai_api(system_prompt, user_prompt, model="gpt-4o", max_tokens=500, temperature=0):
    """
    Call OpenAI API with system and user prompts
    
    Args:
        system_prompt (str): The system message to set AI behavior
        user_prompt (str): The user's question or request
        model (str): OpenAI model to use (default: "gpt-4")
        max_tokens (int): Maximum tokens in response (default: 500)
        temperature (float): Response creativity 0.0-2.0 (default: 0.7)
    
    Returns:
        str: AI response content or error message
    """
    try:
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return f"Error: {e}"



class BusinessAssistant:
    """
    Initialize the BusinessAssistant class
    """
    def __init__(self):
        pass

    def fallback(self, question):
        """
        Fallback response when the question is not related to business, finance, transactions, payments, or data analysis
        """
        return call_openai_api(FALLBACK_PROMPT, question)

    def classify_question(self, question):
        """
        Classify the question into causal or insight
        """
        return call_openai_api(CLASSIFY_QUESTION_PROMPT, question)
    
    def kpi_extraction(self, question):
        """
        Extract KPI from the business question
        """
        return call_openai_api(EXTRACT_KPI_PROMPT, question)


    def run_insight(self, question):
        """Example of how to use the assistant for specific questions"""
        analyzer = DataAnalysisAssistant()
        
        # Setup
        analyzer.create_assistant()
        analyzer.create_thread()
        analyzer.upload_file("data/data_cleaned.csv")
        
        # Ask multiple questions
        
        
        print(f"\n📊 Question : {question}")
        response = analyzer.ask_question_with_detailed_steps(question)
        print("-" * 80)
        
        analyzer.cleanup()

        return response

    def query(self, question):
        """
        Query the business assistant
        """
        classification = self.classify_question(question)

        if classification == "causal":
            pass
        elif classification == "insight":
            # return self.run_insight(question)
            response = process_query(question)
            return response['english_response']
        else:
            return self.fallback(question)

            