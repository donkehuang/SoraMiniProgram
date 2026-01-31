from openai import OpenAI
client = OpenAI()

resp = client.responses.create(
  model="gpt-5",
  reasoning={"effort": "medium"},
  tools=[{ "type": "web_search", "external_web_access": False }],
  tool_choice="auto",
  input="Get me one funny news story from today. Tell me this story in a narrative style, keeping it under five sentences. Make sure the story retains its humor. Output in Chinese.",
)
print(resp.output_text)