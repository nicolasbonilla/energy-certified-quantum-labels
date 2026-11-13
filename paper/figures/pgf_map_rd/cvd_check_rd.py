"""Colour-vision check of the NEW colours of fig_map_rd.tex (python -B -I cvd_check_rd.py; writes cvd_check_rd.txt).

The label colours are those of ../pgf_map/fig_map.tex (checked there: ../pgf_map/cvd_check.txt). New here: the four
colours of the status strip, the tint of the E1 symbols, the grey of the undecided symbols, and the elements of the
bottom panels. Method and matrices: ../pgf_map/cvd_check.py (imported, nothing is written there): Machado, Oliveira
& Fernandes 2009, severity 1.0, CIE76 colour difference of every pair that is drawn next to each other.
"""
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "pgf_map")))
import cvd_check as C          # noqa: E402  (functions sim, M only)


def mix(hexc, share):
    """the colour <hexc>!<share>!white of xcolor"""
    return "".join("%02X" % round(share * int(hexc[i:i + 2], 16) + (1 - share) * 255) for i in (0, 2, 4))


# 2026-11-13 (F2): one status code for Figs. 1(c), 2(b), 3 -- certified = teal 169B88 (rim 0B5F53), not certified =
# 55554F, undecided = DAD9D3 (rim and hatch 8E8D88), certified only with E1 = 7FC8BE (= 169B88 at 55 %) with a dot; the
# labels are told apart by symbol and line style; the third average and the local labels are grey (6E6E69, 8A8A85)
PAL = {"certified cell": "169B88", "not-certified cell": "55554F", "undecided cell": "DAD9D3", "E1 cell": mix("169B88", 0.55),
       "white": "FFFFFF", "test shading": "E9E8E3",
       "certified symbol": "169B88", "E1 symbol": mix("169B88", 0.55), "undecided symbol": "DAD9D3",
       "not-certified line": "55554F", "third average": "6E6E69", "local label": "8A8A85",
       "band": "CFE0F4", "exact line": "169B88", "public label": "0B0B0B", "emulation": "C0392B"}
PAIRS = [("certified cell", "not-certified cell"), ("certified cell", "undecided cell"), ("certified cell", "E1 cell"),
         ("not-certified cell", "undecided cell"), ("not-certified cell", "E1 cell"), ("undecided cell", "E1 cell"),
         ("undecided cell", "white"), ("undecided cell", "test shading"),
         ("certified symbol", "E1 symbol"), ("E1 symbol", "white"), ("E1 symbol", "undecided symbol"),
         ("certified symbol", "not-certified line"), ("not-certified line", "local label"), ("local label", "white"),
         ("band", "white"), ("band", "exact line"), ("band", "public label"), ("band", "emulation"),
         ("public label", "emulation")]


def main():
    lines = ["pair                                    " + "".join("%9s" % k for k in C.M)]
    worst = (1e9, None)
    for a, b in PAIRS:
        row = "%-39s " % (a + " / " + b)
        for k, m in C.M.items():
            la, lb = C.sim(PAL[a], m), C.sim(PAL[b], m)
            d = sum((x - y) ** 2 for x, y in zip(la, lb)) ** 0.5
            row += "%9.1f" % d
            worst = min(worst, (d, "%s / %s (%s)" % (a, b, k)))
        lines.append(row)
    lines.append("CIE76 Delta E; below about 10 two colours are hard to tell apart by colour alone.")
    lines.append("smallest: %.1f for %s" % worst)
    lines.append("The E1 cells also carry a dot and the undecided cells a hatch; the E1 symbols sit on a dashed line; "
                 "the undecided symbols have a grey rim. Labels differ by symbol shape and line style, not by colour.")
    print("\n".join(lines))
    with open(os.path.join(HERE, "cvd_check_rd.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
