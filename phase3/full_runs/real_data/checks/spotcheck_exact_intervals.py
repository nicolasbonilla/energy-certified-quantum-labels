# real_data / checks / spotcheck_exact_intervals.py   (own code of the task rd-map; 2026-11-12; written AFTER the hash)
#
# Independent recomputation of the exact intervals of DECLARATION.md Sec. 2 (certified side), written from the text of
# the declaration (Sec. 0, Sec. 2, Sec. 12 lines 2 and 3). It imports NOTHING of real_data/code/ and nothing of the
# stored run folders: standard library only, fractions.Fraction throughout. It reads
#   - converted/real_n57.json, converted/real_n115.json (plain JSON; only after checking DECLARATION.sha256),
#   - the graph files of the stored map (eta and edges),
#   - every *_cert.json of the two rigor runs and of final_tests/ with its *_ver.json,
#   - summary_map.json (this project's reference values, for tau),
#   - out/map_rows.json (the output of the sealed code), ONLY to compare.
# What it does: for m_s and Czz_bar at the 50 couplings of both sizes it rebuilds the interval
#   I = hull over M in {M_real (worse of +-1e-6, bound by bound), M_0} of [max of the lower bounds, min of the upper bounds]
# at the energy E_real + 1e-6, compares both ends as exact rationals with the sealed output, recounts CERTIFIED (exact)
# and J*_exact for both tolerances, and prints the rows named in SPOT in full.
#
#   python -B -I spotcheck_exact_intervals.py            (writes spotcheck_exact_intervals.json next to itself)
import hashlib
import json
import os
import re
import sys
from fractions import Fraction as Fr

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
RD = os.path.dirname(HERE)
FULL = os.path.dirname(RD)
ALLOW = Fr(1, 10 ** 6)
GRAPH = {57: "hh_d5.json", 115: "hh_d7.json"}
ROOTS = [os.path.join(FULL, "rigor", "out_20261031T073328Z"), os.path.join(FULL, "rigor", "out_20261031T100015Z"),
         os.path.join(FULL, "final_tests")]
RANGE = {57: (Fr(34, 10), Fr(6)), 115: (Fr(4), Fr(6))}          # declaration Sec. 2, "Range"
COUPLINGS = [Fr(k, 10) for k in range(11, 61)]
TRAIN = [J for J in COUPLINGS if J >= Fr(16, 10)]
SPOT = [(57, "3.4", "m_s"), (57, "3.5", "m_s"), (115, "4.0", "m_s"), (115, "5.0", "m_s"), (57, "5.0", "Czz_bar"),
        (115, "4.0", "Czz_bar")]


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def guard():
    want = re.search(r"[0-9a-f]{64}", open(os.path.join(RD, "DECLARATION.sha256"), encoding="utf-8").read()).group(0)
    have = sha(os.path.join(RD, "DECLARATION.md"))
    if want != have:
        raise SystemExit("REFUSED: DECLARATION.sha256 does not match DECLARATION.md")
    return have


def load_graph(n):
    G = json.load(open(os.path.join(FULL, "map", "laptop_analysis", "code", "graphs", GRAPH[n]), encoding="utf-8"))
    assert G["n"] == n
    return [int(x) for x in G["eta"]], [tuple(sorted(e)) for e in G["edges"]]


def load_certs(n, M0):
    """Every distinct certificate file of size n: (kind, J_base, sigma, lam, c, mu, name). Accepted only if its
    verification record says ok for this very file and c - mu M_0 equals the claimed bound exactly."""
    out, seen, nfiles = [], set(), 0
    for root in ROOTS:
        for dp, _, fn in os.walk(root):
            for f in sorted(fn):
                if not f.endswith("_cert.json"):
                    continue
                p = os.path.join(dp, f)
                d = json.load(open(p, encoding="utf-8"))
                if d.get("graph") != GRAPH[n]:
                    continue
                nfiles += 1
                h = sha(p)
                if h in seen:
                    continue
                seen.add(h)
                t = d["task"]
                den = 2 ** int(d["K"])
                c = sum(Fr(int(x), den) for x in d["t"])
                mu = Fr(int(d["mu"]), den)
                claim = Fr(d["E_claim"])
                assert c - mu * M0 == claim, "E_claim mismatch in " + f
                v = json.load(open(p[:-len("_cert.json")] + "_ver.json", encoding="utf-8"))
                assert v["ok"] is True and v["cert_sha256"] == h and Fr(v["E_LB_exact"]) == claim, "bad record for " + f
                out.append(dict(kind=t["kind"], J=Fr(str(t["Jz"])), sigma=int(t.get("sigma", 0)), lam=Fr(str(t.get("lam", "0"))),
                                c=c, mu=mu, name=f[:-len("_cert.json")], sha=h))
    return out, nfiles


