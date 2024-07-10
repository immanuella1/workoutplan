import os 
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')

client = openai

def workoutRecommendation(goal, height, current_weight):
    completion = client.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are giving the user a workout plan based on the information given in a weekly format where there is a specific set of workouts for each day of the week"},
            {"role": "user", "content": f'Using this goal "{goal}", create a workout plan for me to meet my goals. Please also take into account that my current height is {height} inches and my current weight is {current_weight} pounds. The output should be in the following format: Monday: ... Tuesday: ... Wednesday: ... Thursday: ... Friday: ... Saturday: ... Sunday: ... Nutrition Goals: ... DO NOT RETURN ANY MARKDOWN'}
        ]
    )  
    return completion.choices[0].message.content

# print(workoutRecommendation("I want to improve my sprint time in the 100m from 12 seconds to 11.5"))