import datetime
import logging
import traceback
import csv
import pyodbc
from dbutils.persistent_db import PersistentDB

import app.factory
import app.globals as glob
from configparser import ConfigParser
import pandas as pd
import os



config = ConfigParser()
config.read('static/preferences.ini')
db_config = {
    'host': config['mssql']['host'],
    'user': config['mssql']['user'],
    'password': config['mssql']['password'],
    'database': config['mssql']['database'],
    'connect_timeout': int(config['mssql']['connect_timeout']),
    'driver': config['mssql']['driver'],
    'TrustServerCertificate': config['mssql']['TSC'],
}

sql_connection_pool = PersistentDB(
    creator=pyodbc,
    **db_config
)

def createTable(tableName):
    try:
        cnx = sql_connection_pool.connection()
        cursor = cnx.cursor()
        sql = "CREATE TABLE ? LIKE messwerte"
        cursor.execute(sql, (tableName))
        cnx.commit()
        cursor.close()
        cnx.close()
    except Exception as ex:
        logging.error("db_connection.createTable(): " + str(ex) + "\n" + traceback.format_exc())


def insertValue(data):
    try:
        cnx = sql_connection_pool.connection()
        cursor = cnx.cursor()
        fileSize = os.path.getsize(app.factory.root_path + '/logs/tmpBuffer.csv')
        # regular case: There was no connection error and is no connection error
        if fileSize == 0:
            sql = "INSERT INTO messwerte VALUES (?,?,?,?,?)"
            cursor.execute(sql, (data['time'], data['temp1'], data['temp2'], data['temp3'], data['temp4']))
        # there was a connection error and now it is solved --> insert values from the last times
        else:
            reader = pd.read_csv(app.factory.root_path + '/logs/tmpBuffer.csv', header=None)
            tmpdata = list(reader.values.tolist())
            for row in tmpdata:
                row[0] = datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f')
            tmpdata.append([data['time'], data['temp1'], data['temp2'], data['temp3'], data['temp4']])
            sql = "INSERT INTO messwerte (zeit, temp1, temp2, temp3, temp4) VALUES (?,?,?,?,?)"
            cursor.executemany(sql, tmpdata)
            with open(app.factory.root_path + '/logs/tmpBuffer.csv', 'w') as file:
                file.truncate()
        cnx.commit()
        cursor.close()
        cnx.close()
    except Exception as ex:
        try:
            glob.setWarnLevel(2)
            with open(app.factory.root_path + '/logs/tmpBuffer.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow([data['time'], data['temp1'], data['temp2'], data['temp3'], data['temp4']])
                logging.error("db_connection.insertValue(): " + str(ex) + "\n" + traceback.format_exc())
        except Exception as ex:
            glob.setWarnLevel(3)
            logging.error("db_connection.insertValue().writeTo(): " + str(ex) + "\n" + traceback.format_exc())


def getValuesFromTo(timeFrom, timeTo):
    try:
        timeFrom = datetime.datetime.strptime(timeFrom, '%Y-%m-%d')
        timeTo = datetime.datetime.strptime(timeTo + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
        cnx = sql_connection_pool.connection()
        cursor = cnx.cursor()
        sql = "SELECT zeit, temp1, temp2, temp3, temp4 FROM messwerte WHERE zeit >= ? AND zeit <= ?"
        cursor.execute(sql, (timeFrom, timeTo))
        rows = cursor.fetchall()
        cursor.close()
        cnx.close()
        result = []
        for row in rows:
            result.append([x for x in row])
        return result
    except Exception as ex:
        glob.setWarnLevel(1)
        logging.error("db_connection.getValuesFromTo(): " + str(ex) + "\n" + traceback.format_exc())
        return ()


def getMinMaxDate():
    try:
        cnx = sql_connection_pool.connection()
        cursor = cnx.cursor()
        sql = "SELECT MIN(zeit), MAX(zeit) FROM messwerte"
        cursor.execute(sql, )
        result = cursor.fetchone()
        cursor.close()
        return {
            'minDate': result[0],
            'maxDate': result[1]
        }
    except Exception as ex:
        glob.setWarnLevel(1)
        logging.error("db_connection.getMinMaxDate(): " + str(ex) + "\n" + traceback.format_exc())
        return {
            'minDate': datetime.datetime(1, 1, 1, 0, 0),
            'maxDate': datetime.datetime.now()
        }


def getLatestValues(amount):
    try:
        cnx = sql_connection_pool.connection()
        cursor = cnx.cursor()
        sql = "SELECT TOP(?) * FROM messwerte ORDER BY zeit DESC"
        cursor.execute(sql, amount)
        result = cursor.fetchall()
        cursor.close()
        return result
    except Exception as ex:
        glob.setWarnLevel(1)
        logging.error("db_connection.getLatestValues(): " + str(ex) + "\n" + traceback.format_exc())
        return ()
