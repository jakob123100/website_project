import requests
from datetime import datetime

class datebase_inteface:
    class datatypes:
        class temperatures:
            heatpump_in = 0
            heatpump_out = 1
            indoor = 2
            outdoor = 3
            sauna = 4

    __api_url = "http://217.208.66.120:7777/"
    __is_connected_api_path = "is-connected"

    class paths:
        class categories:
            class temperatures:
                heatpump_in = 'temp_heatpump_in_c'
                heatpump_out = 'temp_heatpump_out_c'
                indoor = 'temp_indoor_c'
                outdoor = 'temp_outdoor_c'
                sauna = 'temp_sauna_c'


    def __init__(self) -> None:
        pass

    def __datetime_to_str(self, date_time: datetime) -> str:
        date_time_string = str(date_time).replace(" ", "T")
        date_time_string = date_time_string[:19]
        return date_time_string

    def __request_json_data(self, path, json_data: dict = None) -> dict:
        try:
            #print(self.__api_url + path)
            response = requests.get(self.__api_url + path, json=json_data)
        except requests.exceptions.InvalidURL:
            print("Could not connect to api url")
            return None

        print(response)

        return response.json()
    
    def __post_json_data(self, path, date_time: datetime, value: float):
        date_time_string = str(date_time).replace(" ", "T")
        date_time_string = date_time_string[:19]

        try:
            print(self.__api_url + path)
            json_data = {"date_time": date_time_string, "value": value}
            response = requests.post(self.__api_url + path, json=json_data)
        except requests.exceptions.InvalidURL:
            print("Could not connect to api url")
            return None

        print(response)
        return response.json()
    
    def __get_category_string(self, datatype) -> str:
        if(datatype == self.datatypes.temperatures.indoor):
            return self.paths.categories.temperatures.indoor
        
        if(datatype == self.datatypes.temperatures.outdoor):
            return self.paths.categories.temperatures.outdoor
        
        if(datatype == self.datatypes.temperatures.heatpump_in):
            return self.paths.categories.temperatures.heatpump_in
        
        if(datatype == self.datatypes.temperatures.heatpump_out):
            return self.paths.categories.temperatures.heatpump_out
        
        if(datatype == self.datatypes.temperatures.sauna):
            return self.paths.categories.temperatures.sauna

    def is_connencted(self) -> bool:
        response = self.__request_json_data(self.__is_connected_api_path)
        try:
            connected = response["Connected"] == True
        except:
            connected = False

        return connected
    
    def get_latest(self, datatype) -> dict:
        category = self.__get_category_string(datatype)
        response_data: dict = self.__request_json_data(f"{category}/get/latest")
        return response_data
    
    def get_all(self, datatype) -> dict:
        category = self.__get_category_string(datatype)
        response_data: dict = self.__request_json_data(f"{category}/get/latest")
        return response_data
    
    def get_between_time(self, datatype: int, start_time: datetime, end_time: datetime) -> dict:
        category = self.__get_category_string(datatype)
        start_time_str = self.__datetime_to_str(start_time)
        end_time_str = self.__datetime_to_str(end_time)
        time_data = {"start_time": start_time_str, "end_time": end_time_str}
        
        response_data: dict = self.__request_json_data(f"{category}/get/between-date-time", json_data=time_data)
        return response_data
    
    def instet(self, datatype, date_time: datetime, value: float):
        category = self.__get_category_string(datatype)
        response = self.__post_json_data(f"{category}/insert/", date_time, value)
        return response

if(__name__ == "__main__"):
    #import random
    df = datebase_inteface()
    dt1 = datetime.strptime("2012/07/27T16:30:22", "%Y/%m/%dT%H:%M:%S")
    dt2 = datetime.strptime("2032/07/27T16:30:22", "%Y/%m/%dT%H:%M:%S")
    #dt = datetime.now()

    #dp.date_time = datetime.time
    #dp.value = 24

    #print(df.instet(df.datatype.temp.indoor, dt, random.randrange(0, 100)))
    print(df.get_between_time(df.datatypes.temperatures.indoor, dt1, dt2).get("Response"))
    #last_temp_data = df.get_latest(df.datatype.temperature)
    #print(f"Time: {last_temp_data['Date']}, Temperature: {last_temp_data['Temperature']}")
    pass