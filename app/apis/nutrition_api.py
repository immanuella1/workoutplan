import requests
import json


def nutrition_calculator(query):
    url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
    headers = {
        "Content-Type": "application/json",
        "x-app-id": "6f62040c",
        "x-app-key": "d1489824d203fd2f2de64e20ca76bd18",
    }
    body = {"query": f"{query}"}

    response = requests.post(url, headers=headers, data=json.dumps(body))

    if response.status_code == 200:
        data = response.json()

        total_calories = 0
        total_protein = 0
        total_sugars = 0
        total_sodium = 0

        if "foods" in data:
            for food in data["foods"]:
                food_name = food.get("food_name", "Unknown food")
                calories = food.get("nf_calories", 0)
                protein = food.get("nf_protein", 0)
                sugars = food.get("nf_sugars", 0)
                sodium = food.get("nf_sodium", 0)
                """
                print(f"Food: {food_name}")
                print(f"  Calories: {calories}")
                print(f"  Protein: {protein}")
                print(f"  Sugars: {sugars}")
                print(f"  Sodium: {sodium}")
                print()
                """

                total_calories += calories
                total_protein += protein
                total_sugars += sugars if sugars is not None else 0
                total_sodium += sodium

            total_calories = round(total_calories, 2)
            total_protein = round(total_protein, 2)
            total_sugars = round(total_sugars, 2)
            total_sodium = round(total_sodium, 2)

            return {
                "total_calories": total_calories,
                "total_protein": total_protein,
                "total_sugars": total_sugars,
                "total_sodium": total_sodium,
            }

        else:
            print("No food information found in the response")
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
