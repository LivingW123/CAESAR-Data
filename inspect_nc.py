import netCDF4
import numpy as np
import json

ds = netCDF4.Dataset("RF02S.20240229.092740_182647.PNI.nc")

result = {}

# Dimensions
result["dimensions"] = {k: v.size for k, v in ds.dimensions.items()}

# Variables of interest
vars_of_interest = ["Time", "PALT", "GGLON", "GGLAT", "THETA", "VMR_VXL", "dD_WVISO1"]
var_info = {}
for v in vars_of_interest:
    if v in ds.variables:
        var = ds[v]
        data = var[:]
        if hasattr(data, 'compressed'):
            data_clean = data.compressed()
        else:
            data_clean = data[~np.isnan(data)]
        info = {
            "shape": list(var.shape),
            "units": getattr(var, "units", "N/A"),
            "long_name": getattr(var, "long_name", "N/A"),
        }
        if len(data_clean) > 0:
            info["min"] = float(np.min(data_clean))
            info["max"] = float(np.max(data_clean))
        else:
            info["all_nan"] = True
        var_info[v] = info
    else:
        var_info[v] = "NOT FOUND"

result["variables"] = var_info

# Time & segments
time_data = ds["Time"][:]
result["time_range"] = {"min": float(np.min(time_data)), "max": float(np.max(time_data))}

mask_spiral = (time_data >= 40414) & (time_data <= 49099)
mask_horiz = (time_data >= 52000) & (time_data <= 54000)
result["spiral_points"] = int(np.sum(mask_spiral))
result["horiz_points"] = int(np.sum(mask_horiz))

palt = ds["PALT"][:]
if hasattr(palt, 'filled'):
    palt_np = palt.filled(np.nan)
else:
    palt_np = np.array(palt, dtype=float)

result["palt_spiral"] = {"min": float(np.nanmin(palt_np[mask_spiral])), "max": float(np.nanmax(palt_np[mask_spiral]))}
result["palt_horiz"] = {"min": float(np.nanmin(palt_np[mask_horiz])), "max": float(np.nanmax(palt_np[mask_horiz]))}

ds.close()

with open("inspect_result.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)

print("DONE")
