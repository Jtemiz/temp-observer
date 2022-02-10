import logging
import traceback
from datetime import datetime
import csv
import pymysql
from dbutils.persistent_db import PersistentDB
from app.globals import TABLENAME, LONGTERM_VALUES
from configparser import ConfigParser
import pandas as pd
import os

config = ConfigParser()
config.read('/Users/jtemiz/finishedProjs/temp-observer/logs/preferences.ini')
db_config = {
    'host': config['mysql']['host'],
    'user': config['mysql']['user'],
    'password': config['mysql']['password'],
    'database': config['mysql']['database'],
    'connect_timeout': int(config['mysql']['connect_timeout'])
}

mysql_connection_pool = PersistentDB(
    creator=pymysql,
    **db_config
)


def createTable(tableName):
    try:
        cnx = mysql_connection_pool.connection()
        cursor = cnx.cursor()
        sql = "CREATE TABLE %s LIKE `y2022`"
        cursor.execute(sql, (tableName))
        cnx.commit()
        cursor.close()
        cnx.close()
    except Exception as ex:
        logging.error("db_connection.createTable(): " + str(ex) + "\n" + traceback.format_exc())


def insertValue(data):
    try:
        cnx = mysql_connection_pool.connection()
        cursor = cnx.cursor()
        fileSize = os.path.getsize('/Users/jtemiz/finishedProjs/temp-observer/logs/tmpBuffer.csv')
        # regular case: There was no connection error and is no connection error
        if fileSize == 0:
            sql = "INSERT INTO `y2022` VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (data['time'], data['temp1'], data['temp2'], data['temp3'], data['temp4']))
            print("No Data to Upload")
        # there was a connection error and no it is solved --> insert values from the last times
        else:
            reader = pd.read_csv('/Users/jtemiz/finishedProjs/temp-observer/logs/tmpBuffer.csv', header=None)
            sql = "INSERT INTO `y2022` (zeit, temp1, temp2, temp3, temp4) VALUES (%s, %s, %s, %s, %s)"
            cursor.executemany(sql, list(reader).append(data))
            with open('/Users/jtemiz/finishedProjs/temp-observer/logs/tmpBuffer.csv', 'w') as file:
                file.truncate()
            print("stored Data uploaded")
        cnx.commit()
        cursor.close()
        cnx.close()
    except Exception as ex:
        try:
            with open('/Users/jtemiz/finishedProjs/temp-observer/logs/tmpBuffer.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow([data['time'], data['temp1'], data['temp2'], data['temp3'], data['temp4']])
                logging.error("db_connection.insertValue(): " + str(ex) + "\n" + traceback.format_exc())
        except Exception as ex:
            logging.error("db_connection.insertValue().writeTo(): " + str(ex) + "\n" + traceback.format_exc() + ex.__class__.__name__,)


def getValuesFromTo(timeFrom, timeTo):
    try:
        print(timeFrom, timeTo)
        cnx = mysql_connection_pool.connection()
        cursor = cnx.cursor()
        sql = "SELECT zeit, temp1, temp2, temp3, temp4 FROM y2022 WHERE zeit > %s AND zeit < %s"
        cursor.execute(sql, (timeFrom.year, timeFrom, timeTo))
        result = cursor.fetchall()
        cursor.close()
        cnx.close()
        return result
    except Exception as ex:
        logging.error("db_connection.getValuesFromTo(): " + str(ex) + "\n" + traceback.format_exc())


def getMinMaxDate():
    try:
        cnx = mysql_connection_pool.connection()
        cursor = cnx.cursor()
        sql = "SELECT MIN(zeit), MAX(zeit) FROM y2022"
        cursor.execute(sql, )
        result = cursor.fetchone()
        cursor.close()
        return {
            'minDate': result[0],
            'maxDate': result[1]
        }
    except Exception as ex:
        logging.error("db_connection.getMinMaxDate(): " + str(ex) + "\n" + traceback.format_exc())

def getLatestValues(amount):
    cnx = mysql_connection_pool.connection()
    cursor = cnx.cursor()
    sql = "SELECT * FROM y2022 ORDER BY zeit DESC LIMIT %s"
    cursor.execute(sql, amount)
    result = cursor.fetchall()
    cursor.close()
    print(result)
    return result
