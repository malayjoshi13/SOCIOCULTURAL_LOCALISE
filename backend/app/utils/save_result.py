import datetime
import json
import os

os.makedirs("save_debugging_results", exist_ok=True)

def saving_result(path_to_save_at, result_to_save):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"save_debugging_results/{path_to_save_at}_{timestamp}.json", "w") as f:
        json.dump(result_to_save, f, indent=4)