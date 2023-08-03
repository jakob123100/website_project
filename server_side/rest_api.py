from fastapi import FastAPI, Request
import uvicorn
import mysql.connector
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

#start /home/bokajnevs/.local/bin/uvicorn webb_api:app --reload

app = FastAPI()
#http://127.0.0.1:8000/
#http://213.67.132.100/

sites = [
    "koltrastvägen",
    "finnbacka"
]

#({table_name: str}, (digits:int, decimal:int))
categories = [
    "grid_power_kW", 
    "home_power_kW", 
    "pv_solar_power_kW", 
    "battery_power_kW", 

    "temp_outdoor_c", 
    "temp_indoor_c", 
    "temp_heatpump_in_c", 
    "temp_heatpump_out_c", 
    "temp_sauna_c", 
    "air_pressure_hPa", 

    "grid_import_hour_energy_kWh", 
    "grid_import_day_energy_kWh", 
    "grid_import_week_energy_kWh", 
    "grid_import_month_energy_kWh", 
    "grid_import_year_energy_kWh", 

    "grid_export_hour_energy_kWh", 
    "grid_export_day_energy_kWh", 
    "grid_export_week_energy_kWh", 
    "grid_export_month_energy_kWh", 
    "grid_export_year_energy_kWh", 

    "grid_net_hour_energy_kWh", 
    "grid_net_day_energy_kWh", 
    "grid_net_week_energy_kWh", 
    "grid_net_month_energy_kWh", 
    "grid_net_year_energy_kWh", 

    "pv_solar_hour_energy_kWh", 
    "pv_solar_day_energy_kWh", 
    "pv_solar_week_energy_kWh", 
    "pv_solar_month_energy_kWh", 
    "pv_solar_year_energy_kWh", 

    "home_hour_energy_kWh", 
    "home_day_energy_kWh", 
    "home_week_energy_kWh", 
    "home_month_energy_kWh", 
    "home_year_energy_kWh", 

    "battery_hour_energy_kWh", 
    "battery_day_energy_kWh", 
    "battery_week_energy_kWh", 
    "battery_month_energy_kWh", 
    "battery_year_energy_kWh", 

    "grid_import_end_hour_energy_kWh", 
    "grid_import_end_day_energy_kWh", 
    "grid_import_end_week_energy_kWh", 
    "grid_import_end_month_energy_kWh", 
    "grid_import_end_year_energy_kWh", 

    "grid_export_end_hour_energy_kWh", 
    "grid_export_end_day_energy_kWh", 
    "grid_export_end_week_energy_kWh", 
    "grid_export_end_month_energy_kWh", 
    "grid_export_end_year_energy_kWh", 

    "grid_net_end_hour_energy_kWh", 
    "grid_net_end_day_energy_kWh", 
    "grid_net_end_week_energy_kWh", 
    "grid_net_end_month_energy_kWh", 
    "grid_net_end_year_energy_kWh", 

    "pv_solar_end_hour_energy_kWh", 
    "pv_solar_end_day_energy_kWh", 
    "pv_solar_end_week_energy_kWh", 
    "pv_solar_end_month_energy_kWh", 
    "pv_solar_end_year_energy_kWh", 

    "home_end_hour_energy_kWh", 
    "home_end_day_energy_kWh", 
    "home_end_week_energy_kWh", 
    "home_end_month_energy_kWh", 
    "home_end_year_energy_kWh", 

    "battery_end_hour_energy_kWh", 
    "battery_end_day_energy_kWh", 
    "battery_end_week_energy_kWh", 
    "battery_end_month_energy_kWh", 
    "battery_end_year_energy_kWh", 

    "battery_Soc_percent", 
    "battery_SoH_percent", 
    "battery_capacity_new_kWh", 
    "battery_capacity_now_kWh", 

    "extra1", 
    "extra2", 
    "extra3", 
    "extra4"
]

sql_formula_insert = "INSERT INTO %s (date_time, value) VALUES ('%s', '%s')" #TABLE, DATETIME, FLOAT
sql_formula_get_specific_date_time = "SELECT * FROM %s WHERE date_time = '%s'" #TABLE, DATETIME
sql_formula_get_betwen_date_time = "SELECT * FROM %s WHERE " + \
                     "date_time BETWEEN '%s' AND '%s' ORDER BY date_time DESC" #TABLE, DATETIME, DATETIME

