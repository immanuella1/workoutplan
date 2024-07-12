import os 
import openai
from dotenv import load_dotenv

load_dotenv()

my_api_key = os.getenv("OPENAI_KEY")


client = openai

def workoutRecommendation(goal, height, current_weight):
    prompt = f'''
        Using this goal "{goal}", create a workout plan for me to meet my goals. Please also take into account that my current height is {height} inches and my current weight is {current_weight} pounds. 

        The output should be in the following format:
        Monday: ...
        Tuesday: ...
        Wednesday: ...
        Thursday: ...
        Friday: ...
        Saturday: ...
        Sunday: ...
        Nutrition Goals: XXX calories a day - XXX grams of protein

        For example:
        Nutrition Goals: 2000 calories a day - 150 grams of protein
        
        DO NOT RETURN ANYTHING ELSE FOR NUTRITION GOALS OUTSIDE OF WHAT IS SPECIFIED

        Please return the information in plain text, with no markdown.
    '''
    completion = client.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are giving the user a workout plan based on the information given in a weekly format where there is a specific set of workouts for each day of the week"},
            {"role": "user", "content": prompt}
        ]
    )  
    return completion.choices[0].message.content

info = "User's height, weight, goal and time frame"

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