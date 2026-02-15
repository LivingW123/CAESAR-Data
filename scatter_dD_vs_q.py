import netCDF4
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

nc_file = "RF02S.20240229.092740_182647.PNI.nc"
ds = netCDF4.Dataset(nc_file)

def to_array(var):
    arr = var[:]
    return arr.filled(np.nan) if hasattr(arr, "filled") else np.array(arr, dtype=float)

time_sec = to_array(ds.variables["Time"])
vmr = to_array(ds.variables["VMR_VXL"])
dD_raw = to_array(ds.variables["dD_WVISO1"])

ds.close()

dD = dD_raw[:, 0] if dD_raw.ndim == 2 else dD_raw
q = vmr * (18.0 / 29.0)

# Horizontal leg mask
leg_mask = (time_sec >= 52000) & (time_sec <= 54000)
qq = q[leg_mask]
dd = dD[leg_mask]
valid = np.isfinite(qq) & np.isfinite(dd)
qq_valid = qq[valid]
dd_valid = dd[valid]

# Linear regression
slope, intercept, r_value, p_value, std_err = stats.linregress(qq_valid, dd_valid)
fit_x = np.linspace(np.nanmin(qq_valid), np.nanmax(qq_valid), 200)
fit_y = slope * fit_x + intercept

# Plot
fig, ax = plt.subplots(figsize=(8, 6))
ax.scatter(qq_valid, dd_valid, s=10, alpha=0.5, color="#1565C0", edgecolors="none", label="Data")
ax.plot(fit_x, fit_y, color="#C62828", linewidth=2, label="Linear fit")
annotation = (f"r = {r_value:.2f}\n" f"p = {p_value:.2e}\n" f"slope = {slope:.2f} ‰/(g/kg)")
ax.annotate(annotation, xy=(0.05, 0.95), xycoords="axes fraction", fontsize=11, verticalalignment="top", bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor="#aaa", alpha=0.9))
ax.set_xlabel("q (g/kg)", fontsize=12)
ax.set_ylabel("δD (‰)", fontsize=12)
ax.set_title("RF02  ·  δD vs q — Near-Surface Leg (52 000–54 000 s)", fontsize=14, fontweight="bold")
ax.legend(loc="lower right", fontsize=10, framealpha=0.9)
ax.grid(True, linestyle="--", alpha=0.35)
ax.tick_params(labelsize=10)
plt.tight_layout()
plt.savefig("scatter_dD_vs_q.png", dpi=200)
plt.show()
print("Saved → scatter_dD_vs_q.png")
