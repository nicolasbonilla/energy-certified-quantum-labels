# real_data / checks / g6_supplement.py   (own code of the task rd-map; 2026-11-12; written AFTER the hash; POST HOC)
#
# Supplement to gate G6 (first part). The declared selection of G6 (NOT CERTIFIED rows within 0.3 of a J*, and ten rows
# drawn with the seed) contains no component whose tensors are on the laptop, so the declared first part checked
# nothing (NOT COMPLETE, DECLARATION.md Sec. 12 line 16). This script does NOT replace the gate. It answers a narrower
# question with what is on the laptop: for the stored states whose tensors ARE here (map/npz_20261030T022613Z,
# n = 57, Jz = 1.6), does the energy recomputed from the tensors at a neighbouring coupling agree with the linear rule
#     E_phi(J) = E_phi(J_g) + (J - J_g) (1/4) sum_e <Z_i Z_j>_phi      (DECLARATION.md Sec. 0)?
# Part A: every component of every NOT CERTIFIED row of out/map_rows.json whose tensors are on the laptop, at the
#         row's coupling (function g6_linear of the sealed code, unchanged, applied to all NOT CERTIFIED rows).
# Part B: every state with tensors on the laptop, at Jz = 1.5 and 1.7 (the two couplings where states stored at 1.6
#         are re-evaluated), whether or not it is a witness component.
# It reads the sealed outputs and the stored objects only; nothing of converted/ is opened.
#
#   python -B -I g6_supplement.py        (writes g6_supplement.json next to itself)
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
RD = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(RD, "code"))

import map_common as C      # noqa: E402
import map_gates as MG      # noqa: E402
import map_stored as MS     # noqa: E402


def main():
    C.declaration_guard()
    stored = MS.Stored()
    rows = C.rj(os.path.join(RD, "out", "map_rows.json"))["rows"]
    nc = [r for r in rows if r["status"] == "NOT_CERTIFIED"]
    npz_root = os.path.join(C.MAPRUN, "npz_20261030T022613Z")
    here = sorted(sid for sid, s in stored.D.states.items()
                  if s.get("npz") and os.path.exists(os.path.join(npz_root, *s["npz"].split("/"))))
    print("stored states with tensors on the laptop: %d" % len(here))
    for sid in here:
        s = stored.D.states[sid]
        print("   %s  n = %s  Jz = %s  E = %.9f  slope = %.9f" % (sid, s["n"], s["Jz"], s["tenpy"]["E"], stored.slope(sid)))
    a = MG.g6_linear(stored, nc)
    print("Part A: NOT CERTIFIED rows %d; components checked %d; components without tensors %d; max |dE| = %s; all within 1e-8: %s" % (
        len(nc), a["n_checked"], a["n_missing_tensors"], a["max_dE"], a["pass"] if a["n_checked"] else "nothing checked"))
    for c in a["checked"]:
        print("   n = %d  Jz = %.1f  %-10s %s (stored at %.1f): tensors %.10f  linear %.10f  |dE| = %.2e" % (
            c["n"], c["Jz"], c["label"], c["sid"], c["Jg"], c["E_tensors"], c["E_linear"], c["dE"]))
    pseudo = [dict(n=stored.D.states[sid]["n"], Jz=J, label="(state %s)" % sid,
                   lower=dict(components=dict(min=[[sid]], max=[]), ref=None)) for sid in here for J in (1.5, 1.7)]
    b = MG.g6_linear(stored, pseudo)
    print("Part B: %d (state, coupling) pairs; max |dE| = %s; all within 1e-8: %s" % (b["n_checked"], b["max_dE"], b["pass"]))
    for c in b["checked"]:
        print("   %s at Jz = %.1f (stored at %.1f): tensors %.10f  linear %.10f  |dE| = %.2e" % (
            c["sid"], c["Jz"], c["Jg"], c["E_tensors"], c["E_linear"], c["dE"]))
    out = dict(note="POST HOC supplement to gate G6a; does not replace the gate (which stays NOT COMPLETE)",
               states_with_tensors=here, part_A=dict(n_rows=len(nc), n_checked=a["n_checked"], n_missing=a["n_missing_tensors"],
                                                     max_dE=a["max_dE"], checked=a["checked"]),
               part_B=dict(n_checked=b["n_checked"], max_dE=b["max_dE"], all_within_1e8=b["pass"], checked=b["checked"]))
    with open(os.path.join(HERE, "g6_supplement.json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(out, indent=1, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
