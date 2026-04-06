import datetime
import os
import pickle
import shutil
from pathlib import Path
#finocgio Erweiterung
from pymongo import MongoClient

from dotenv import load_dotenv
import pandas as pd
from azure.storage.blob import BlobServiceClient
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

ENV_STORAGE_KEY = "AZURE_STORAGE_CONNECTION_STRING"
MODEL_CONTAINER_PREFIX = "hikeplanner-model"
#finocgio Erweiterung
ENV_MONGO_KEY = "MONGO_DB_CONNECTION_STRING"

# init app, load model from storage
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path, override=True)
print("*** Load Model from Blob Storage ***")
if ENV_STORAGE_KEY in os.environ:
    azureStorageConnectionString = os.environ[ENV_STORAGE_KEY]
    blob_service_client = BlobServiceClient.from_connection_string(azureStorageConnectionString)

    containers = blob_service_client.list_containers(include_metadata=True)
    suffix = max(
        int(container.name.split("-")[-1])
        for container in containers
        if container.name.startswith(MODEL_CONTAINER_PREFIX)
    )
    model_folder = f"{MODEL_CONTAINER_PREFIX}-{suffix}"
    print(f"using version {model_folder}")
    
    container_client = blob_service_client.get_container_client(model_folder)
    blob_list = list(container_client.list_blobs())

    # Download all blobs to a clean local folder
    local_model_dir = Path("./model")
    if local_model_dir.exists():
        shutil.rmtree(local_model_dir)
    local_model_dir.mkdir(parents=True, exist_ok=True)
    for blob in blob_list:
        download_file_path = local_model_dir / blob.name
        print(f"downloading blob to {download_file_path.resolve()}")
        with open(file=download_file_path, mode="wb") as download_file:
            download_file.write(container_client.download_blob(blob.name).readall())

else:
    print("CANNOT ACCESS AZURE BLOB STORAGE - Please set AZURE_STORAGE_CONNECTION_STRING. Current env: ")
    print(os.environ)

gbr_model_path = Path(".", "model", "GradientBoostingRegressor.pkl")
with open(gbr_model_path, 'rb') as fid:
    gradient_model = pickle.load(fid)

linear_model_path = Path(".", "model", "LinearRegression.pkl")
with open(linear_model_path, 'rb') as fid:
    linear_model = pickle.load(fid)

#finocgio Erweiterung RF
rf_model_path = Path(".", "model", "RandomForestRegressor.pkl")
with open(rf_model_path, "rb") as fid:
    rf_model = pickle.load(fid)

def din33466(uphill, downhill, distance):
    km = distance / 1000.0
    vertical = downhill / 500.0 + uphill / 300.0
    horizontal = km / 4.0
    return 3600.0 * (min(vertical, horizontal) / 2 + max(vertical, horizontal))

def sac(uphill, downhill, distance):
    km = distance / 1000.0
    return 3600.0 * (uphill/400.0 + km /4.0)

def timedelta_minutes(seconds):
    rounded_minutes = int(round(seconds / 60.0))
    return str(datetime.timedelta(minutes=rounded_minutes))

#finocgio Erweiterung Funktion Hilfsfunktion
def to_hike_response(doc, score):
    return {
        "title": doc.get("title") or doc.get("name") or doc.get("gpx_filename") or "Unbekannte Wanderung",
        "length_3d": int(doc.get("length_3d", 0)),
        "uphill": int(doc.get("uphill", 0)),
        "downhill": int(doc.get("downhill", 0)),
        "moving_time": timedelta_minutes(doc.get("moving_time", 0)),
        "max_elevation": int(doc.get("max_elevation", 0)),
        "score": round(score, 2),
    }

#finocgio Erweiterung Funktion Suchfunktion
def find_similar_hikes(distance, uphill, downhill, limit=5):
    if mongo_collection is None:
        return []

    query = {
        "length_3d": {"$exists": True, "$ne": None},
        "uphill": {"$exists": True, "$ne": None},
        "downhill": {"$exists": True, "$ne": None},
        "moving_time": {"$exists": True, "$ne": None},
    }

    candidates = list(
        mongo_collection.find(
            query,
            {
                "title": 1,
                "name": 1,
                "gpx_filename": 1,
                "length_3d": 1,
                "uphill": 1,
                "downhill": 1,
                "moving_time": 1,
                "max_elevation": 1,
            },
        ).limit(1000)
    )

    hikes = []
    for doc in candidates:
        try:
            score = (
                abs(float(doc.get("length_3d", 0)) - distance)
                + abs(float(doc.get("uphill", 0)) - uphill) * 5
                + abs(float(doc.get("downhill", 0)) - downhill) * 5
            )
            hikes.append(to_hike_response(doc, score))
        except Exception:
            continue

    hikes.sort(key=lambda x: x["score"])
    return hikes[:limit]

print("\n*** Flask Backend ***")
app = Flask(__name__)
cors = CORS(app)
app = Flask(__name__, static_url_path='/', static_folder='../frontend/build')

@app.route("/")
def indexPage():
     return send_file("../frontend/build/index.html")  

@app.route("/api/predict")
def hello_world():
    downhill = request.args.get("downhill", default=0, type=int)
    uphill = request.args.get("uphill", default=0, type=int)
    length = request.args.get("length", default=0, type=int)

    demoinput = [[downhill, uphill, length, 0]]
    demodf = pd.DataFrame(
        columns=["downhill", "uphill", "length_3d", "max_elevation"],
        data=demoinput,
    )

    gradient_prediction = gradient_model.predict(demodf)[0]
    linear_prediction = linear_model.predict(demodf)[0]
    #finocgio Erweiterung RF Prediction
    rf_prediction = rf_model.predict(demodf)[0]

    # NEU
    similar_hikes = find_similar_hikes(length, uphill, downhill)
    print("DEBUG: neue predict-route aktiv")
    print("DEBUG similar_hikes count:", len(similar_hikes))

    return jsonify(
        {
            "time": timedelta_minutes(gradient_prediction),
            "linear": timedelta_minutes(linear_prediction),
            "random_forest": timedelta_minutes(rf_prediction),
            "din33466": timedelta_minutes(
                din33466(uphill=uphill, downhill=downhill, distance=length)
            ),
            "sac": timedelta_minutes(
                sac(uphill=uphill, downhill=downhill, distance=length)
            ),
            "similar_hikes": similar_hikes,
            "debug_test": "neu",
        }
    )

#finocgio Erweiterung
mongo_collection = None

if ENV_MONGO_KEY in os.environ:
    mongo_uri = os.environ[ENV_MONGO_KEY]
    mongo_client = MongoClient(mongo_uri)
    mongo_db = mongo_client["tracks"]
    mongo_collection = mongo_db["tracks"]
    print("*** MongoDB connection ready ***")
else:
    print("CANNOT ACCESS MONGODB - Please set MONGO_DB_CONNECTION_STRING.")