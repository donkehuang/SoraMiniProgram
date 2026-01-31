from openai import OpenAI
from datetime import datetime

client = OpenAI()

def optimize_scrpits(prompt_suggestion: str) -> str:
    response = client.responses.create(
        model="gpt-5",
        reasoning={"effort": "low"},
        input=[
            {
                "role": "developer",
                "content": "You are an excellent comedy director. I need you to optimize the script based on these requirements. The video length is 8 seconds, so you can add some background music as needed. Chinese subtitles are needed, and the dubbing should be in Mandarin Chinese.",
            },
            {
                "role": "user",
                "content": prompt_suggestion,
            }
        ]
    )
    return response.output_text


if __name__ == "__main__":
    prompt_suggestion = "The puppy is playing in the park and meets a butterfly."
    optimized_script = optimize_scrpits(prompt_suggestion)
    print("Optimized Script:", optimized_script)
