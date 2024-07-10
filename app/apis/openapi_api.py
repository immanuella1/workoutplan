import os 
import openai
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from a .env file
load_dotenv()

my_api_key = os.getenv("OPENAI_KEY")

openai.api_key = os.getenv('OPENAI_API_KEY')

client = openai

def workoutRecomendation(info):
# Specify the model to use and the messages to send
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            #messages needs to be revised and changed 
            {"role": "system", "content": "You are giving the user a workout plan based on the information given in a weekly format where there is a specific set of workouts for each day of the week"},
            {"role": "user", "content": f'Using this information {info}, create a workout plan for me to meet my goals'}
            
        ]
    )   
    return completion.choices[0].message.content

def nutritionRecomendation(info):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            #messages needs to be revised and changed 
            {"role": "system", "content": "You are giving the user a nutritional information based on the personal information given"},
            {"role": "user", "content": f'Using this information {info}, create a nutritional plan'} 
        ]
    )
    return completion.choices[0].message.content
#if __name__ == "__main__":
#    recomendation()