from flask import Flask, request, jsonify
from api_key import my_api_key
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app) 

def get_flight_details(api_key, from_city, to_city, outbound_date, return_date=None, currency="USD"):
    api_url = "https://serpapi.com/search"
    
    params = {
        "api_key": api_key,
        "engine": "google_flights",
        "departure_id": from_city,
        "arrival_id": to_city,
        "currency": currency
    }
    
    if return_date:
        params["type"] = "1"
        params["outbound_date"] = outbound_date
        params["return_date"] = return_date
    else:
        params["type"] = "2"
        params["outbound_date"] = outbound_date
    
    response = requests.get(api_url, params=params)
    
    if response.status_code == 200:
        flight_data = response.json()
        return flight_data
    else:
        return None

def format_flight_details(flight_details, currency="USD"):
    formatted_details = []
    for best_flight in flight_details.get('best_flights', []):
        for flight in best_flight.get('flights', []):
            departure_airport = flight['departure_airport']['name']
            arrival_airport = flight['arrival_airport']['name']
            departure_time = flight['departure_airport']['time']
            arrival_time = flight['arrival_airport']['time']
            duration = flight['duration']
            price = flight_details['price_insights']['lowest_price']
            formatted_flight = {
                "Departure Airport": departure_airport,
                "Arrival Airport": arrival_airport,
                "Departure Time": departure_time,
                "Arrival Time": arrival_time,
                "Duration (minutes)": duration,
                "Price (USD)": price  # Always in USD
            }
            formatted_details.append(formatted_flight)
    return formatted_details

@app.route('/flight-details', methods=['POST'])
def get_flight_details_route():
    data = request.json
    api_key = my_api_key
    from_city = data.get("from_city")
    to_city = data.get("to_city")
    trip_type = data.get("trip_type")
    outbound_date = data.get("outbound_date")
    return_date = data.get("return_date")
    currency = "USD"  # Always in USD as per requirement

    if trip_type not in ["1", "2"]:
        return jsonify({"error": "Invalid trip type. Choose 1 or 2."}), 400

    flight_details = get_flight_details(api_key, from_city, to_city, outbound_date, return_date, currency)
    if flight_details:
        formatted_details = format_flight_details(flight_details, currency)
        return jsonify(formatted_details)
    else:
        return jsonify({"error": "Failed to retrieve flight details."}), 500

if __name__ == "__main__":
    app.run(debug=True)
