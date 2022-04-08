import logging
import traceback
import csv
import pymysql
from dbutils.persistent_db import PersistentDB

import app.factory
import app.globals as glob
from configparser import ConfigParser
import pandas as pd
import os

config = ConfigParser()
config.read('static/preferences.ini')
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
        sql = "CREATE TABLE %s LIKE `values`"
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
        fileSize = os.path.getsize(app.factory.root_path + '/logs/tmpBuffer.csv')
        # regular case: There was no connection error and is no connection error
        if fileSize == 0:
            sql = "INSERT INTO `values` VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (str(data['time']), data['temp1'], data['temp2'], data['temp3'], data['temp4']))
        # there was a connection error and now it is solved --> insert values from the last times
        else:
            reader = pd.read_csv(app.factory.root_path + '/logs/tmpBuffer.csv', header=None)
            sql = "INSERT INTO `values` (zeit, temp1, temp2, temp3, temp4) VALUES (%s, %s, %s, %s, %s)"
            cursor.executemany(sql, list(reader).append(data))
            with open(app.factory.root_path + '/logs/tmpBuffer.csv', 'w') as file:
                file.truncate()
        cnx.commit()
        cursor.close()
        cnx.close()
    except Exception as ex:
        try:
            if glob.WARN_LEVEL < 2:
                glob.WARN_LEVEL = 2
            with open(app.factory.root_path + '/logs/tmpBuffer.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow([str(data['time']), data['temp1'], data['temp2'], data['temp3'], data['temp4']])
                logging.error("db_connection.insertValue(): " + str(ex) + "\n" + traceback.format_exc())
        except Exception as ex:
            glob.WARN_LEVEL = 3
            logging.error("db_connection.insertValue().writeTo(): " + str(
                ex) + "\n" + traceback.format_exc() + ex.__class__.__name__, )


def getValuesFromTo(timeFrom, timeTo):
    try:
        cnx = mysql_connection_pool.connection()
        cursor = cnx.cursor()
        sql = "SELECT zeit, temp1, temp2, temp3, temp4 FROM `values` WHERE zeit >= %s AND zeit <= %s"
        cursor.execute(sql, (timeFrom, timeTo + '+ 23:59:59.999'))
        result = cursor.fetchall()
        cursor.close()
        cnx.close()
        return result
    except Exception as ex:
        if glob.WARN_LEVEL < 1:
            glob.WARN_LEVEL = 1
        logging.error("db_connection.getValuesFromTo(): " + str(ex) + "\n" + traceback.format_exc())


def getMinMaxDate():
    try:
        cnx = mysql_connection_pool.connection()
        cursor = cnx.cursor()
        sql = "SELECT MIN(zeit), MAX(zeit) FROM `values`"
        cursor.execute(sql, )
        result = cursor.fetchone()
        cursor.close()
        return {
            'minDate': result[0],
            'maxDate': result[1]
        }
    except Exception as ex:
        if glob.WARN_LEVEL < 1:
            glob.WARN_LEVEL = 1
        logging.error("db_connection.getMinMaxDate(): " + str(ex) + "\n" + traceback.format_exc())


def getLatestValues(amount):
    try:
        cnx = mysql_connection_pool.connection()
        cursor = cnx.cursor()
        sql = "SELECT * FROM `values` ORDER BY zeit DESC LIMIT %s"
        cursor.execute(sql, amount)
        result = cursor.fetchall()
        cursor.close()
        return result
    except Exception as ex:
        if glob.WARN_LEVEL < 1:
            glob.WARN_LEVEL = 1
        logging.error("db_connection.getLatestValues(): " + str(ex) + "\n" + traceback.format_exc())
