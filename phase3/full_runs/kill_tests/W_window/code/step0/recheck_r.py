"""Post-hoc recheck of step 0 of test W (2026-11-08, paper pass R5 should-fix). Arithmetic only, no physics, no web.

  python -I recheck_r.py <W_window dir>   -> <dir>/step0_recheck.json

Envelope (FORMULA.md, supplement scaling lemma with p = 3/2):
  A = (c / 6 pi) (m0 / rho_s)^(3/2),  u(de) = 3 (A/2)^(2/3) de^(1/3),  Dm2_env = 2 m0 u + u^2,
  r_D = (m_D^2 - m0^2) / Dm2_env(e_D - e0).
iPEPS inputs (Hasik, Poilblanc, Becca, arXiv:2009.02313): D = 3..6 from the vector data of its Figs. 4 and 5 (STEP0.md
Sec. 3), D = 7 from its Table II (chi -> infinity) and, as a check, from the figures.
Constant sets:
  "api"     : e0 = -0.669441857 and m0 = 0.307447 (Sandvik, arXiv:2601.20189, abstract), rho_s = 0.18081 J and
              c = 1.6586 J a (Jiang and Wiese, arXiv:1011.6205, abstract); every digit re-read on the arXiv API 2026-11-08.
  "formula" : the set of FORMULA.md (m0 = 0.307444, rho_s = 0.180752, c = 1.65880 from Sec. III of 2601.20189, read
              through a web reader on 2026-11-07; not re-read on the API).
  "e0_1997" : the "api" set with e0 = -0.669437 (Sandvik 1997), for the e0 sensitivity.
"""
import json
import math
import os
import sys

W = sys.argv[1]
IPEPS = {"3": (-0.66460143, 0.137910), "4": (-0.66896732, 0.112848), "5": (-0.66938019, 0.103088),
         "6": (-0.66942312, 0.100097), "7_table": (-0.669432, 0.0994), "7_fig": (-0.66943196, 0.099380)}
SETS = {"api": dict(e0=-0.669441857, m0=0.307447, rho=0.18081, c=1.6586),
        "formula": dict(e0=-0.669441857, m0=0.307444, rho=0.180752, c=1.65880),
        "e0_1997": dict(e0=-0.669437, m0=0.307447, rho=0.18081, c=1.6586)}
out = {"note": "post-hoc arithmetic recheck of STEP0.md; not part of the declaration of test W", "sets": {}}
for name, k in SETS.items():
    A = k["c"] / (6 * math.pi) * (k["m0"] / k["rho"]) ** 1.5
    coef = 3 * (A / 2) ** (2 / 3)
    rows = {}
    for D, (e, m2) in IPEPS.items():
        de = e - k["e0"]
        u = coef * de ** (1 / 3)
        env = 2 * k["m0"] * u + u * u
        rows[D] = dict(de=de, excess=m2 - k["m0"] ** 2, env=env, r=(m2 - k["m0"] ** 2) / env)
    out["sets"][name] = dict(A=A, u_coef=coef, rows=rows)
a = out["sets"]["api"]["rows"]
out["summary"] = dict(r_api={D: round(v["r"], 3) for D, v in a.items()},
                      r_formula={D: round(v["r"], 3) for D, v in out["sets"]["formula"]["rows"].items()},
                      r_e0_1997={D: round(v["r"], 3) for D, v in out["sets"]["e0_1997"]["rows"].items()},
                      r_max_D3_6_api=max(a[D]["r"] for D in "3456"),
                      u_coef_rel_change=out["sets"]["formula"]["u_coef"] / out["sets"]["api"]["u_coef"] - 1)
json.dump(out, open(os.path.join(W, "step0_recheck.json"), "w", encoding="utf8"), indent=1)
print(json.dumps(out["summary"], indent=1))
print("A", out["sets"]["api"]["A"], "coef", out["sets"]["api"]["u_coef"])
