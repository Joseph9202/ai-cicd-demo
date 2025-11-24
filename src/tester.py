import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class MarketSimulator:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-lite')

    def generate_scenario(self):
        prompt = "Generate a realistic financial market scenario (e.g., about a stock, crypto, or economic event). Output ONLY the scenario description in one sentence."
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error generating scenario: {e}")
            return "The Federal Reserve announces a 0.5% interest rate hike."

    def evaluate_advice(self, scenario, advice):
        prompt = f"""
        Scenario: {scenario}
        Advisor Analysis: {advice}
        
        Evaluate if the Advisor's analysis and recommendation (BUY/SELL/HOLD) is logically consistent with the Scenario.
        It doesn't have to be correct financial advice, just logical (e.g., bad news -> SELL or HOLD, good news -> BUY).
        Respond with exactly "PASS" or "FAIL".
        """
        try:
            response = self.model.generate_content(prompt)
            result = response.text.strip().upper()
            if "PASS" in result:
                return "PASS"
            return "FAIL"
        except Exception as e:
            print(f"Error evaluating advice: {e}")
            return "FAIL"

if __name__ == "__main__":
    # Test the simulator
    try:
        sim = MarketSimulator()
        s = sim.generate_scenario()
        print(f"Generated Scenario: {s}")
        eval_result = sim.evaluate_advice(s, "This is bad news, so SELL.")
        print(f"Evaluation: {eval_result}")
    except Exception as e:
        print(f"Simulator initialization failed: {e}")
