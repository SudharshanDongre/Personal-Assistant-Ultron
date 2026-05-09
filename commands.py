import google.generativeai as genai



API_KEY = "AIzaSyBIjRpwI575rW_wYgkZQ36-GXbD5HBcaxM"
genai.configure(api_key=API_KEY)

model= genai.GenerativeModel("gemini-2.0 flash")
chat=model.start_chat()
response = chat.send_message("command")
print("Gemini:",response.text)
