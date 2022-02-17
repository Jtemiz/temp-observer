import datetime
import logging
import traceback
import io
import csv as csvPackage

from flask import Blueprint, render_template, url_for, flash, Response, jsonify, request, redirect
import app.backend.db_connection as DBCon

data_bp = Blueprint('data_bp', __name__, template_folder='pages')

@data_bp.route('/data')
def data():
    try:
        return render_template(
            'data.html',
            title="Datenbestand",
            description="Datenbestand",
            dates=DBCon.getMinMaxDate()
        )
    except Exception as ex:
        logging.error("Data.data(): " + str(ex) +
                      "\n" + traceback.format_exc())

@data_bp.route('/saveCSV/<tablename>')
def download_csv(tablename):
    try:
        metadata = DBCon.getMetadata(tablename)
        metadata = list(metadata)
        output = io.StringIO()
        writer = csvPackage.writer(output)
        writer.writerow(['Datum: '])
        writer.writerow(['Prüfer: ' + metadata[0][3]])
        writer.writerow(['Adresse: ' + metadata[0][1]])
        writer.writerow(['Maßnahme: ' + metadata[0][4]])
        writer.writerow(['Gesamtlänge: '+ str(metadata[0][2]) + 'm'])
        line = ['Station;Höhe;Geschw;Breite;Grenze;Kommentar']
        writer.writerow(line)
        data = DBCon.getTable(int(tablename))
        coms = DBCon.getComments(tablename)
        for row in data:
            com = ''
            if len(coms) > 0 and coms[0][0] == row[1]:
                com = coms[0][1]
                coms.pop(0)
            line = [str(row[1]) + ';' + str(row[2]) + ';' + str(row[3] ) + ';' + str(row[4]) + ';' + str(row[5]) + ';' + com]
            writer.writerow(line)
        output.seek(0)
        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-disposition":
                         "attachment; filename=" + tablename})
    except Exception as ex:
        logging.error("Data.download_csv(): " + str(ex) +
                      "\n" + traceback.format_exc())

@data_bp.route('/searchValues', methods=['POST'])
def searchValues():
    try:
        dateFrom = request.form['minDate']
        dateTo = request.form['maxDate']
        print(dateFrom)
        values = DBCon.getValuesFromTo(dateFrom, dateTo)
        print(values)
        return jsonify(values)
    except Exception as ex:
        logging.error("Data.getTable(): " + str(ex) +
                      "\n" + traceback.format_exc())

@data_bp.route('/deleteTable', methods=['POST'])
def deleteTable():
    try:
        tn = request.form['tablename']
        DBCon.dropTable(tn)
        return redirect(url_for('data_bp.data'))
    except Exception as ex:
        logging.error("Data.deleteTable(): " + str(ex) +
                      "\n" + traceback.format_exc())

def getExistingTables():
    try:
        existingTables = []
        data = DBCon.getAllTables()
        for measurement in data:
            existingTables.append({
                "measurement": measurement[0],
                "place": measurement[1],
                "distance": measurement[2],
                "user": measurement[3],
                "measure": measurement[4]
            })
        return existingTables
    except Exception as ex:
        logging.error("Data.getExistingTables(): " + str(ex) +
                      "\n" + traceback.format_exc())

def getTable(tablename):
    try:
        return DBCon.getTable(tablename)
    except Exception as ex:
        logging.error("Data.getTable(): " + str(ex) +
                      "\n" + traceback.format_exc())

