import requests

# Test messages
test_cases = [
    # Legit messages
    ("Hi team, please find attached the meeting minutes from yesterday.", "legit"),
    ("Thank you for your order. Your package will arrive in 3-5 business days.", "legit"),
    ("Can we schedule a call for next week to discuss the project?", "legit"),

    # Likely spam / suspicious
    ("Your payment failed. Update your details to avoid service interruption.", "likely spam"),
    ("Congratulations! You've won a free iPhone. Click here to claim.", "likely spam"),
    ("Urgent: Your account has been suspended. Verify now.", "likely spam"),

    # Scam messages
    ("Your bank account has been compromised. Send your details immediately.", "scam"),
    ("Invest in Bitcoin now and double your money in 24 hours!", "scam"),
    ("This is the IRS. You owe taxes. Pay now or face arrest.", "scam"),
]

print("Testing model predictions via API...\n")

for text, expected in test_cases:
    try:
        response = requests.post("http://127.0.0.1:8000/predict", json={"text": text})
        data = response.json()
        prediction = data["prediction"]
        confidence = data["confidence"]
        status = "✓" if prediction == expected else "✗"
        print(f"{status} Expected: {expected.upper()} | Predicted: {prediction.upper()} | Confidence: {confidence:.4f}")
        print(f"   Text: {text[:50]}...")
        print()
    except Exception as e:
        print(f"Error testing: {text[:30]}... - {e}")
        print()

print("Test complete.")