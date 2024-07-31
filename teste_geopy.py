from geopy.geocoders import Nominatim
from geopy import distance

geolocator = Nominatim(user_agent="Teste129")

c1 = "SANTO ANDRÉ"

c2 = "ARARAQUARA"

l1 = geolocator.geocode(c1)
l2 = geolocator.geocode(c2)

loc1 = ((l1.latitude, l1.longitude))
loc2 = ((l2.latitude, l2.longitude))

print(f'{distance.distance(loc1, loc2).km:.2f}', "kms")