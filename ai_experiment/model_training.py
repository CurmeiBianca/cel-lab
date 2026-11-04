import csv
import math
from pathlib import Path


DEFAULT_DATASET = Path(__file__).resolve().parents[1] / "data" / "datasets" / "cell_activity.csv"
FEATURE_COLUMNS = ["generation", "total_cells", "active_cells", "inactive_cells",
                   "active_density", "changed_cells", "rows", "columns"]
TARGET_COLUMN = "target_active_cells_next"


def train_model(dataset_path=DEFAULT_DATASET, model_path=None, test_size=0.2):
    """Antrenează un RandomForest și evaluează-l; întoarce status explicativ fără date suficiente."""
    path = Path(dataset_path)
    if not path.exists():
        return {"trained": False, "message": f"Datasetul nu există: {path}"}
    with path.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    if len(rows) < 5:
        return {"trained": False, "message": f"Sunt necesare cel puțin 5 tranziții; găsite: {len(rows)}."}
    try:
        import numpy as np
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.metrics import mean_absolute_error, mean_squared_error
        from sklearn.model_selection import GroupShuffleSplit, train_test_split
        import joblib
    except ImportError as error:
        return {"trained": False, "message": f"Lipsește o dependență ML: {error}"}

    x = np.asarray([[float(row[column]) for column in FEATURE_COLUMNS] for row in rows])
    y = np.asarray([float(row[TARGET_COLUMN]) for row in rows])
    groups = np.asarray([row.get("simulation_id", "") for row in rows])
    if len(set(groups)) >= 2:
        splitter = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=42)
        train, test = next(splitter.split(x, y, groups))
    else:
        train, test = train_test_split(np.arange(len(rows)), test_size=test_size, random_state=42)
    if len(train) < 2 or len(test) < 1:
        return {"trained": False, "message": "Nu sunt suficiente simulări pentru separarea antrenare/test."}
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(x[train], y[train])
    predictions = model.predict(x[test])
    result = {"trained": True, "rows": len(rows),
              "mae": float(mean_absolute_error(y[test], predictions)),
              "rmse": float(math.sqrt(mean_squared_error(y[test], predictions))),
              "train_size": len(train), "test_size": len(test)}
    if model_path is not None:
        destination = Path(model_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, destination)
        result["model_path"] = str(destination)
    return result


if __name__ == "__main__":
    result = train_model()
    if result["trained"]:
        print(f"Model antrenat pe {result['rows']} tranziții; MAE={result['mae']:.3f}, RMSE={result['rmse']:.3f}.")
    else:
        print(result["message"])
