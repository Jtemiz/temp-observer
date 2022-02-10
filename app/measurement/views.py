import logging, traceback, time, json
from datetime import datetime
from flask import Blueprint, render_template, url_for, flash, Response, jsonify, request
from app.globals import VALUES, MEASUREMENT_IS_ACTIVE, PAUSE_IS_ACTIVE, TABLENAME, IS_LISTING
import app.backend.db_connection as DBCon
import app.backend.sps_connection as SPS_Con

measurement_bp = Blueprint('measurement_bp', __name__, template_folder='pages')

METADATA_MEASURE = 'Nicht angegeben'
METADATA_USER = 'Nicht angegeben'
METADATA_LOCATION = 'Nicht angegeben'
METADATA_DISTANCE = ''


@measurement_bp.route('/')
def chart():
    try:
        SPS_Con.startReset_Arduino()
        return render_template(
            'chart.html',
            title="Messung",
            measurementActive=MEASUREMENT_IS_ACTIVE
        )
    except Exception as ex:
        logging.error("Measurement.chart(): " + str(ex) +
                      "\n" + traceback.format_exc())


# Methods for Chart
@measurement_bp.route('/toggleMeasuring')
def toggleMeasuring():
    try:
        if MEASUREMENT_IS_ACTIVE == False:
            startMeasuring()
        else:
            stopMeasuring()
        return jsonify(MEASUREMENT_IS_ACTIVE)
    except Exception as ex:
        logging.error("Measurement.toggleMeasuring(): " + str(ex) +
                      "\n" + traceback.format_exc())




@measurement_bp.route('/setMeasurementDistance', methods=['POST'])
def getMeasurementDistance():
    try:
        global METADATA_DISTANCE
        METADATA_DISTANCE = request.form['distance']
        return 'valid'
    except Exception as ex:
        logging.error("Measurement.getMeasurementDistance(): " + str(ex) +
                      "\n" + traceback.format_exc())


@measurement_bp.route('/metaDataInput', methods=['POST'])
def handleMetaDataInput():
    try:
        global METADATA_USER
        global METADATA_LOCATION
        global METADATA_MEASURE
        METADATA_USER = request.form['user']
        METADATA_LOCATION = request.form['location']
        SPS_Con.STREED_WIDTH = request.form['width']
        METADATA_MEASURE = request.form['measure']
        return 'valid'
    except Exception as ex:
        logging.error("Measurement.handleMetaDataInput(): " + str(ex) +
                      "\n" + traceback.format_exc())


@measurement_bp.route('/isMActive')
def isMActive():
    try:
        return jsonify(MEASUREMENT_IS_ACTIVE)
    except Exception as ex:
        logging.error("Measurement.isMActive(): " + str(ex) +
                      "\n" + traceback.format_exc())


@measurement_bp.route('/isPActive')
def isPActive():
    try:
        return jsonify(PAUSE_IS_ACTIVE)
    except Exception as ex:
        logging.error("Measurement.isPActive(): " + str(ex) +
                      "\n" + traceback.format_exc())


@measurement_bp.route('/chart-data', methods=['GET'])
def chart_data():
    try:
        for idx, entry in enumerate(DBCon.getLatestValues(20)):
            data = {
                "index": idx,
                "time": str(entry[0]),
                "temp1": entry[1],
                "temp2": entry[2],
                "temp3": entry[3],
                "temp4": entry[4]
            }
            VALUES.append(data)
        return Response(getMeasurementValues(), mimetype="text/event-stream")
    except Exception as ex:
        logging.error("Measurement.chart_data(): " + str(ex) +
                      "\n" + traceback.format_exc())


@measurement_bp.route('/changeLimitVal', methods=['POST'])
def changeLimitVal():
    try:
        lim = request.form['limVal']
        SPS_Con.LIMIT_VALUE = lim
        return 'valid'
    except Exception as ex:
        logging.error("Measurement.changeLimitVal(): " + str(ex) +
                      "\n" + traceback.format_exc())


@measurement_bp.route('/addComment', methods=['POST'])
def addComment():
    try:
        com = request.form['comment']
        pos = request.form['position']
        pos = float(pos[:-2])
        DBCon.insertComment(TABLENAME, com, pos)
        flash("Kommentar wurde gesetzt bei ")
        return 'valid'
    except Exception as ex:
        logging.error("Measurement.addComment(): " + str(ex) +
                      "\n" + traceback.format_exc())


def getMeasurementValues():
    while True:
        if len(VALUES) != 0:
            try:
                print("Data sended")
                tmp = VALUES
                data = json.dumps(tmp)
                del VALUES[:len(tmp)]
                yield f"data: {data}\n\n"
                time.sleep(1.)
            except Exception as ex:
                logging.error("routes.getMeasurementValues(): " + str(ex) +
                              "\n" + traceback.format_exc())


def startMeasuring():
    try:
        global TABLENAME
        global PAUSE_IS_ACTIVE
        global MEASUREMENT_IS_ACTIVE
        PAUSE_IS_ACTIVE = False
        MEASUREMENT_IS_ACTIVE = True
        now = datetime.now()
        TABLENAME = now.strftime("%Y%m%d%H%M%S")
        print(TABLENAME)
        print(PAUSE_IS_ACTIVE)
        print(MEASUREMENT_IS_ACTIVE)
        DBCon.createTable(TABLENAME)
        SPS_Con.startReset_Arduino()
    except Exception as ex:
        logging.error("Measurement.startMeasuring(): " + str(ex) +
                      "\n" + traceback.format_exc())


def stopMeasuring():
    try:
        global PAUSE_IS_ACTIVE
        global MEASUREMENT_IS_ACTIVE
        MEASUREMENT_IS_ACTIVE = False
        PAUSE_IS_ACTIVE = False
        SPS_Con.stop_Arduino()
        DBCon.insertTable(TABLENAME)
        DBCon.insertMetadata(TABLENAME, METADATA_LOCATION, METADATA_DISTANCE, METADATA_USER, METADATA_MEASURE)
    except Exception as ex:
        logging.error("Measurement.stopMeasuring(): " + str(ex) +
                      "\n" + traceback.format_exc())

def stopConnection():
    try:
        SPS_Con.SUDPServer.stop_server()
        IS_LISTING = False
    except Exception as ex:
        logging.error("Measurement.stopConnection(): " + str(ex) +
                      "\n" + traceback.format_exc())


def initConnection():
    try:
        SPS_Con.SUDPServer.start_server()
        IS_LISTING = True
    except Exception as ex:
        logging.error("Measurement.initConnections(): " + str(ex) +
                      "\n" + traceback.format_exc())
