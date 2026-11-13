"""Interactive (Plotly) versions of the certification landscape, same data as fig_landscape.py.

  python fig_landscape_html.py   -> interactive/landscape_n57.html, interactive/landscape_n115.html
                                    (+ interactive/plotly.min.js, shared, so the pages work offline)
Data: fig_landscape.data(n), i.e. landscape_data.py reading the deposited map and method outputs.
"""
import os

import numpy as np
import plotly.graph_objects as go

import common as C
import fig_landscape as F
import landscape_data as L

OUTDIR = os.path.join(C.HERE, "interactive")


def page(n):
    D = F.data(n)
    Js, de = D["Js"], D["de"]
    Jf, up = F.refine(D, D["up"], k=6)
    _, lo = F.refine(D, D["lo"], k=6)
    cert = (de[None, :] <= F.thresh_at(D, Jf)[:, None]).astype(float)
    cs = [[0, F.NEUTRAL], [0.5, F.NEUTRAL], [0.5, F.CERT], [1, F.CERT]]
    hov = "J<sub>z</sub> = %{x:.2f}<br>δe = %{y:.2e}<br>m<sub>s</sub> − m<sub>s</sub><sup>GS</sup> = %{z:.4f}<extra>%{fullData.name}</extra>"
    fig = go.Figure()
    for V, name, op in ((up, "upper edge m<sub>s</sub><sup>+</sup>", 0.6), (lo, "lower edge m<sub>s</sub><sup>−</sup>", 0.9)):
        fig.add_trace(go.Surface(x=np.repeat(Jf[:, None], len(de), 1), y=np.repeat(de[None, :], len(Jf), 0), z=V,
                                 surfacecolor=cert, colorscale=cs, cmin=0, cmax=1, showscale=False, opacity=op,
                                 name=name, hovertemplate=hov, lighting=dict(ambient=0.55, diffuse=0.6, specular=0.2)))
    # window at the dataset's energy
    for J, e, a, b in zip(Js, D["dig"], D["wlo"], D["wup"]):
        fig.add_trace(go.Scatter3d(x=[J, J], y=[e, e], z=[a, b], mode="lines", line=dict(color="#111111", width=6),
                                   showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter3d(x=Js, y=D["dig"], z=D["wup"], mode="lines+markers", name="window at the dataset's energy",
                               line=dict(color="#111111", width=5), marker=dict(size=2, color="#111111"),
                               hovertemplate=hov))
    fig.add_trace(go.Scatter3d(x=Js, y=D["dig"], z=D["wlo"], mode="lines", showlegend=False,
                               line=dict(color="#111111", width=5), hovertemplate=hov))
    E = [(J, d, m) for J, d, m in L.emu_states(n) if D["box"].de_min <= d <= D["box"].de_max]
    fig.add_trace(go.Scatter3d(x=[e[0] for e in E], y=[e[1] for e in E], z=[e[2] for e in E], mode="markers",
                               name="emulated method, own energy", marker=dict(size=6, color=F.EMU_C),
                               hovertemplate=hov))
    digJ = dict(zip(Js, D["dig"]))
    M = [(J, digJ[J], dm) for J, dm in L.dz_matched(n) if J in digJ]
    fig.add_trace(go.Scatter3d(x=[m[0] for m in M], y=[m[1] for m in M], z=[m[2] for m in M], mode="markers",
                               name="method bias at the dataset's energy (from ΔZ)",
                               marker=dict(size=5, color=F.EST_C, symbol="diamond"), hovertemplate=hov))
    Jb = np.linspace(Js[0], Js[-1], 300)
    tb = F.thresh_at(D, Jb)
    ok = (tb >= de[0]) & (tb <= de[-1])
    fig.add_trace(go.Scatter3d(x=Jb[ok], y=tb[ok], z=np.full(ok.sum(), D["box"].z_min), mode="lines",
                               name="threshold δe*(J<sub>z</sub>) (floor)", line=dict(color=F.CERT, width=5)))
    fig.add_trace(go.Scatter3d(x=Js, y=D["dig"], z=np.full(len(Js), D["box"].z_min), mode="lines",
                               name="dataset's δe (floor)", line=dict(color="#444444", width=5)))
    fig.update_layout(
        title=dict(text="What the energy allows for the staggered magnetization, n = %d (green: certified to ±3%%)" % n,
                   x=0.02, font=dict(size=15)),
        template="simple_white", font=dict(family="Georgia, serif", size=12), height=760,
        legend=dict(x=0.01, y=0.98, bgcolor="rgba(255,255,255,0.7)"), margin=dict(l=0, r=0, t=50, b=0),
        scene=dict(xaxis=dict(title="coupling J<sub>z</sub>", range=[F.J_MIN, F.J_MAX]),
                   yaxis=dict(title="energy error per site δe", type="log", autorange="reversed"),
                   zaxis=dict(title="m<sub>s</sub> − m<sub>s</sub><sup>GS</sup>", range=[D["box"].z_min, D["box"].z_max]),
                   aspectmode="manual", aspectratio=dict(x=1.8, y=1.0, z=1.2),
                   camera=dict(eye=dict(x=-1.0, y=-1.9, z=1.2))))
    os.makedirs(OUTDIR, exist_ok=True)
    out = os.path.join(OUTDIR, "landscape_n%d.html" % n)
    fig.write_html(out, include_plotlyjs="directory", full_html=True,
                   config=dict(displaylogo=False, toImageButtonOptions=dict(format="png", scale=2)))
    print("wrote", out)


if __name__ == "__main__":
    for n in (57, 115):
        page(n)
