import os 
import openai
from dotenv import load_dotenv

load_dotenv()

my_api_key = os.getenv("OPENAI_KEY")


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