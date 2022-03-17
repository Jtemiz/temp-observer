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
            dates={'minDate': DBCon.getMinMaxDate()['minDate'].strftime("%Y-%m-%d"), 'maxDate': DBCon.getMinMaxDate()['maxDate'].strftime("%Y-%m-%d")}
        )
    except Exception as ex:
        logging.error("Data.data(): " + str(ex) +
                      "\n" + traceback.format_exc())

@data_bp.route('/saveCSV', methods=['GET'])
def download_csv():
    try:
        dateFrom = request.args.get('from')
        dateTo = request.args.get('to')
        data = DBCon.getValuesFromTo(dateFrom, dateTo)
        output = io.StringIO()
        writer = csvPackage.writer(output)
        writer.writerow(['Abfragezeitraum:;%s;%s' % (dateFrom, dateTo)])
        writer.writerow(['Messpunkt-Anzahl:;%s' % str(len(data))])
        line = ['Zeit;System1;System2;System3;System4']
        writer.writerow(line)
        for row in data:
            line = [row[0].strftime("%d.%m.%Y, %H:%M:%S") + ';' + str(row[1]) + ';' + str(row[2] ) + ';' + str(row[3]) + ';' + str(row[4])]
            writer.writerow(line)
        output.seek(0)
        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-disposition":
                         "attachment; filename=" + dateFrom + "_" + dateTo})
    except Exception as ex:
        logging.error("Data.download_csv(): " + str(ex) +
                      "\n" + traceback.format_exc())

@data_bp.route('/searchValues', methods=['GET'])
def searchValues():
    try:
        dateFrom = request.args.get('from')
        dateTo = request.args.get('to')
        values = DBCon.getValuesFromTo(dateFrom, dateTo)
        metaData = {
            'dateFrom': dateFrom,
            'dateTo': dateTo,
            'dataSize': len(values)
        }
        return jsonify({
            'metaData': metaData,
            'values': values
        })
    except Exception as ex:
        logging.error("Data.getTable(): " + str(ex) +
                      "\n" + traceback.format_exc())

