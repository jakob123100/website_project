import requests
import datetime

class data_packet:
    date_time: datetime.datetime
    value: float

class data_fetcher:
    class datatype:
        temperature: int = 0

    __api_url = "http://213.67.132.100:80/"
    __is_connected_api_path = "IsConnected"
    __temperature_api_path = "Temperature"
    __get_latest_api_path = "GetLatest"

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
    
    def __post_json_data(self, path, json_data: dict):
        try:
            print(self.__api_url + path)
            response = requests.post(self.__api_url + path, json=json_data)
        except requests.exceptions.InvalidURL:
            print("Could not connect to api url")
            return None

        return response.json()
    
    def __get_category_string(self, datatype) -> str:
        if(datatype == self.datatype.temperature):
            return self.__temperature_api_path

    def is_connencted(self) -> bool:
        response = self.__request_json_data(self.__is_connected_api_path)
        try:
            connected = response["Connected"] == True
        except:
            connected = False

        return connected
    
    def get_latest(self, datatype) -> dict:
        category = self.__get_category_string(datatype)
        temperature_data: dict = self.__request_json_data(f"{category}{self.__get_latest_api_path}")
        return temperature_data
    
    def test_instet(self, datatype, data_packet: dict):
        category = self.__get_category_string(datatype)
        response = self.__post_json_data(f"{category}/InsertTest/", data_packet)
        return response

    
df = data_fetcher()
dt = datetime.datetime.strptime("2023/07/27T16:30:22", "%Y/%m/%d %H:%M:%S")
print(dt)
dp = {"date_time": str(dt), "value": 24}

#dp.date_time = datetime.time
#dp.value = 24

print(df.test_instet(df.datatype.temperature, dp))
#last_temp_data = df.get_latest(df.datatype.temperature)
#print(f"Time: {last_temp_data['Date']}, Temperature: {last_temp_data['Temperature']}")