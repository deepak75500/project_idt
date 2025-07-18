from gemini import Gemini

cookies = {"<key>" : "<value>"} # Cookies may vary by account or region. Consider sending the entire cookie file.
client = Gemini(cookies=cookies) # You can use various args

response = client.generate_content("Hello, Gemini. What's the weather like in Seoul today?")
response.payload