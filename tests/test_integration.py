import pytest
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.assistant import TradingAdvisor
from src.tester import MarketSimulator

def test_trading_loop():
    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        pytest.skip("GOOGLE_API_KEY not set")

    print("\n--- Starting Trading AI Integration Test ---")
    
    # 1. Initialize
    try:
        advisor = TradingAdvisor() # Uses default distilgpt2
        simulator = MarketSimulator()
    except Exception as e:
        pytest.fail(f"Initialization failed: {e}")

    # 2. Generate Market Scenario
    scenario = simulator.generate_scenario()
    print(f"Market Scenario: {scenario}")
    assert scenario, "Simulator failed to generate a scenario"

    # 3. Get Trading Advice
    advice = advisor.analyze_scenario(scenario)
    print(f"Trading Advice: {advice}")
    assert advice, "Advisor failed to generate advice"

    # 4. Evaluate Advice
    evaluation = simulator.evaluate_advice(scenario, advice)
    print(f"Evaluation: {evaluation}")
    
    # We don't strictly assert PASS because small models can be dumb, 
    # but we assert the evaluation mechanism worked.
    assert evaluation in ["PASS", "FAIL"], "Invalid evaluation result"
    
    if evaluation == "FAIL":
        print("Warning: Advisor failed the evaluation, but the pipeline worked.")
    else:
        print("Success: Advisor passed the evaluation.")
