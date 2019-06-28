import requests


class Aircraft:
    def __init__(self, init_dict:dict):
        self.name = init_dict["name"]
        self.manufacturer = init_dict["manufacturer"]
        self.type = init_dict["type"]
        self.iata_code = init_dict["iata_code"]
        self.icao_code = init_dict["icao_code"]
        self.passengers = init_dict["passengers"]
        self.speed_kmh = init_dict["speed_kmh"]
        self.speed_kts = init_dict["speed_kts"]
        self.ceiling_m = init_dict["ceiling_m"]
        self.ceiling_ft = init_dict["ceiling_ft"]
        self.range_km = init_dict["range_km"]
        self.range_nm = init_dict["range_nm"]
        self.mtow_kg = init_dict["mtow_kg"]
        self.mtow_lbs = init_dict["mtow_lbs"]
        self.alias = init_dict["alias"]

    def to_dict(self):
        return self.__dict__


class Route:
    def __init__(self, init_dict:dict):
        self.speed_km = init_dict["totals"]["speed_kmh"]
        self.speed_nm = init_dict["totals"]["speed_kts"]

        self.distance_km = init_dict["legs"][0]["distance_km"]
        self.distance_nm = init_dict["legs"][0]["distance_nm"]
        self.flight_time_min = init_dict["legs"][0]["flight_time_min"]
        self.heading_deg = init_dict["legs"][0]["heading_deg"]
        self.heading_compass = init_dict["legs"][0]["heading_compass"]
        self.origin = RoutePoint(init_dict["legs"][0]["origin"])
        self.destination = RoutePoint(init_dict["legs"][0]["destination"])

    def to_dict(self):
        self_as_dict = self.__dict__
        self_as_dict["origin"] = self.origin.to_dict()
        self_as_dict["destination"] = self.destination.to_dict()

        return self_as_dict


class RoutePoint:
    def __init__(self, init_dict:dict):
        self.id = init_dict["id"]
        self.ident = init_dict["ident"]
        self.name = init_dict["name"]
        self.elevation_ft = init_dict["elevation_ft"]
        self.icao_code = init_dict["icao_code"]
        self.iata_code = init_dict["iata_code"]
        self.alias = init_dict["alias"]
        self.latitude_deg = init_dict["latitude_deg"]
        self.longitude_deg = init_dict["longitude_deg"]
        self.latitude_minsec = MinSec(init_dict["latitude_minsec"]) # TODO
        self.longitude_minsec = MinSec(init_dict["longitude_minsec"]) # TODO
        self.link = init_dict["link"]

    def to_dict(self):
        self_as_dict = self.__dict__
        self_as_dict["latitude_minsec"] = self.latitude_minsec.to_dict()
        self_as_dict["longitude_minsec"] = self.longitude_minsec.to_dict()

        return self_as_dict


class Airport:
    def __init__(self, init_dict:dict):
        self.ident = init_dict["ident"]
        self.name = init_dict["name"]
        self.municipality = init_dict["municipality"] if "municipality" in init_dict.keys() else None
        self.icao_code = init_dict["icao_code"]
        self.country = init_dict["country"] if "country" in init_dict.keys() else None
        self.region = init_dict["region"] if "region" in init_dict.keys() else None

    def to_dict(self):
        return self.__dict__


class MinSec:
    def __init__(self, init_str:str):
        pass    # TODO

    def to_dict(self):
        return self.__dict__

class CircleMapper:
    def __init__(self, api_key: str):
        self.header = self._get_header(api_key)

    def route_calculation(self, speed_kts: float, orig_airport_icao: str, dest_airport_icao: str):
        """
        Returns all route specific information for the given trip between two airports. None if an error occurs.
        :param speed_kts: the planes traveling speed in knots
        :param orig_airport_icao: the ICAO of the origin airport
        :param dest_airport_icao: the ICAO of the destination airport
        :return: An Route object containing all APIs information. None if an error occurs.
        """
        request_url = "https://greatcirclemapper.p.rapidapi.com/airports/route/{}-{}/{}".format(orig_airport_icao.upper(),
                                                                                                dest_airport_icao.upper(),
                                                                                                str(speed_kts))
        response = requests.get(url=request_url, headers=self.header)
        if self._is_bad_response(response):
            return None
        else:
            return Route(response.json())

    def read_aircraft_type(self, icao_iata: str):
        """
        Returns all aircraft specific information. None if an error occurs.
        :param icao_iata: The ICAO or IATA of the plane.
        :return: An Aircraft object containing all APIs information. None if an error occurs.
        """
        request_url = "https://greatcirclemapper.p.rapidapi.com/aircraft/read/{}".format(icao_iata)
        response = requests.get(url=request_url, headers=self.header)
        if self._is_bad_response(response):
            return None
        else:
            return Aircraft(response.json())

    def read_airport(self, airport_icao_iata: str):
        """
        Returns all airport specific information. None if an error occurs.
        :param airport_icao_iata: The ICAO or IATA of the airport.
        :return: An Airport object containing all APIs information. None if an error occurs.
        """
        request_url = "https://greatcirclemapper.p.rapidapi.com/airports/read/{}".format(airport_icao_iata)
        response = requests.get(url=request_url, headers=self.header)
        if self._is_bad_response(response):
            return None
        else:
            return Airport(response.json())

    def search_airport_by_icao(self, icao: str):
        """
        Returns a List of Airport objects containing all airports of the given ICAO region. None if an error occurs.
        :param icao: The ICAO of the airports region.
        :return: A List of Airport objects containing all airports of the given ICAO region. None if an error occurs.
        """
        # returns a list
        return self._search_airport(icao)

    def search_airport_by_iata(self, iata: str):
        """
        Returns a List of Airport objects containing all airports of the given IATA region. None if an error occurs.
        :param iata: The IATA of the airports region.
        :return: A List of Airport objects containing all airports of the given IATA region. None if an error occurs.
        """
        # returns a list
        return self._search_airport(iata)

    def search_airport_by_town(self, town: str):
        """
        Returns a List of Airport objects containing all airports of the given town region. None if an error occurs.
        :param town: The town name of the airports region.
        :return: A List of Airport objects containing all airports of the given ICAO region. None if an error occurs.
        """
        # returns a list
        return self._search_airport(town)

    def _search_airport(self, location_identification: str):
        request_url = "https://greatcirclemapper.p.rapidapi.com/airports/search/{}".format(location_identification)
        response = requests.get(url=request_url, headers=self.header)
        if self._is_bad_response(response):
            return None
        else:
            response_object= response.json()
            # returns a list
            return [Airport(element) for element in response_object]

    def _get_header(self, api_key: str):
        return {
            "X-RapidAPI-Host": "greatcirclemapper.p.rapidapi.com",
            "X-RapidAPI-Key": api_key,
        }

    def _is_bad_response(self, response):
        return response.status_code != 200

if __name__ == "__main__":
    api = CircleMapper("4ec00197d4msh0c15eedf6e8292cp1ced08jsn78e663cb2bb1")

    print(api.route_calculation(1000, "KADG", "KJFK").to_dict())
    print("\n########################\n")

    print(api.read_aircraft_type("A388").to_dict())
    print("\n########################\n")

    print(api.read_airport("KADG").to_dict())
    print("\n########################\n")

    for element in api.search_airport_by_iata("CGN"):
        print(element.to_dict())
    print("\n########################\n")

    for element in api.search_airport_by_icao("EDDK"):
        print(element.to_dict())
    print("\n########################\n")

    for element in api.search_airport_by_town("Frankfurt"):
        print(element.to_dict())
    print("\n########################\n")
