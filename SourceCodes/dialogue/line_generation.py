from openai import OpenAI
from datetime import datetime
from dialogue.extract_prompt_from_time import read_prompt_by_time
from dialogue.save_generated_lines import save_to_csv
client = OpenAI()

def generate_dialogue_line(prompt_suggestion: str) -> str:
    response = client.responses.create(
        model="gpt-5",
        reasoning={"effort": "low"},
        input=[
            {
                "role": "developer",
                "content": "A funny short film featuring a cat and a dog imitating human stand-up comedy, offering a cat's perspective on criticizing humans. ",
            },
            {
                "role": "user",
                "content": prompt_suggestion,
            }
        ]
    )
    return response.output_text


def generate_and_save_line(current_time: str, csv_suggestion_path: str, generated_lines_path: str, first_frame_image: str = ""):
    prompt_suggestion = read_prompt_by_time(csv_suggestion_path)
    line_generated = generate_dialogue_line(prompt_suggestion)
    print(" Generated Dialogue Line:", line_generated)
    save_to_csv(generated_lines_path, current_time, prompt_suggestion, line_generated, first_frame_image)


if __name__ == "__main__":

    csv_suggestion_path = "ScriptsLists\prompts.csv"
    generated_lines_path = "ScriptsLists\generated_lines.csv"
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    generate_and_save_line(current_time, csv_suggestion_path, generated_lines_path)