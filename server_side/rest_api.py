from fastapi import FastAPI, Request
import uvicorn
import mysql.connector
from datetime import datetime
from ..client-side import api

#start /home/bokajnevs/.local/bin/uvicorn webb_api:app --reload

app = FastAPI()
#http://127.0.0.1:8000/
#http://213.67.132.100/

categories = [
    'air_pressure_hPa',
    'day_battery_cumulative_energy_kWh',
    'day_battery_power_kW',
    'day_battery_soC',
    'day_grid_cumulative_energy_kWh',
    'day_grid_power_kW',
    'day_home_cumulative_energy_kWh',
    'day_home_power_kW',
    'day_pv_cumulative_energy_kWh',
    'day_pv_power_kW',
    'month_grid_energy_kWh',
    'month_house_energy_kWh',
    'month_pv_energy_kWh',
    'temp_heatpump_in_c',
    'temp_heatpump_out_c',
    'temp_indoor_c',
    'temp_outdoor_c',
    'temp_sauna_c',
    'week_grid_energy_kWh',
    'week_house_energy_kWh',
    'week_pv_energy_kWh',
    'year_grid_energy_kWh',
    'year_house_energy_kWh',
    'year_pv_energy_kWh',
]

sql_formula_insert = "INSERT INTO %s (date_time, value) VALUES ('%s', '%s')" #TABLE, DATETIME, FLOAT
sql_formula_get_specific_date_time = "SELECT * FROM %s WHERE date_time = '%s'" #TABLE, DATETIME
sql_formula_get_betwen_date_time = "SELECT * FROM %s WHERE " + \
                     "date_time BETWEEN '%s' AND '%s' ORDER BY date_time" #TABLE, DATETIME, DATETIME

#if (__name__ == "__main__"):
#    uvicorn.run("webb_api:app", host="192.168.0.127", reload=True)

#[ip]/[database]/[table]/[]

@app.get("/")
async def root():
    return {"example": "This is an example", "data": 0}

@app.get("/IsConnected/")
async def root():
    return {"Connected": True}

@app.get("/Categories/")
async def root():
    mydb = connect_to_database()
    mycursor = mydb.cursor()
    mycursor.execute("SHOW TABLES")

    category_string = ""

    for tb in mycursor:
        category_string += str(tb)
        
    return {"categorys": category_string} 

@app.get("/GetAll/{category}")
async def root(category: str):
    if(not category in categories):
        return "Invalid category"

    mydb = connect_to_database()

    mycursor = mydb.cursor()
    mycursor.execute(f"SELECT * FROM {category} ORDER BY date_time")

    result = mycursor.fetchall()

    if(result == None):
        return "No result found"

    return result

@app.get("/GetBetweenDateTime/{category}/{start_date_time}/{end_date_time}")
async def root(category: str, start_date_time: str, end_date_time: str):
    if(not category in categories):
        return "Invalid category"
    
    if(not is_valid_date_time(start_date_time)):
        return "Invalid start time"
    
    if(not is_valid_date_time(end_date_time)):
        return "Invalid end time"
    
    start_date_time = start_date_time.replace("T", " ")
    end_date_time = end_date_time.replace("T", " ")

    mydb = connect_to_database()

    mycursor = mydb.cursor()
    sql_command = sql_formula_get_betwen_date_time % (category, start_date_time, end_date_time)

    mycursor.execute(sql_command)

    result = mycursor.fetchall()

    if(result == None):
        return "No result found"

    return result

@app.post("/{category}/InsertTest/")
async def root(category: str, time: str, value: str):

    if(not category in categories):
        return {"Invalid category"}
    
    format = "%Y-%m-%dT%H:%M:%S"

    if(not is_valid_date_time(time)):
        return "Invalid Date Time"

    try:
        float(value)
    except ValueError:
        return "Invalid Value"

    mydb = connect_to_database()

    mycursor = mydb.cursor()

    time = time.replace("T", " ")

    sql_command = sql_formula_get_specific_date_time % (category, time)
    #return sql_command
    mycursor.execute(sql_command)
    result = mycursor.fetchall()

    if(len(result) != 0):
        return "Time already documented"

    sql_command = sql_formula_insert % (category, time, value)

    #return sql_command

    mycursor.execute(sql_command)
    mydb.commit()

    return sql_command

    #mycursor.execute(sql_formula, example_temp)

    #result = mycursor.fetchone()

    #return {"Date": result[0], "Temperature": result[1]}

@app.post("/{category}/Insert/time={time}/value={value}")
async def root(category: str, time: str, value: str):

    if(not category in categories):
        return {"Invalid category"}
    
    format = "%Y-%m-%dT%H:%M:%S"

    if(not is_valid_date_time(time)):
        return "Invalid Date Time"

    try:
        float(value)
    except ValueError:
        return "Invalid Value"

    mydb = connect_to_database()

    mycursor = mydb.cursor()

    time = time.replace("T", " ")

    sql_command = sql_formula_get_specific_date_time % (category, time)
    #return sql_command
    mycursor.execute(sql_command)
    result = mycursor.fetchall()

    if(len(result) != 0):
        return "Time already documented"

    sql_command = sql_formula_insert % (category, time, value)

    #return sql_command

    mycursor.execute(sql_command)
    mydb.commit()

    return sql_command

    #mycursor.execute(sql_formula, example_temp)

    #result = mycursor.fetchone()

    #return {"Date": result[0], "Temperature": result[1]}


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