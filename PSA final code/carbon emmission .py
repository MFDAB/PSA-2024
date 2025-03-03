import requests
import math

def calculate_emission_savings():
    # Constants
    EMISSION_RATE_PER_KM = 0.1  # kg CO₂ per km per container
    BASELINE_UTILIZATION = 0.5   # Assume containers are only 50% utilized without optimization

    # Step 1: Retrieve data from the database
    
    total_baseline_emissions = 0
    total_optimized_emissions = 0

    # Step 2: Calculate emissions for each container
    
    distance = calculate_distance('Port of Hong Kong, Hong Kong','Port of Los Angeles, USA')
    cargos_in_container = 10  # Number of cargos packed

    # Assume max capacity is 10 cargos per container for this example
    max_capacity = 10

     # Baseline emissions (assuming 50% utilization)
    baseline_emissions = (distance * EMISSION_RATE_PER_KM) / BASELINE_UTILIZATION
    total_baseline_emissions += baseline_emissions

    # Optimized emissions based on actual utilization
    utilization_ratio = cargos_in_container / max_capacity
    optimized_emissions = distance * EMISSION_RATE_PER_KM * utilization_ratio
    total_optimized_emissions += optimized_emissions

    # Step 3: Calculate savings and percentage
    emissions_saved = total_baseline_emissions - total_optimized_emissions
    savings_percentage = (emissions_saved / total_baseline_emissions) * 100

    # Step 4: Return results
    return {
        'baseline_emissions': total_baseline_emissions,
        'optimized_emissions': total_optimized_emissions,
        'emissions_saved': emissions_saved,
        'savings_percentage': savings_percentage
    }


    
def get_lat_long(location):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        'address': location,
        'key': 'AIzaSyDFlQy2yBwug1vMuffg7cG-RfsBqSTwXDA'
    }
    response = requests.get(url, params=params)
    data = response.json()

    if response.status_code == 200 and data['status'] == 'OK':
        # Extracting the latitude and longitude
        lat_long = data['results'][0]['geometry']['location']
        return lat_long['lat'], lat_long['lng']
    else:
        raise Exception("Error in API response: {}".format(data.get('error_message', 'No error message provided')))

def haversine(lat1, lon1, lat2, lon2):
    r = 6371  # Radius of Earth in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)

    c = 2 * math.asin(math.sqrt(a))
    distance = r * c  # Distance in kilometers
    return distance

def calculate_distance(origin, destination):
    # Get latitude and longitude for both locations
    lat1, lon1 = get_lat_long(origin)
    lat2, lon2 = get_lat_long(destination)

    # Calculate the distance using Haversine formula
    distance = haversine(lat1, lon1, lat2, lon2)
    return distance


results = calculate_emission_savings()

# Print results
print("Emission Savings Results:")
print(f"Baseline Emissions: {results['baseline_emissions']:.2f} kg CO₂")
print(f"Optimized Emissions: {results['optimized_emissions']:.2f} kg CO₂")
print(f"Emissions Saved: {results['emissions_saved']:.2f} kg CO₂")
print(f"Savings Percentage: {results['savings_percentage']:.2f}%")
