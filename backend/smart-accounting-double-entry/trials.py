
from google import genai

client = genai.Client(api_key="KEY")

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents="""
    Classify the following invoice:

    Description:
    Annual server maintenance

    Return:
    - account_code
    - confidence
    - reasoning
    """
)

print(response.text)