#if (__name__ == "__main__"):
#    uvicorn.run("webb_api:app", host="192.168.0.127", reload=True)

#[ip]/[operation]/[database]/[table]/[query]

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"example": "This is an example", "data": 0}

@app.get("/is-connected")
async def root():
    return {"connected": True}

@app.get("/tables")
async def root():
    mydb = connect_to_database()
    mycursor = mydb.cursor()
    mycursor.execute("SHOW TABLES")

    category_string = ""

    for tb in mycursor:
        category_string += str(tb)
        
    return {"tables": category_string} 

@app.get("/{site}/{category}/get/{operation}")
async def root(site: str, category: str, operation: str, json_data: dict = None):
    if(not site in sites):
        return {"Response": "Site is not reconized"}

    if(not category in categories):
        return {"Response": "category is not reconized"}

    response = None
    table_name = f"{site}_{category}"
    if(operation == "latest"):
        response = get_latets_item_in_table(table_name)
    elif(operation == "all"):
        response = get_all_items_in_table(table_name)
    elif(operation == "between-date-time"):
        response = get_between_date_time(table_name, time_data = json_data)


    return({"Response": response})

def get_latets_item_in_table(table_name: str):
    mydb = connect_to_database()

    mycursor = mydb.cursor()
    mycursor.execute(f"SELECT * FROM {table_name} ORDER BY date_time DESC")

    result = mycursor.fetchone()

    return result

def get_all_items_in_table(table_name: str):
    mydb = connect_to_database()

    mycursor = mydb.cursor()
    mycursor.execute(f"SELECT * FROM {table_name} ORDER BY date_time DESC")

    result = mycursor.fetchall()

    return result

def get_between_date_time(table_name: str, time_data: dict):
    start_date_time = time_data.get("start_time")
    end_date_time = time_data.get("end_time")
    
    if(not is_valid_date_time(start_date_time)):
        return "Invalid start time"
    
    if(not is_valid_date_time(end_date_time)):
        return "Invalid end time"
    
    start_date_time = start_date_time.replace("T", " ")
    end_date_time = end_date_time.replace("T", " ")

    mydb = connect_to_database()

    mycursor = mydb.cursor()
    sql_command = sql_formula_get_betwen_date_time % (table_name, start_date_time, end_date_time)

    mycursor.execute(sql_command)

    result = mycursor.fetchall()

    if(result == None):
        return "No result found"

    return result

@app.post("/{site}/{category}/insert")
async def print_data_packet(site: str, category: str, json_data: dict):
    date_time = json_data.get("date_time")
    value = json_data.get("value")

    if(not site in sites):
        return {"Response": "Site is not reconized"}

    if(not category in categories):
        return {"Response": "category is not reconized"}

    if(not is_valid_date_time(date_time)):
        return {"Message": "Invalid Date Time"}

    try:
        float(value)
    except ValueError:
        return {"Message": "Invalid Value"}

    mydb = connect_to_database()

    mycursor = mydb.cursor()

    sql_command = sql_formula_get_specific_date_time % (site + "_" + category, date_time)
    mycursor.execute(sql_command)
    result = mycursor.fetchall()

    if(len(result) != 0):
        return {"Message": "Time already documented"}

    sql_command = sql_formula_insert % (category, date_time, value)

    mycursor.execute(sql_command)
    mydb.commit()

    return {"Message": "Db updated"}

@app.get("/clear")
async def clear_db():
    for site in sites:
        for category in categories:
            mydb = connect_to_database()

            mycursor = mydb.cursor()

            sql_command = f"DELETE FROM {site}_{category}"
            mycursor.execute(sql_command)
            mydb.commit()

    return {"Message": "Db cleared"}


def is_valid_date_time(date_time: str) -> bool:
    format = "%Y-%m-%dT%H:%M:%S"
    try:
        valid_time = bool(datetime.strptime(date_time, format))
    except ValueError:
        return False
    return True

def connect_to_database(database_name: str = "koltrast_15_data"):
    database = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="Linnea02",
        database="koltrast_15_data"
    )

    return database


"""
for category in categories:
    mydb = connect_to_database()

    mycursor = mydb.cursor()

    sql_command = f"DELETE FROM {category}"
    mycursor.execute(sql_command)
    mydb.commit()
"""