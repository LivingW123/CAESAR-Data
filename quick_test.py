import netCDF4
import pandas as pd
import numpy as np
from datetime import datetime

def load_first_n_lines(nc_path, n=5):
    """
    Demonstrates loading only the first N rows for rapid testing
    without reading the entire 1.4GB file.
    """
    print(f"Opening {nc_path} for quick test (first {n} rows)...")
    ds = netCDF4.Dataset(nc_path)
    vars_to_load = ["Time", "PALT", "GGLON", "GGLAT", "THETA", "VMR_VXL", "dD_WVISO1"]
    data = {}
    
    for v in vars_to_load:
        if v in ds.variables:
            val = ds.variables[v][:n]
            if hasattr(val, 'filled'):
                val = val.filled(np.nan)
            if val.ndim == 2:
                val = val[:, 0]
            data[v] = val
    
    if "VMR_VXL" in data:
        data["q"] = data["VMR_VXL"] * (18.0 / 29.0) / 1000.0
        
    if "Time" in data:
        base_date = datetime(2024, 2, 29) # Fallback date
        data["Timestamp"] = pd.to_datetime(base_date) + pd.to_timedelta(data["Time"], unit='s')

    df = pd.DataFrame(data)
    ds.close()
    return df

if __name__ == "__main__":
    nc_file = "RF02S.20240229.092740_182647.PNI.nc"
    output_csv = "quick_test_output.csv"
    
    df_test = load_first_n_lines(nc_file, 5)
    
    df_test.to_csv(output_csv, index=False)
    print(f"Results saved to {output_csv}")
    print(df_test)
