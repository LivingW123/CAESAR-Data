import netCDF4
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta

nc_file = "RF02S.20240229.092740_182647.PNI.nc"
ds = netCDF4.Dataset(nc_file)

time_raw = ds.variables["Time"][:]
palt_raw = ds.variables["PALT"][:]

if hasattr(palt_raw, "filled"):
    palt = palt_raw.filled(np.nan)
else:
    palt = np.array(palt_raw, dtype=float)

if hasattr(time_raw, "filled"):
    time_sec = time_raw.filled(np.nan)
else:
    time_sec = np.array(time_raw, dtype=float)

ds.close()

base_date = datetime(2024, 2, 29)
timestamps = np.array([base_date + timedelta(seconds=float(s)) for s in time_sec])
spiral_range = (40414, 49099)   # vertical spiral
surface_range = (52000, 54000)  # near-surface horizontal leg

spiral_mask = (time_sec >= spiral_range[0]) & (time_sec <= spiral_range[1])
surface_mask = (time_sec >= surface_range[0]) & (time_sec <= surface_range[1])

fig, ax = plt.subplots(figsize=(14, 5))

ax.fill_between(timestamps, 0, palt, color="#d9d9d9", alpha=0.6, zorder=1)
ax.fill_between(timestamps, 0, palt, where=spiral_mask, color="#1565C0", alpha=0.45, label="Vertical spiral (40 414–49 099 s)", zorder=2)
ax.fill_between(timestamps, 0, palt, where=surface_mask, color="#C62828", alpha=0.50, label="Near-surface leg (52 000–54 000 s)", zorder=2)
ax.plot(timestamps, palt, color="#1a1a1a", linewidth=0.9, label="Flight track", zorder=3)

ax.set_xlabel("Time (UTC)", fontsize=12)
ax.set_ylabel("Altitude  PALT (m)", fontsize=12)
ax.set_title("RF02  ·  29 Feb 2024  —  Flight Curtain", fontsize=14, fontweight="bold")
ax.set_ylim(bottom=0)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
ax.xaxis.set_major_locator(mdates.AutoDateLocator())
fig.autofmt_xdate(rotation=0, ha="center")
ax.legend(loc="upper right", fontsize=10, framealpha=0.9)
ax.grid(True, linestyle="--", alpha=0.35)
ax.tick_params(labelsize=10)

plt.tight_layout()
plt.savefig("flight_track.png", dpi=200)
plt.show()
print("Saved → flight_track.png")