def bounds_ms(certs, n, J):
    """[(sign, lam*n, c, mu, text)]: sign * m_s <= (E - c + mu M)/(lam n). Direct certificates at J and every pair
    J_1 < J < J_2 of the same sign, combined with t = (J_2 - J)/(J_2 - J_1)."""
    cs = [x for x in certs if x["kind"] == "m_s"]
    out = [(x["sigma"], x["lam"] * n, x["c"], x["mu"], "direct " + x["name"]) for x in cs if x["J"] == J]
    for a in cs:
        for b in cs:
            if a["sigma"] == b["sigma"] and a["J"] < J < b["J"]:
                t = (b["J"] - J) / (b["J"] - a["J"])
                out.append((a["sigma"], (t * a["lam"] + (1 - t) * b["lam"]) * n, t * a["c"] + (1 - t) * b["c"],
                            t * a["mu"] + (1 - t) * b["mu"], "pair t=%s %s + %s" % (t, a["name"], b["name"])))
    return out


def bounds_czz(certs, J, n_e):
    """A certificate of kind Czz_bar (base J_b, sign s, field lam) or H is H(J') + mu M >= c with J' = J_b - 4 s lam.
    J' < J: Czz_bar <= 4 (E - c + mu M)/((J - J') n_e); J' > J: -Czz_bar <= 4 (E - c + mu M)/((J' - J) n_e)."""
    out = []
    for x in certs:
        if x["kind"] not in ("Czz_bar", "H"):
            continue
        Jp = x["J"] - 4 * x["sigma"] * x["lam"] if x["kind"] == "Czz_bar" else x["J"]
        if Jp == J:
            continue
        out.append((1 if Jp < J else -1, abs(J - Jp) * n_e / 4, x["c"], x["mu"], "J'=%s %s" % (float(Jp), x["name"])))
    return out


def interval(bounds, E, M_real, M0):
    """Hull over the two values of M of the interval allowed by all the bounds; None if a side has no bound."""
    if not any(b[0] == 1 for b in bounds) or not any(b[0] == -1 for b in bounds):
        return None
    E = E + ALLOW
    ends = []
    for M, dM in ((M_real, ALLOW), (Fr(M0), Fr(0))):
        up = min(((E - c + mu * M + abs(mu) * dM) / lamS, txt) for s, lamS, c, mu, txt in bounds if s == 1)
        dn = min(((E - c + mu * M + abs(mu) * dM) / lamS, txt) for s, lamS, c, mu, txt in bounds if s == -1)
        ends.append((-dn[0], up[0], dn[1], up[1]))
    lo, hi = min(e[0] for e in ends), max(e[1] for e in ends)
    who = dict(lower_end_from="M_real" if ends[0][0] <= ends[1][0] else "M_0", upper_end_from="M_real" if ends[0][1] >= ends[1][1] else "M_0",
               at_M_real=[float(ends[0][0]), float(ends[0][1]), ends[0][2], ends[0][3]],
               at_M_0=[float(ends[1][0]), float(ends[1][1]), ends[1][2], ends[1][3]])
    return max(lo, Fr(-1)), min(hi, Fr(1)), who


def jstar(flags):
    js = None
    for J in reversed(TRAIN):
        if not flags.get(J):
            break
        js = float(J)
    return js


