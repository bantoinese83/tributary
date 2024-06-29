import json
import redis
from flask import Flask, request, jsonify
from loguru import logger

app = Flask(__name__)

HISTORY_LENGTH = 10
DATA_KEY = "engine_temperature"


@app.route('/record', methods=['POST'])
def record_engine_temperature():
    payload = request.get_json(force=True)
    logger.info(f"(*) record request --- {json.dumps(payload)} (*)")

    engine_temperature = payload.get("engine_temperature")
    logger.info(f"engine temperature to record is: {engine_temperature}")

    database = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)
    database.lpush(DATA_KEY, engine_temperature)
    logger.info(f"stashed engine temperature in redis: {engine_temperature}")

    while database.llen(DATA_KEY) > HISTORY_LENGTH:
        database.rpop(DATA_KEY)
    engine_temperature_values = database.lrange(DATA_KEY, 0, -1)
    logger.info(f"engine temperature list now contains these values: {engine_temperature_values}")

    logger.info(f"record request successful")
    return {"success": True}, 200


@app.route('/collect', methods=['GET'])
def collect_engine_temperatures():
    database = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)
    engine_temperature_values = database.lrange(DATA_KEY, 0, -1)

    if not engine_temperature_values:
        return jsonify({"message": "No engine temperature data available"}), 200

    current_engine_temperature = float(engine_temperature_values[0])
    average_engine_temperature = sum(map(float, engine_temperature_values)) / len(engine_temperature_values)

    result = {
        "current_engine_temperature": current_engine_temperature,
        "average_engine_temperature": average_engine_temperature
    }

    logger.info(f"collect request successful: {result}")
    return jsonify(result), 200


# practically identical to the above
@app.route('/collect', methods=['POST'])
def collect_engine_temperature():
    return {"success": True}, 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
