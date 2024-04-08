import requests

def get_car_history(vin):
    url = f'https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/{vin}?format=json'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if 'Results' in data:
            return data['Results']
        else:
            return "Car history not found."
    else:
        return "Error fetching data."

# Пример использования функции
vin_number = '2GKALLEK2G6212010'  # Замените на VIN вашего автомобиля
car_history = get_car_history(vin_number)

if car_history != "Car history not found." and car_history != "Error fetching data.":
    print("Car History:")
    for item in car_history:
        for key, value in item.items():
            print(f"{key}: {value}")
        print("-----------")
else:
    print(car_history)
