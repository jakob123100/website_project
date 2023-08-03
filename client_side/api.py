import requests
from datetime import datetime

class datebase_inteface:
    __api_url = "http://217.208.66.120:7777/"
    __is_connected_api_path = "is-connected"

    class paths:
        class sites:
            koltrastvägen = "koltrastvägen"
            finnbacka = "finnbacka"

        class categories:
            class temperature:
                heatpump_in = 'temp_heatpump_in_c'
                heatpump_out = 'temp_heatpump_out_c'
                indoor = 'temp_indoor_c'
                outdoor = 'temp_outdoor_c'
                sauna = 'temp_sauna_c'
            
            class grid:
                power = "grid_power_kW"

                class imported:
                    hour = "grid_import_hour_energy_kWh"
                    day = "grid_import_day_energy_kWh"
                    week = "grid_import_week_energy_kWh"
                    month = "grid_import_month_energy_kWh"
                    year = "grid_import_year_energy_kWh"

                class exported:
                    hour = "grid_export_hour_energy_kWh"
                    day = "grid_export_day_energy_kWh"
                    week = "grid_export_week_energy_kWh"
                    month = "grid_export_month_energy_kWh"
                    year = "grid_export_year_energy_kWh"

                class net:
                    hour = "grid_net_hour_energy_kWh"
                    day = "grid_net_day_energy_kWh"
                    week = "grid_net_week_energy_kWh"
                    month = "grid_net_month_energy_kWh"
                    year = "grid_net_year_energy_kWh"

                class end:
                    class imported:
                        hour = "grid_import_end_hour_energy_kWh"
                        day = "grid_import_end_day_energy_kWh"
                        week = "grid_import_end_week_energy_kWh"
                        month = "grid_import_end_month_energy_kWh"
                        year = "grid_import_end_year_energy_kWh"

                    class exported:
                        hour = "grid_export_end_hour_energy_kWh"
                        day = "grid_export_end_day_energy_kWh"
                        week = "grid_export_end_week_energy_kWh"
                        month = "grid_export_end_month_energy_kWh"
                        year = "grid_export_end_year_energy_kWh"

                    class net:
                        hour = "grid_net_end_hour_energy_kWh"
                        day = "grid_net_end_day_energy_kWh"
                        week = "grid_net_end_week_energy_kWh"
                        month = "grid_net_end_month_energy_kWh"
                        year = "grid_net_end_year_energy_kWh"


            class pv:
                power = "pv_solar_power_kW"
                hour = "pv_solar_hour_energy_kWh"
                day = "pv_solar_day_energy_kWh"
                week = "pv_solar_week_energy_kWh"
                month = "pv_solar_month_energy_kWh"
                year = "pv_solar_year_energy_kWh"

                class end:
                    hour = "pv_solar_end_hour_energy_kWh"
                    day = "pv_solar_end_day_energy_kWh"
                    week = "pv_solar_end_week_energy_kWh"
                    month = "pv_solar_end_month_energy_kWh"
                    year = "pv_solar_end_year_energy_kWh"

            class home:
                power = "home_power_kW"
                hour = "home_hour_energy_kWh"
                day = "home_day_energy_kWh"
                week = "home_week_energy_kWh"
                month = "home_month_energy_kWh"
                year = "home_year_energy_kWh"

                class end:
                    hour = "home_end_hour_energy_kWh"
                    day = "home_end_day_energy_kWh"
                    week = "home_end_week_energy_kWh"
                    month = "home_end_month_energy_kWh"
                    year = "home_end_year_energy_kWh"

            class battery:
                power = "battery_power_kW"
                hour = "battery_hour_energy_kWh"
                day = "battery_day_energy_kWh"
                week = "battery_week_energy_kWh"
                month = "battery_month_energy_kWh"
                year = "battery_year_energy_kWh"

                class end:
                    hour = "battery_end_hour_energy_kWh"
                    day = "battery_end_day_energy_kWh"
                    week = "battery_end_week_energy_kWh"
                    month = "battery_end_month_energy_kWh"
                    year = "battery_end_year_energy_kWh"

            class air:
                pressure = "air_pressure_hPa"
            
            class extra:
                extra1 = "extra1"
                extra2 = "extra2"
                extra3 = "extra3"
                extra4 = "extra4"


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

    def is_connencted(self) -> bool:
        response = self.__request_json_data(self.__is_connected_api_path)
        try:
            connected = response["Connected"] == True
        except:
            connected = False

        return connected
    
    def get_latest(self, site:paths.sites, category: paths.categories) -> dict:
        response_data: dict = self.__request_json_data(f"{site}/{category}/get/latest")
        return response_data
    
    def get_all(self, site:paths.sites, category: paths.categories) -> dict:
        response_data: dict = self.__request_json_data(f"{site}/{category}/get/latest")
        return response_data
    
    def get_between_time(self, site:paths.sites, category: paths.categories, start_time: datetime, end_time: datetime) -> dict:
        start_time_str = self.__datetime_to_str(start_time)
        end_time_str = self.__datetime_to_str(end_time)
        time_data = {"start_time": start_time_str, "end_time": end_time_str}
        
        response_data: dict = self.__request_json_data(f"{site}/{category}/get/between-date-time", json_data=time_data)
        return response_data
    
    def insert(self, site:paths.sites, category: paths.categories, date_time: datetime, value: float):
        response = self.__post_json_data(f"{site}/{category}/insert/", date_time, value)
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
    print(df.get_between_time(df.paths.sites.koltrastvägen, df.paths.categories.temperature.outdoor, dt1, dt2).get("Response"))
    #last_temp_data = df.get_latest(df.datatype.temperature)
    #print(f"Time: {last_temp_data['Date']}, Temperature: {last_temp_data['Temperature']}")
    pass