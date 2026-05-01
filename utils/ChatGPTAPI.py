from dotenv import load_dotenv
import os
from openai import OpenAI
#from Prompt import prompt

load_dotenv("APIKEY.env")
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI()

def create_file(file_path):
  with open(file_path, "rb") as file_content:
    result = client.files.create(
        file=file_content,
        purpose="vision",
    )
    return result.id

# Getting the file ID
#file_id = create_file("/home/jasonzou/Downloads/Figure_1.png")

def call_gpt(prompt, file_id):
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {"type": "input_image", "file_id": file_id},
            ],
        }],
        text={
            "format": {
                "type": "json_object"
            }
        },
    )
    return response.output_text

#print(response.output_text)