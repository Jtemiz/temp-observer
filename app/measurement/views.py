import logging, traceback, time, json
from flask import Blueprint, render_template, url_for, flash, Response
from app.globals import VALUES, MEASUREMENT_IS_ACTIVE
import app.globals as glob
import app.backend.db_connection as DBCon
import app.backend.sps_connection as SPS_Con

measurement_bp = Blueprint('measurement_bp', __name__, template_folder='pages')


@measurement_bp.route('/')
def chart():
    try:
        generateToastr()
        return render_template(
            'chart.html',
            title="Messung",
            measurementActive=MEASUREMENT_IS_ACTIVE
        )
    except Exception as ex:
        logging.error("Measurement.chart(): " + str(ex) +
                      "\n" + traceback.format_exc())


@measurement_bp.route('/chart-data', methods=['GET'])
def chart_data():
    amount = 20
    lastVals = DBCon.getLatestValues(amount)
    try:
        if len(lastVals) != 0:
            for i in range(amount-1, -1, -1):
                data = {
                    "index": i,
                    "time": lastVals[i][0],
                    "temp1": lastVals[i][1],
                    "temp2": lastVals[i][2],
                    "temp3": lastVals[i][3],
                    "temp4": lastVals[i][4]
                }
                VALUES.append(data)
        return Response(getMeasurementValues(), mimetype="text/event-stream")
    except Exception as ex:
        logging.error("Measurement.chart_data(): " + str(ex) +
                      "\n" + traceback.format_exc())


def getMeasurementValues():
    while True:
        if len(VALUES) != 0:
            try:
                tmp = VALUES
                data = json.dumps(tmp, default=str)
                del VALUES[:len(tmp)]
                yield f"data: {data}\n\n"
                time.sleep(1.)
            except Exception as ex:
                logging.error("Measurement.getMeasurementValues(): " + str(ex) +
                              "\n" + traceback.format_exc())


def stopConnection(sig, frame):
    try:
        SPS_Con.SUDPServer.stop_server()
    except Exception as ex:
        logging.error("Measurement.stopConnection(): " + str(ex) +
                      "\n" + traceback.format_exc())


def initConnection():
    try:
        SPS_Con.SUDPServer.start_server()
    except Exception as ex:
        logging.error("Measurement.initConnections(): " + str(ex) +
                      "\n" + traceback.format_exc())


def generateToastr():
    if glob.WARN_LEVEL == 3:
        flash("Schwerwiegender Fehler liegt vor. Weitere Aufzeichnungen nicht möglich.", 'error')
    elif glob.WARN_LEVEL == 2:
        flash("Kritischer Fehler liegt vor. Bitte zeitnah Verbindung mit Service aufnehmen. Die Aufzeichnung wird "
              "fortgesetzt.", 'warning')
    elif glob.WARN_LEVEL == 1:
        flash("Es wurde ein Fehler entdeckt. Bitte zeitnah Verbindung mit Service aufnehmen. Die Aufzeichnung wird "
              "fortgesetzt.")
