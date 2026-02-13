import netCDF4
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def load_and_preprocess(nc_path):
    """
    Loads all vars:
    - Extracts GGLON, GGLAT, dD_WVISO1
    - Convert VMR_VXL (ppmv) to moisture ratio q (g/kg)
    - Convert Time (seconds since midnight) to datetime objects
    """
    print(f"Opening {nc_path}...")
    ds = netCDF4.Dataset(nc_path)
    
    # vars to dictionary
    data = {}
    total_vars = len(ds.variables)
    for i, var_name in enumerate(ds.variables):
        if i % 50 == 0:
            print(f"Loading variables: {i}/{total_vars}...")
        var = ds.variables[var_name]
        val = var[:]
        if hasattr(val, 'filled'):
            val = val.filled(np.nan)
        data[var_name] = val

    # 2d vars
    sub_1hz_vars = ["GGLON", "GGLAT", "dD_WVISO1"]
    for v in sub_1hz_vars:
        if v in data and data[v].ndim == 2:
            print(f"Extracting 1Hz column for {v} (shape: {data[v].shape})")
            data[v] = data[v][:, 0]

    # moisture ratio conversion
    if "VMR_VXL" in data:
        print("Converting VMR_VXL to moisture ratio q (g/kg)...")
        data["q"] = data["VMR_VXL"] * (18.0 / 29.0) / 1000.0

    # time conversion
    if "Time" in data:
        print("Converting Time to datetime objects...")
        time_unit = getattr(ds.variables["Time"], "units", "")
        if "since" in time_unit:
            try:
                date_str = time_unit.split("since ")[1].split(" ")[0]
                base_date = datetime.strptime(date_str, "%Y-%m-%d")
            except Exception:
                base_date = datetime(2024, 2, 29)
        else:
            base_date = datetime(2024, 2, 29)
        data["Timestamp"] = pd.to_datetime(base_date) + pd.to_timedelta(data["Time"], unit='s')

    ds.close()
    
    df_main = pd.DataFrame({
        "Timestamp": data.get("Timestamp"),
        "Time_sec": data.get("Time"),
        "PALT": data.get("PALT"),
        "GGLON": data.get("GGLON"),
        "GGLAT": data.get("GGLAT"),
        "THETA": data.get("THETA"),
        "VMR_VXL": data.get("VMR_VXL"),
        "q": data.get("q"),
        "dD_WVISO1": data.get("dD_WVISO1")
    })
    
    return data, df_main

if __name__ == "__main__":
    nc_file = "RF02S.20240229.092740_182647.PNI.nc"
    data, df = load_and_preprocess(nc_file)
    print("\nPreprocessed Data Summary:")
    print(df.head())
    print(f"\nTotal Records: {len(df)}")
    print(f"Data Loaded: {list(data.keys())[:10]} ... (+{len(data)-10} more)")
