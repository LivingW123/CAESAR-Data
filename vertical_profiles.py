import netCDF4
import numpy as np
import matplotlib.pyplot as plt

nc_file = "RF02S.20240229.092740_182647.PNI.nc"
ds = netCDF4.Dataset(nc_file)

time_sec = ds.variables["Time"][:]
palt = ds.variables["PALT"][:]
theta = ds.variables["THETA"][:]
vmr = ds.variables["VMR_VXL"][:]
dD_raw = ds.variables["dD_WVISO1"][:]

for arr_name in ["palt", "theta", "vmr", "dD_raw"]:
    arr = locals()[arr_name]
    if hasattr(arr, "filled"):
        locals()[arr_name] = arr.filled(np.nan)

palt = locals()["palt"]
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

# Compute q (g/kg) from VMR_VXL (ppmv)
q = vmr * (18.0 / 29.0) / 1000.0
spiral_mask = (time_sec >= 40414) & (time_sec <= 49099)

alt = palt[spiral_mask]
th = theta[spiral_mask]
qq = q[spiral_mask]
dd = dD[spiral_mask]
sort_idx = np.argsort(alt)
alt = alt[sort_idx]
th = th[sort_idx]
qq = qq[sort_idx]
dd = dd[sort_idx]

# Plot
fig, axes = plt.subplots(1, 3, figsize=(14, 6), sharey=True)
marker_kw = dict(s=8, alpha=0.6, edgecolors="none")
axes[0].scatter(th, alt, color="#1565C0", **marker_kw)
axes[0].set_xlabel("θ (K)", fontsize=12)
axes[0].set_ylabel("Altitude  PALT (m)", fontsize=12)
axes[0].set_title("Potential Temperature", fontsize=12, fontweight="bold")
axes[1].scatter(qq, alt, color="#2E7D32", **marker_kw)
axes[1].set_xlabel("q (g/kg)", fontsize=12)
axes[1].set_title("Specific Humidity", fontsize=12, fontweight="bold")
axes[2].scatter(dd, alt, color="#C62828", **marker_kw)
axes[2].set_xlabel("δD (‰)", fontsize=12)
axes[2].set_title("Isotope Ratio", fontsize=12, fontweight="bold")

for ax in axes:
    ax.grid(True, linestyle="--", alpha=0.35)
    ax.tick_params(labelsize=10)

fig.suptitle("RF02  ·  Vertical Profiles — Spiral Segment (40 414–49 099 s)", fontsize=14, fontweight="bold", y=1.01)

plt.tight_layout()
plt.savefig("vertical_profiles.png", dpi=200, bbox_inches="tight")
plt.show()
print("Saved → vertical_profiles.png")
