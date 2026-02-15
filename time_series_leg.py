import netCDF4
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta

nc_file = "RF02S.20240229.092740_182647.PNI.nc"
ds = netCDF4.Dataset(nc_file)

time_sec = ds.variables["Time"][:]
theta = ds.variables["THETA"][:]
vmr = ds.variables["VMR_VXL"][:]
dD_raw = ds.variables["dD_WVISO1"][:]

for arr_name in ["theta", "vmr", "dD_raw"]:
    arr = locals()[arr_name]
    if hasattr(arr, "filled"):
        locals()[arr_name] = arr.filled(np.nan)

theta = locals()["theta"]
vmr = locals()["vmr"]
dD_raw = locals()["dD_raw"]

if dD_raw.ndim == 2:
    dD = dD_raw[:, 0]
else:
    dD = dD_raw

if hasattr(time_sec, "filled"):
    time_sec = time_sec.filled(np.nan)

ds.close()

q = vmr * (18.0 / 29.0) / 1000.0
base_date = datetime(2024, 2, 29)
timestamps = np.array([base_date + timedelta(seconds=float(s)) for s in time_sec])

# Horizontal leg mask
leg_mask = (time_sec >= 52000) & (time_sec <= 54000)
t = timestamps[leg_mask]
th = theta[leg_mask]
qq = q[leg_mask]
dd = dD[leg_mask]

# Plot
fig, axes = plt.subplots(3, 1, figsize=(14, 8), sharex=True)
axes[0].plot(t, th, color="#1565C0", linewidth=0.9)
axes[0].set_ylabel("θ (K)", fontsize=12)
axes[0].set_title("Potential Temperature", fontsize=12, fontweight="bold")
axes[1].plot(t, qq, color="#2E7D32", linewidth=0.9)
axes[1].set_ylabel("q (g/kg)", fontsize=12)
axes[1].set_title("Specific Humidity", fontsize=12, fontweight="bold")
axes[2].plot(t, dd, color="#C62828", linewidth=0.9)
axes[2].set_ylabel("δD (‰)", fontsize=12)
axes[2].set_xlabel("Time (UTC)", fontsize=12)
axes[2].set_title("Isotope Ratio", fontsize=12, fontweight="bold")
axes[2].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
axes[2].xaxis.set_major_locator(mdates.AutoDateLocator())

for ax in axes:
    ax.grid(True, linestyle="--", alpha=0.35)
    ax.tick_params(labelsize=10)

fig.suptitle("RF02  ·  Time Series — Near-Surface Leg (52 000–54 000 s)", fontsize=14, fontweight="bold", y=1.01)

plt.tight_layout()
plt.savefig("time_series_leg.png", dpi=200, bbox_inches="tight")
plt.show()
print("Saved → time_series_leg.png")
