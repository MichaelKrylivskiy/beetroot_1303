from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut


def get_address_from_coordinates(coordinates):
    try:
        # Initialize Nominatim API geocoder
        geolocator = Nominatim(user_agent="reverse_geocode_app")

        # Split the coordinates string into latitude and longitude
        lat, lon = map(float, coordinates.split(','))

        # Perform reverse geocoding
        location = geolocator.reverse((lat, lon), language='en')

        # Return the address if found
        if location:
            return location.address
        else:
            return "Address not found"

    except (ValueError, GeocoderTimedOut) as e:
        print(f"Error: {e}")
        return None


# Example usage:
coordinates = '50.479944,30.489993'
address = get_address_from_coordinates(coordinates)
print(f"The address corresponding to coordinates {coordinates} is:\n{address}")
