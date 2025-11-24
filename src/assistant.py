import os
import torch
from transformers import pipeline

class TradingAdvisor:
    def __init__(self, model_name="distilgpt2"):
        self.device = 0 if torch.cuda.is_available() else -1
        print(f"Loading Trading Advisor model {model_name} on device {'GPU' if self.device == 0 else 'CPU'}...")
        self.generator = pipeline("text-generation", model=model_name, device=self.device)

    def analyze_scenario(self, market_scenario, max_length=100):
        # Prompt engineering to force a trading perspective
        prompt = f"Market Scenario: {market_scenario}\nAnalysis and Recommendation (BUY/SELL/HOLD):"
        try:
            response = self.generator(prompt, max_length=max_length, num_return_sequences=1)
            return response[0]['generated_text']
        except Exception as e:
            return f"Error generating analysis: {str(e)}"

if __name__ == "__main__":
    advisor = TradingAdvisor()
    print(advisor.analyze_scenario("Apple just released a revolutionary new product."))
