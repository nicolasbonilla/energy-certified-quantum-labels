# real_data / checks / emulation_vs_published_energy.py   (coordinator, 2026-11-13; descriptive, post hoc, no rule)
#
# Energy error per site of the stored emulated first-stage states (method run, primary variant) over the PUBLISHED
# energy error per site of the dataset at the same coupling and size. Replaces, for the text of Sec. IV B, the same
# ratio against the energies read from the figures (learning_ibm/out/descriptive.json, energy_ratio_57).
# Reads only stored outputs:
#   phase3/full_runs/method/laptop_post/out/emu/emu_n<n>_J<Jz>.json   var.primary.dE_site
#   phase3/full_runs/real_data/out/map_rows.json                       rows[n, Jz, label = m_s].de_real
# Writes emulation_vs_published_energy.json next to this file.
#   python -B -I emulation_vs_published_energy.py
import glob
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
RD = os.path.abspath(os.path.join(HERE, ".."))
RUNS = os.path.abspath(os.path.join(RD, ".."))

rows = json.load(open(os.path.join(RD, "out", "map_rows.json")))["rows"]
pub = {(r["n"], round(float(r["Jz"]), 1)): float(r["de_real"]) for r in rows if r["label"] == "m_s" and r.get("de_real") is not None}

out = {"what": "energy error per site of the emulated first stage (primary variant) over the published energy error "
               "per site of the dataset, same coupling and size; descriptive, post hoc (coordinator, 2026-11-13)",
       "sources": ["phase3/full_runs/method/laptop_post/out/emu/emu_n<n>_J<Jz>.json: var.primary.dE_site",
                   "phase3/full_runs/real_data/out/map_rows.json: rows[label = m_s].de_real"],
       "sizes": {}}
for n in (57, 115):
    items = []
    for path in sorted(glob.glob(os.path.join(RUNS, "method", "laptop_post", "out", "emu", "emu_n%d_J*.json" % n))):
        J = round(float(re.search(r"_J([0-9.]+)\.json$", path).group(1)), 1)
        d = json.load(open(path))
        try:
            de_emu = float(d["var"]["primary"]["dE_site"])
        except (KeyError, TypeError):
            continue
        if (n, J) not in pub:
            continue
        items.append({"Jz": J, "de_emulated": de_emu, "de_published": pub[(n, J)], "ratio": de_emu / pub[(n, J)]})
    items.sort(key=lambda x: x["Jz"])
    ratios = [x["ratio"] for x in items]
    out["sizes"][str(n)] = {"rows": items, "n_couplings": len(items), "ratio_min": min(ratios), "ratio_max": max(ratios),
                            "ratio_min_at": items[ratios.index(min(ratios))]["Jz"], "ratio_max_at": items[ratios.index(max(ratios))]["Jz"]}
    print("n = %d: %d couplings" % (n, len(items)))
    for x in items:
        print("   Jz = %.1f  emulated %.6f  published %.6f  ratio %.4f" % (x["Jz"], x["de_emulated"], x["de_published"], x["ratio"]))
    print("   ratio from %.4f (Jz = %.1f) to %.4f (Jz = %.1f)" % (min(ratios), out["sizes"][str(n)]["ratio_min_at"], max(ratios), out["sizes"][str(n)]["ratio_max_at"]))
with open(os.path.join(HERE, "emulation_vs_published_energy.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(out, f, indent=1)
