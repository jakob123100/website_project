import requests
from datetime import datetime

class datebase_inteface:
    class datatype:
        class temp:
            heatpump_in = 0
            heatpump_out = 1
            indoor = 2
            outdoor = 3
            sauna = 4

    __api_url = "http://213.67.132.100:80/"
    __is_connected_api_path = "IsConnected"
    __get_latest_api_path = "GetLatest"

    class paths:
        class categories:
            class temps:
                heatpump_in = 'temp_heatpump_in_c'
                heatpump_out = 'temp_heatpump_out_c'
                indoor = 'temp_indoor_c'
                outdoor = 'temp_outdoor_c'
                sauna = 'temp_sauna_c'


    def __init__(self) -> None:
        pass

    def __request_json_data(self, path) -> dict:
        try:
            #print(self.__api_url + path)
            response = requests.get(self.__api_url + path)
        except requests.exceptions.InvalidURL:
            print("Could not connect to api url")
            return None

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
        if(datatype == self.datatype.temp.indoor):
            return self.paths.categories.temps.indoor

    def is_connencted(self) -> bool:
        response = self.__request_json_data(self.__is_connected_api_path)
        try:
            connected = response["Connected"] == True
        except:
            connected = False

        return connected
    
    def get_latest(self, datatype) -> dict:
        category = self.__get_category_string(datatype)
        temperature_data: dict = self.__request_json_data(f"{category}/{self.__get_latest_api_path}")
        return temperature_data
    
    def instet(self, datatype, date_time: datetime, value: float):
        category = self.__get_category_string(datatype)
        response = self.__post_json_data(f"{category}/InsertTest/", date_time, value)
        return response

    
df = datebase_inteface()
dt = datetime.strptime("2022/07/27T16:30:22", "%Y/%m/%dT%H:%M:%S")
#dt = datetime.now()

#dp.date_time = datetime.time
#dp.value = 24

print(df.test_instet(df.datatype.temp.indoor, dt, 333.3))
#last_temp_data = df.get_latest(df.datatype.temperature)
#print(f"Time: {last_temp_data['Date']}, Temperature: {last_temp_data['Temperature']}")