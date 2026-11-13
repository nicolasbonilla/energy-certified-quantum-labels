# real_data / e1 / learn_e1 / make_sets_e1.py   (own code; written 2026-11-12 by the rewrite task rw-L, after the
# declaration and after every result of the primary analysis was known; it decides nothing)
#
# PURPOSE.  DECLARATION.md Sec. 3: "the set S of Sec. 7 (f3) is fixed WITHOUT them (the E1-extended set is reported
# as secondary if E1 finishes)"; Sec. 12, line 17: the E1 certificates "feed only the separate E1 column and the
# secondary E1 sets". The declared map code, run with the E1 certificates (e1/collect_e1.py -> e1/map_e1/), wrote
#   e1/map_e1/S_sets.json   sizes.<n>.secondary_E1 = {S, S_3_4, S_1_2, S_p, S_p_name}   (map_tables.s_sets, 'exact_e1')
#   e1/map_e1/map_rows.json field exact_e1 of every m_s row                           (the exact interval with E1)
# but the key "intervals" of that sets file holds the exact intervals of the STORED certificates only, and the
# learning entry point code/run_learn.py reads the keys S, S_3_4, S_1_2, S_p and "intervals" (it ignores
# "secondary_E1"). It therefore cannot take the secondary sets as they are stored.
#
# WHAT THIS SCRIPT DOES.  It writes a sets file IN THE FORMAT OF THE DECLARED CODE (schema p5-real-data-S-sets-v1)
#   S_sets_E1.json   S, S_3_4, S_1_2, S_p, S_p_name := the secondary_E1 sets, copied;
#                    intervals.<Jz>.exact := the fields lo, hi, lo_exact, hi_exact, width_over_tau, certified,
#                    certified_rf of exact_e1 of the m_s row (the same seven fields that map_tables.sets_object copies
#                    from "exact"); tau, q, training, lower, outer_like: copied unchanged from e1/map_e1/S_sets.json;
#   S_sets_E1.sha256
# so that the declared entry point can be run on them UNCHANGED:
#   python -B -I code/run_learn.py --hash=<H> --stage=f3 --sets=<this folder>/S_sets_E1.json --out=<this folder>
# Nothing is recomputed here: no interval, no set, no threshold. The declared loader (rd_common.load_sets/parse_sets)
# then re-checks the file: nested sets, S_p = the most stringent nested set with at least 15 couplings, every member
# has an exact interval within its fraction of tau.
#
# It reads e1/map_e1/ only (after checking the two SHA-256 recorded there) and writes ONLY into its own folder.
# It does not open converted/, does not import the declared code and writes nothing under real_data/out/.
#
#   python -B -I make_sets_e1.py
import hashlib
import json
import os
import sys
from fractions import Fraction

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
E1 = os.path.dirname(HERE)                                   # .../real_data/e1
RD = os.path.dirname(E1)                                     # .../real_data
MAP = os.path.join(E1, "map_e1")
SCHEMA = "p5-real-data-S-sets-v1"
FIELDS = ("lo", "hi", "lo_exact", "hi_exact", "width_over_tau", "certified", "certified_rf")


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def rj(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def recorded(listing, name):
    for line in open(listing, encoding="utf-8").read().splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[-1].lstrip("*") == name:
            return parts[0].lower()
    raise SystemExit("no SHA-256 recorded for %s in %s" % (name, listing))


def main():
    decl = sha(os.path.join(RD, "DECLARATION.md"))
    with open(os.path.join(RD, "DECLARATION.sha256"), encoding="utf-8") as f:
        if decl not in f.read().lower():
            raise SystemExit("DECLARATION.md does not have the recorded SHA-256: nothing is written")
    p_sets, p_rows = os.path.join(MAP, "S_sets.json"), os.path.join(MAP, "map_rows.json")
    listing = os.path.join(MAP, "SHA256SUMS_map.txt")
    for p in (p_sets, p_rows):
        if sha(p) != recorded(listing, os.path.basename(p)):
            raise SystemExit("%s does not have the SHA-256 recorded in %s" % (p, listing))
    S0, R = rj(p_sets), rj(p_rows)
    if S0.get("schema") != SCHEMA or S0.get("declaration_sha256") != decl or R.get("declaration_sha256") != decl:
        raise SystemExit("the E1 map outputs were not written under the declaration on disk")
    rows = {(r["n"], r["key"]): r for r in R["rows"] if r["label"] == "m_s" and r.get("group") == "dataset"}
    obj = dict(schema=SCHEMA, declaration_sha256=decl, label="m_s",
               note="SECONDARY (DECLARATION.md Sec. 3 and Sec. 12 line 17): S, S_3_4, S_1_2, S_p = the sets "
                    "'secondary_E1' written by the declared map code with the stored AND the E1 certificates "
                    "(e1/map_e1/S_sets.json); intervals of m_s at (E_real, M_real): exact = the field exact_e1 of "
                    "e1/map_e1/map_rows.json (interval I of Sec. 2 with the E1 certificates added), lower and "
                    "outer_like copied unchanged. Written by e1/learn_e1/make_sets_e1.py; nothing is recomputed.",
               source=dict(sets=dict(path="e1/map_e1/S_sets.json", sha256=sha(p_sets)),
                           rows=dict(path="e1/map_e1/map_rows.json", sha256=sha(p_rows))), sizes={})
    report = []
    for n in sorted(S0["sizes"], key=int):
        s0 = S0["sizes"][n]
        sec = s0.get("secondary_E1")
        if not sec:
            raise SystemExit("no secondary_E1 sets for n = %s" % n)
        iv = {}
        n_e1 = n_stored = n_changed = 0
        for key, r0 in s0["intervals"].items():
            row = rows[(int(n), key)]
            if abs(row["tau"] - r0["tau"]) > 0 or (row.get("q") != r0.get("q")):
                raise SystemExit("n = %s, Jz = %s: tau or q of the row differs from the sets file" % (n, key))
            ex1 = row.get("exact_e1")
            new = None
            if ex1 and ex1.get("exists"):
                new = {k: ex1[k] for k in FIELDS}
                n_e1 += 1
            old = r0.get("exact")
            if old is not None:
                n_stored += 1
                if new is None:
                    raise SystemExit("n = %s, Jz = %s: an interval of the stored certificates has no E1 counterpart" % (n, key))
                # adding certificates can only tighten an interval: exact comparison of the rational ends
                if not (Fraction(new["lo_exact"]) >= Fraction(old["lo_exact"]) and Fraction(new["hi_exact"]) <= Fraction(old["hi_exact"])):
                    raise SystemExit("n = %s, Jz = %s: the E1 interval is not inside the stored one" % (n, key))
                n_changed += int(new["lo_exact"] != old["lo_exact"] or new["hi_exact"] != old["hi_exact"])
            iv[key] = dict(tau=r0["tau"], q=r0.get("q"), training=r0["training"], exact=new,
                           lower=r0.get("lower"), outer_like=r0.get("outer_like"))
        for k in ("S", "S_3_4", "S_1_2", "S_p"):                # every member has an E1 interval (the loader re-checks widths)
            for J in sec[k]:
                if iv["%.1f" % J]["exact"] is None:
                    raise SystemExit("n = %s: Jz = %.1f is in %s but has no E1 interval" % (n, J, k))
        obj["sizes"][n] = dict(S=sec["S"], S_3_4=sec["S_3_4"], S_1_2=sec["S_1_2"], S_p=sec["S_p"], S_p_name=sec["S_p_name"],
                               intervals=iv)
        report.append("n = %s: exact intervals with E1 at %d couplings (stored certificates alone: %d; changed by E1 "
                      "where both exist: %d); secondary sets |S| = %d, |S_3/4| = %d, |S_1/2| = %d, S_p = %s; "
                      "declared sets |S| = %d, |S_3/4| = %d, |S_1/2| = %d, S_p = %s"
                      % (n, n_e1, n_stored, n_changed, len(sec["S"]), len(sec["S_3_4"]), len(sec["S_1_2"]), sec["S_p_name"],
                         len(s0["S"]), len(s0["S_3_4"]), len(s0["S_1_2"]), s0["S_p_name"]))
    txt = json.dumps(obj, indent=1, sort_keys=True, allow_nan=False, ensure_ascii=True) + "\n"
    out = os.path.join(HERE, "S_sets_E1.json")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(txt)
    h = sha(out)
    with open(os.path.join(HERE, "S_sets_E1.sha256"), "w", encoding="utf-8", newline="\n") as f:
        f.write("%s  S_sets_E1.json\n" % h)
    print("declaration %s" % decl)
    print("read  e1/map_e1/S_sets.json   %s" % sha(p_sets))
    print("read  e1/map_e1/map_rows.json %s" % sha(p_rows))
    for line in report:
        print(line)
    print("wrote S_sets_E1.json %s (and S_sets_E1.sha256)" % h)


if __name__ == "__main__":
    main()
