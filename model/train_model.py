import os
from pathlib import Path

from dotenv import load_dotenv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sn
from pymongo import MongoClient

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path, override=True)
mongo_uri = os.getenv("MONGO_DB_CONNECTION_STRING")
if not mongo_uri:
    raise SystemExit("Missing MongoDB URI. Set MONGO_DB_CONNECTION_STRING in .env or in the environment.")
mongo_db = "tracks"
mongo_collection = "tracks"

client = MongoClient(mongo_uri)
db = client[mongo_db]
collection = db[mongo_collection]

# fetch a single document
projection = {"gpx": 0, "url": 0, "bounds": 0, "name": 0}
track = collection.find_one(projection=projection)
if not track:
    raise SystemExit("No tracks found in MongoDB.")

print("\n*** Loading Tracks from MongoDB ***")
chunks = []
batch = []
chunk_size = 2000
cursor = collection.find(projection=projection)
total_loaded = 0
for idx, doc in enumerate(cursor, start=1):
    batch.append(doc)
    total_loaded = idx
    if idx % chunk_size == 0:
        chunks.append(pd.DataFrame(batch))
        print(f"Loaded {idx} tracks...")
        batch.clear()
if batch:
    chunks.append(pd.DataFrame(batch))
    print(f"Loaded {total_loaded} tracks...")

df = pd.concat(chunks, ignore_index=True).set_index("_id")

df['avg_speed'] = df['length_3d']/df['moving_time']
df['difficulty_num'] = df['difficulty'].map(lambda x: int(x[1])).astype('int32')

# drop na values
df.dropna()
df = df[df['avg_speed'] < 2] # an avg of > 2m/s is probably not a hiking activity
df = df[df['min_elevation'] > 0]
df = df[df['length_2d'] < 100000]
print(f"{len(df)} tracks processed.")

corr = df.corr(numeric_only=True)

print("\n*** Correlation Matrix ***")
print(corr)
plt.figure(figsize=(10, 8))
sn.heatmap(corr, annot=True, fmt=".2f", annot_kws={"size": 7})
static_dir = Path(__file__).resolve().parent.parent / "frontend" / "static" / "images"
static_dir.mkdir(parents=True, exist_ok=True)
plt.tight_layout()
plt.savefig(static_dir / "heatmap.png", dpi=150)
plt.close()

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import Normalizer
#finocgio Erweiterung Bonusthema Model/Training
from sklearn.ensemble import RandomForestRegressor

y = df.reset_index()['moving_time']
x = df.reset_index()[['downhill', 'uphill', 'length_3d', 'max_elevation']]

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.20, random_state=42)

# Baseline Linear Regression
# Model training
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
import datetime
import pickle

y = df.reset_index()["moving_time"]
x = df.reset_index()[["downhill", "uphill", "length_3d", "max_elevation"]]

x_train, x_test, y_train, y_test = train_test_split(
    x, y, test_size=0.20, random_state=42
)

# Linear Regression
lr = LinearRegression()
lr.fit(x_train, y_train)
y_pred_lr = lr.predict(x_test)
lr_r2 = r2_score(y_test, y_pred_lr)
lr_mse = mean_squared_error(y_test, y_pred_lr)

# Gradient Boosting Regressor
gbr = GradientBoostingRegressor(n_estimators=50, random_state=9000)
gbr.fit(x_train, y_train)
y_pred_gbr = gbr.predict(x_test)
gbr_r2 = r2_score(y_test, y_pred_gbr)
gbr_mse = mean_squared_error(y_test, y_pred_gbr)

# Random Forest Regressor
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(x_train, y_train)
y_pred_rf = rf_model.predict(x_test)
rf_r2 = r2_score(y_test, y_pred_rf)
rf_mse = mean_squared_error(y_test, y_pred_rf)

print("\n*** Models ***")
print(f"{'Model':<30} {'R2':>10} {'MSE':>14}")
print("-" * 56)
print(f"{'Linear Regression':<30} {lr_r2:>10.4f} {lr_mse:>14.2f}")
print(f"{'Gradient Boosting Regressor':<30} {gbr_r2:>10.4f} {gbr_mse:>14.2f}")
print(f"{'Random Forest Regressor':<30} {rf_r2:>10.4f} {rf_mse:>14.2f}")


def din33466(uphill, downhill, distance):
    km = distance / 1000.0
    vertical = downhill / 500.0 + uphill / 300.0
    horizontal = km / 4.0
    return 3600.0 * (min(vertical, horizontal) / 2 + max(vertical, horizontal))


def sac(uphill, distance):
    km = distance / 1000.0
    return 3600.0 * (uphill / 400.0 + km / 4.0)


print("\n*** Sample Values ***")
samples = [
    {"downhill": 300, "uphill": 700, "length_3d": 10000, "max_elevation": 1200},
    {"downhill": 600, "uphill": 900, "length_3d": 15000, "max_elevation": 2100},
    {"downhill": 200, "uphill": 400, "length_3d": 7000, "max_elevation": 1400},
    {"downhill": 1200, "uphill": 1300, "length_3d": 22000, "max_elevation": 2800},
    {"downhill": 100, "uphill": 250, "length_3d": 5000, "max_elevation": 1100},
]

print(
    f"{'downhill':>8}  {'uphill':>6}  {'length_3d':>9}  {'max_elev':>8}  "
    f"{'DIN33466':>8}  {'SAC':>8}  {'Linear':>8}  {'Gradient':>8}  {'RF':>8}"
)

for sample in samples:
    demodf = pd.DataFrame(
        [sample],
        columns=["downhill", "uphill", "length_3d", "max_elevation"],
    )

    time_lr = lr.predict(demodf)[0]
    time_gbr = gbr.predict(demodf)[0]
    time_rf = rf_model.predict(demodf)[0]

    din = datetime.timedelta(
        seconds=din33466(
            sample["uphill"], sample["downhill"], sample["length_3d"]
        )
    )
    sac_time = datetime.timedelta(seconds=sac(sample["uphill"], sample["length_3d"]))

    din_str = str(din).rsplit(":", 1)[0]
    sac_str = str(sac_time).rsplit(":", 1)[0]
    lr_str = str(datetime.timedelta(seconds=time_lr)).rsplit(":", 1)[0]
    gbr_str = str(datetime.timedelta(seconds=time_gbr)).rsplit(":", 1)[0]
    rf_str = str(datetime.timedelta(seconds=time_rf)).rsplit(":", 1)[0]

    print(
        f"{sample['downhill']:>8}  {sample['uphill']:>6}  "
        f"{sample['length_3d']:>9}  {sample['max_elevation']:>8}  "
        f"{din_str:>8}  {sac_str:>8}  {lr_str:>8}  {gbr_str:>8}  {rf_str:>8}"
    )

# Save models
with open("GradientBoostingRegressor.pkl", "wb") as f:
    pickle.dump(gbr, f)

with open("LinearRegression.pkl", "wb") as f:
    pickle.dump(lr, f)

with open("RandomForestRegressor.pkl", "wb") as f:
    pickle.dump(rf_model, f)