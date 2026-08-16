import os
from google import genai

os.environ["GEMINI_API_KEY"] = "AQ.Ab8RN6LWy9GV-msQm-lwye4HEc0m_N5mZTPSx-XCpxXn9qFAHA"
client = genai.Client()
for m in client.models.list():
    if "generateContent" in m.supported_actions:
        print(m.name)