def main():
    decl = guard()
    SM = json.load(open(os.path.join(FULL, "map", "laptop_analysis", "summary_map.json"), encoding="utf-8"))
    ref = {(r["n"], "%.1f" % r["Jz"], r["label"]): float(r["O_GS"]) for r in SM["rows"]}
    sealed = {(r["n"], r["key"], r["label"]): r for r in
              json.load(open(os.path.join(RD, "out", "map_rows.json"), encoding="utf-8"))["rows"]}
    res = dict(declaration_sha256=decl, rows=[], summary={})
    n_cmp = n_equal = 0
    for n in (57, 115):
        eta, edges = load_graph(n)
        M0 = sum(eta)
        certs, nfiles = load_certs(n, M0)
        data = json.load(open(os.path.join(RD, "converted", "real_n%d.json" % n), encoding="utf-8"))
        ms_J = sorted(set(x["J"] for x in certs if x["kind"] == "m_s"))
        assert (ms_J[0], ms_J[-1]) == RANGE[n], "range of the m_s certificates differs from the declared one"
        print("n = %d: %d certificate files, %d distinct; m_s certificates at %s" % (n, nfiles, len(certs), [float(j) for j in ms_J]))
        flags = {(lab, tol): {} for lab in ("m_s", "Czz_bar") for tol in ("tau", "tau_rf")}
        for J in COUPLINGS:
            key = "%.1f" % float(J)
            e, dm = data["skqd_random_flip"][key], data["dmrg"][key]
            z = [Fr(x) for x in e["z_basis_opt"]]
            assert len(z) == n
            E, M = Fr(e["final_global_energy"]), sum(z)
            pr = {tuple(sorted(p)): Fr(v) for p, v in zip(e["2_nn_corr_pairs_zz_basis_opt"], e["2_nn_corr_funcs_zz_basis_opt"])}
            prd = {tuple(sorted(p)): Fr(v) for p, v in zip(dm["2_nn_corr_pairs"], dm["2_nn_corr_funcs_zz"])}
            real = dict(m_s=sum(a * b for a, b in zip(eta, z)) / n, Czz_bar=sum(pr[ed] for ed in edges) / len(edges))
            auth = dict(m_s=float(sum(a * Fr(b) for a, b in zip(eta, dm["z"])) / n), Czz_bar=float(sum(prd[ed] for ed in edges) / len(edges)))
            for lab in ("m_s", "Czz_bar"):
                bs = bounds_ms(certs, n, J) if lab == "m_s" else bounds_czz(certs, J, len(edges))
                iv = interval(bs, E, M, M0)
                o_gs = ref.get((n, key, lab), auth[lab])
                tau = Fr(0.06 * abs(o_gs))
                s = sealed[(n, key, lab)]
                row = dict(n=n, Jz=key, label=lab, exists=iv is not None, n_bounds=len(bs))
                sx = s.get("exact") or {}
                if iv is None:
                    row["agrees_with_sealed"] = bool(not sx.get("exists"))
                    for tol in ("tau", "tau_rf"):
                        flags[(lab, tol)][J] = False
                else:
                    lo, hi, who = iv
                    w = hi - lo
                    tau_rf = Fr(6, 100) * (Fr(0) if lo <= 0 <= hi else min(abs(lo), abs(hi)))
                    inr = RANGE[n][0] <= J <= RANGE[n][1]
                    row.update(lo=float(lo), hi=float(hi), lo_exact="%d/%d" % (lo.numerator, lo.denominator),
                               hi_exact="%d/%d" % (hi.numerator, hi.denominator), width_over_tau=float(w / tau),
                               width_over_tau_rf=float(w / tau_rf) if tau_rf > 0 else None, in_range=inr,
                               certified=bool(inr and w <= tau), certified_rf=bool(inr and w <= tau_rf),
                               label_real=float(real[lab]), truth=o_gs, label_inside=bool(lo <= real[lab] <= hi),
                               truth_inside=bool(lo <= Fr(o_gs) <= hi), who=who)
                    same = bool(sx.get("exists") and Fr(sx["lo_exact"]) == lo and Fr(sx["hi_exact"]) == hi
                                and sx["certified"] == row["certified"] and sx["certified_rf"] == row["certified_rf"])
                    row["agrees_with_sealed"] = same
                    for tol, k in (("tau", "certified"), ("tau_rf", "certified_rf")):
                        flags[(lab, tol)][J] = row[k]
                n_cmp += 1
                n_equal += row["agrees_with_sealed"]
                res["rows"].append(row)
                if (n, key, lab) in SPOT:
                    print("  SPOT n=%d Jz=%s %s: E_real=%.9f M_real-M_0=%.6f  %d bounds" % (n, key, lab, float(E), float(M - M0), len(bs)))
                    if iv is not None:
                        print("     I = [%.9f, %.9f]  width/tau = %.6f  width/tau_rf = %.6f  certified = %s / %s  (sealed: [%s, %s], %s / %s)" % (
                            row["lo"], row["hi"], row["width_over_tau"], row["width_over_tau_rf"], row["certified"], row["certified_rf"],
                            "%.9f" % sx["lo"] if sx.get("exists") else None, "%.9f" % sx["hi"] if sx.get("exists") else None,
                            sx.get("certified"), sx.get("certified_rf")))
                        print("     both ends equal to the sealed output as exact rationals: %s;  real label %.9f inside: %s;  truth %.9f inside: %s" % (
                            same, row["label_real"], row["label_inside"], o_gs, row["truth_inside"]))
                        print("     lower end from %s, upper end from %s" % (who["lower_end_from"], who["upper_end_from"]))
                        print("     at M_real: [%.9f, %.9f]  lower: %s | upper: %s" % tuple(who["at_M_real"]))
                        print("     at M_0   : [%.9f, %.9f]  lower: %s | upper: %s" % tuple(who["at_M_0"]))
        for (lab, tol), fl in flags.items():
            tr = {J: fl[J] for J in TRAIN}
            cnt, js = sum(1 for v in tr.values() if v), jstar(tr)
            res["summary"]["%d_%s_%s" % (n, lab, tol)] = dict(certified_of_45=cnt, J_star_exact=js)
            print("  n = %d %-8s %-6s: CERTIFIED (exact) at %d of 45 training couplings, J*_exact = %s" % (n, lab, tol, cnt, js))
    viol = [(r["n"], r["Jz"], r["label"]) for r in res["rows"] if r.get("exists") and (r["certified"] or r["certified_rf"])
            and not (r["label_inside"] and r["truth_inside"])]
    res["summary"].update(n_compared=n_cmp, n_equal_to_sealed=n_equal, G7_violations=viol)
    print("rows compared with the sealed output: %d; identical (both ends as exact rationals and both flags): %d" % (n_cmp, n_equal))
    print("certified rows whose label or truth lies outside the interval:", viol)
    with open(os.path.join(HERE, "spotcheck_exact_intervals.json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(res, indent=1, sort_keys=True) + "\n")
    return 0 if n_cmp == n_equal else 1


if __name__ == "__main__":
    sys.exit(main())
