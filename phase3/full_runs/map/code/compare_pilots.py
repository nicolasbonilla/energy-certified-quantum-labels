"""Only-compared table: the map against the two earlier pilots at the points they share (laptop, JSON arithmetic).

  python -I compare_pilots.py <summary_map.json> <pilot2 summary2.json> <witness pilot summary.json> <out.json>
Pilot2 (design/pilot2, thresholds E_up/E_lo with chi 320 chains; C_zz-bar from its cold ground-state curve) and the
witness pilot (pilot_witness, E_thr = E0 + 0.8 r min(gap) = our E_lo at Jz = 1.2 and 1.6 up to the reading's rounding).
"""
import json
import sys


def main(sp, p2p, pwp, outp):
    S = json.load(open(sp))
    P2 = json.load(open(p2p))
    PW = json.load(open(pwp))
    rows = {(r["n"], round(r["Jz"], 1), r["label"]): r for r in S["rows"]}
    out = []
    # pilot2 chain labels (keys n_J_label; 'up' and 'lo' blocks)
    for key, b in P2["labels"].items():
        n, J, lab = key.split("_", 2)
        r = rows.get((int(n), float(J), lab))
        if not r:
            continue
        for side, ours in (("up", "at_up"), ("lo", "at_lo")):
            out.append(dict(src="pilot2", n=int(n), Jz=float(J), label=lab, at=side,
                            eps_pilot=b[side]["eps"], eps_map=r[ours]["eps"],
                            w_in_pilot=b[side]["w_inner"], w_in_map=r[ours]["w_in"],
                            w_out_pilot=b[side]["w_outer"], w_out_map=r[ours]["w_out"]))
    for J, row in P2["conj"].items():
        r = rows.get((57, float(J), "Czz_bar"))
        if not r:
            continue
        for side, ours in (("up", "at_up"), ("lo", "at_lo")):
            out.append(dict(src="pilot2-curve", n=57, Jz=float(J), label="Czz_bar", at=side,
                            eps_pilot=row[side]["eps"], eps_map=r[ours]["eps"],
                            w_in_pilot=row[side]["Czz_w_inner"], w_in_map=r[ours]["w_in"],
                            w_out_pilot=row[side]["Czz_w_outer"], w_out_map=r[ours]["w_out"]))
    # witness pilot: m_s D at E_thr (= our E_lo), local labels at 1.2 / 1.6, n = 115 at 1.6
    for J, D in PW["Q"].items():
        r = rows.get((57, float(J), "m_s"))
        if r:
            out.append(dict(src="witness", n=57, Jz=float(J), label="m_s", at="lo", D_pilot=D,
                            D_pure_pilot=PW["blocks"]["57_%s" % J].get("D_pure") if "blocks" in PW else None,
                            w_in_map=r["at_lo"]["w_in"], w_pure_map=r["at_lo"]["w_pure"], w_out_map=r["at_lo"]["w_out"],
                            eps_map=r["at_lo"]["eps"]))
    b = PW["n115"]["block"]
    r = rows.get((115, 1.6, "m_s"))
    if r:
        out.append(dict(src="witness", n=115, Jz=1.6, label="m_s", at="lo", D_pilot=b["D"], D_pure_pilot=b["D_pure"],
                        w_in_map=r["at_lo"]["w_in"], w_pure_map=r["at_lo"]["w_pure"], w_out_map=r["at_lo"]["w_out"],
                        eps_map=r["at_lo"]["eps"]))
    for key, b in PW["local"].items():
        lab, J = key.rsplit("_", 1)
        r = rows.get((57, float(J), lab))
        if r:
            out.append(dict(src="witness", n=57, Jz=float(J), label=lab, at="lo", D_pilot=b["D"],
                            D_pure_pilot=b.get("D_pure"), w_in_map=r["at_lo"]["w_in"], w_pure_map=r["at_lo"]["w_pure"],
                            w_out_map=r["at_lo"]["w_out"], eps_map=r["at_lo"]["eps"]))
    json.dump(out, open(outp, "w"), indent=1)
    for x in out:
        print(json.dumps({k: (round(v, 5) if isinstance(v, float) else v) for k, v in x.items()}))


if __name__ == "__main__":
    main(*sys.argv[1:])
