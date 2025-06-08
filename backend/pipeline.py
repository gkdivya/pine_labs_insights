import os
from token import OP
from openai import OpenAI
from .prompts import EXTRACT_KPI_PROMPT, CLASSIFY_QUESTION_PROMPT, FALLBACK_PROMPT
from .assistant import DataAnalysisAssistant
from .execute_llm import process_query
from dotenv import load_dotenv
import networkx as nx
from dowhy import gcm
import pandas as pd
import numpy as np

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

    def query(self, question, merchant):
        """
        Query the business assistant
        """
        classification = self.classify_question(question)

        if classification == "causal":
            kpi = self.kpi_extraction(question)
            kpi = kpi.strip("\"")
            data = pd.read_csv('data/data_cleaned.csv')
            data = data[data['Merchant Display Name'] == merchant]
            df=data.copy()
            data.drop(columns='Convenience Fees Amount In (Paise)', inplace=True)
            data.drop(columns='Pine Payment Gateway Integration Mode Name', inplace=True)
            data.dropna(inplace=True)

            # Encode non-numeric columns except date
            categorical_columns = ['Payment Mode Name', 'Transaction Status Name', 'Acquirer Response Code', 'Acquirer Issuer Match', 'Payout Status']

            for col in categorical_columns:
                data[col] = pd.Categorical(data[col]).codes

            # Create a DAG using networkx
            G = nx.DiGraph()

            # Add nodes and edges based on the whiteboard diagram
            G.add_edges_from([
                ("Acquirer Issuer Match", "Refund Amount"),
                ("Payment Mode Name", "Refund Amount"),
                ("Transaction Status Name", "Refund Amount"),
                ("Acquirer Response Code", "Refund Amount"),
                ("Time To Complete", "Refund Amount"),
                # ("Pine Payment Gateway Integration Mode Name", "Refund Amount"),

                ("Refund Amount", "Settlement Amount"),

                ("Bank Commision", "Settlement Amount"),
                # ("Convenience Fees Amount In (Paise)", "settlement_amount"),
                ("Amount To Be Deducted In Addition To Bank Charges", "Settlement Amount"),
                ("Bank Service Tax", "Settlement Amount")
            ])

            causal_model = gcm.InvertibleStructuralCausalModel(G) 

            sample1 = data[data['Date'] != '2025-05-15']
            sample2 = data[data['Date'] == '2025-05-15']

            sample1.drop(columns='Date', inplace=True)
            sample2.drop(columns='Date', inplace=True)

            gcm.auto.assign_causal_mechanisms(causal_model, data)

            gcm.fit(causal_model, data)
            print(data)
            attribution_scores = gcm.distribution_change(causal_model,
                                                        sample1,
                                                        sample2,
                                                        kpi,
                                                        num_samples=2000,
                                                        difference_estimation_func=lambda x1, x2 : np.mean(x2) - np.mean(x1)
            )
            
            if "Refund Amount" in attribution_scores:
                attribution_scores.pop('Refund Amount')
            if "Settlement Amount" in attribution_scores:
                attribution_scores.pop('Settlement Amount')
            
            attribution_scores = {k: abs(float(v)) for k, v in attribution_scores.items()}   

            # Convert attribution scores to a more readable format
            formatted_scores = "\n".join([f"{k}: {float(v):.2f}" for k,v in attribution_scores.items()])

            # Craft a detailed prompt for GPT
            prompt = f"""You are a financial analyst and data scientist specializing in payment systems and transaction analysis. 
            I have attribution scores from a causal analysis of our payment system, showing how different factors contribute to changes in Refund Amount.

            The scores represent the causal impact of each variable on refund amounts, where the magnitude shows the strength of the impact

            Here are the attribution scores:
            {formatted_scores}

            Please provide a detailed business analysis that:
            1. Identifies the most significant factors affecting refunds. Only include the top 2 factors. 
            2. Explains what these relationships mean in business terms.
            3. Suggests actionable recommendations based on these findings
            4. Discusses potential implications for risk management and process optimization

            Focus on practical insights that would be valuable for:
            - Risk Management Teams
            - Payment Operations
            - Customer Service
            - Business Strategy

            Please structure your response in clear sections and use specific examples where possible.
            These insights have to be given to CEO of pine labs so make sure there is no technical jargon. Also, do not include any actual attribution numbers. 
            """

            # Make the API call
            client = OpenAI()
            response_ = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a financial analyst and payment systems expert providing business insights."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            response_ = str(response_.choices[0].message.content)
            return response_
            
        elif classification == "insight":
            # return self.run_insight(question)
            response = process_query(question,merchant)
            return response['english_response']
        else:
            return self.fallback(question)