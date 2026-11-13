# real_data / descriptive_checks.py  (own code; 2026-11-12)
#
# DESCRIPTIVE checks on the converted public data of arXiv:2606.15983. Reads only plain JSON (no pickle anywhere).
# Nothing here compares a real label with its reference value: that belongs to the analyses of DECLARATION_DRAFT.md,
# which are not run. What is tested:
#   A. the repository's lattice maps against this project's graphs (edge sets, sublattices, pair and loop lists);
#   B. the sum of the published site magnetizations against the sector value, at every coupling;
#   C. a consistency identity between the published energy, the published nearest-neighbour ZZ correlators and the
#      published site magnetizations (the exchange part must lie in its allowed range), and positivity of every
#      published pair distribution;
#   D. the three published energies of each label file against each other and against the reference energies;
#   E. the authors' DMRG observables against this project's references, for the seven label types of the map.
#
# Run:  python -B -I descriptive_checks.py <converted_dir> <ROOT of the project (work/)> <out.json>
import sys, os, io, json, math, collections
import numpy as np

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
CONV, ROOT, OUTJ = sys.argv[1:4]
J = lambda p: json.load(open(p, encoding="utf-8"))
maps = J(os.path.join(CONV, "lattice_maps.json"))["maps"]
SM = J(ROOT + "/phase3/full_runs/map/laptop_analysis/summary_map.json")
out = {"A": {}, "B": {}, "C": {}, "D": {}, "E": {}}
fz = lambda j: float(j)


def bfs_colour_like_networkx(n, edges):
    """networkx.algorithms.bipartite.color on Graph().add_edges_from(edges): the first node gets colour 1."""
    order = []
    adj = collections.OrderedDict()
    for a, b in edges:
        for u, v in ((a, b), (b, a)):
            adj.setdefault(u, []).append(v)
    first = next(iter(adj))
    col = {first: 1}; q = [first]
    while q:
        v = q.pop()
        for w in adj[v]:
            if w not in col:
                col[w] = 1 - col[v]; q.append(w)
            elif col[w] == col[v]:
                raise SystemExit("not bipartite")
    return [col[i] for i in range(n)], first


for n, gname in ((57, "hh_d5.json"), (115, "hh_d7.json")):
    D = J(os.path.join(CONV, "real_n%d.json" % n))
    G = J(ROOT + "/phase3/full_runs/method/code/graphs/" + gname)
    M = maps[str(n)]
    eta = np.array(G["eta"], float)
    M0 = int(round(eta.sum()))
    print("\n" + "=" * 110 + "\nn = %d | this project's graph: %s (%s), sector n_up %d / n_down %d, sum of eta = %d"
          % (n, gname, G["generator"], G["n_up"], G["n_down"], M0))

    # ------------------------------------------------------------------ A. lattice maps
    E_rep = set(tuple(e) for e in M["edges_sorted_unique"])
    E_own = set(tuple(sorted(e)) for e in G["edges"])
    same_edges = E_rep == E_own
    col_nx, first = bfs_colour_like_networkx(n, [tuple(e) for e in M["edges_sorted_unique"]])
    to_flip = [i for i in range(n) if col_nx[i] == 0]                 # the repository's "to_flip" = its num_ones
    same_sub = all((col_nx[i] == 1) == (eta[i] > 0) for i in range(n))
    A = {"edge_sets_identical_as_labelled": same_edges, "n_edges_repository": len(E_rep), "n_edges_project": len(E_own),
         "first_node_of_repository_colouring": first, "num_ones_repository(colour 0)": len(to_flip),
         "colour1_equals_project_eta_plus": same_sub,
         "file_lines": M["n_lines_with_an_edge"], "degree_counts_repository": dict(collections.Counter(M["degrees"])),
         "degree_counts_project": G["degree_counts"]}
    if not same_edges:
        import networkx as nx
        g1 = nx.Graph(list(E_rep)); g2 = nx.Graph(list(E_own))
        A["isomorphic"] = bool(nx.is_isomorphic(g1, g2))
    # pair lists and loop lists (taken from the first DMRG and the first label file; identity over couplings checked)
    nn2 = set(tuple(sorted(p)) for p in G["nn2"])
    loops_own = set(tuple(sorted(l)) for l in G["loops12"])
    groups = {g: D[g] for g in ("skqd_random_flip", "skqd_post_select", "dmrg") if g in D}
    pk = {"skqd_random_flip": "2_nn_corr_pairs_zz_basis_opt", "skqd_post_select": "2_nn_corr_pairs_zz_basis_opt", "dmrg": "2_nn_corr_pairs"}
    for g, d in groups.items():
        k = pk[g]
        lists = [json.dumps(e[k]) for e in d.values() if k in e]
        if not lists:
            A["pairs_%s" % g] = "no pair list in this group"
            continue
        ref = [tuple(sorted(p)) for p in json.loads(lists[0])]
        loops = [json.dumps(e["z_loop_sites"]) for e in d.values()]
        lref = set(tuple(sorted(l)) for l in json.loads(loops[0]))
        A["pairs_%s" % g] = {
            "same_list_and_order_at_every_coupling": len(set(lists)) == 1, "n_pairs": len(ref), "n_distinct": len(set(ref)),
            "pairs_that_are_edges": len(set(ref) & E_rep), "pairs_that_are_project_second_neighbours": len(set(ref) & nn2),
            "set_equals_edges_plus_second_neighbours": set(ref) == (E_own | nn2),
            "loops_same_at_every_coupling": len(set(loops)) == 1, "n_loops": len(lref),
            "loop_sets_equal_project_loops12": lref == loops_own}
    A["pair_order_identical_dmrg_vs_random_flip"] = (
        json.dumps(next(iter(D["dmrg"].values()))["2_nn_corr_pairs"]) == json.dumps(next(iter(D["skqd_random_flip"].values()))["2_nn_corr_pairs_zz_basis_opt"]))
    out["A"][str(n)] = A
    print("A. lattice:", json.dumps(A, indent=1))

    edges = sorted(E_rep)

    def table(g, zkey, ckey, pkey, ekeys):
        rows = []
        for jz, e in groups[g].items():
            if zkey not in e:
                continue
            z = np.array(e[zkey], float)
            pairs = [tuple(sorted(p)) for p in e[pkey]]
            c = dict(zip(pairs, e[ckey]))
            Jz = fz(jz)
            ce = np.array([c[ed] for ed in edges]); zi = np.array([z[a] for a, b in edges]); zj = np.array([z[b] for a, b in edges])
            pa = (1 - ce) / 2; dd = (zi - zj) / 2
            arg = pa ** 2 - dd ** 2
            B_tight = float(np.sum(0.5 * np.sqrt(np.clip(arg, 0, None)))); B_loose = float(np.sum((1 - ce) / 4))
            # positivity of every published pair distribution (all pairs, not only edges)
            viol = 0; worst = 0.0
            for (a, b), cv in c.items():
                m1 = abs(z[a] + z[b]) - (1 + cv); m2 = abs(z[a] - z[b]) - (1 - cv)
                w = max(m1, m2)
                worst = max(worst, w)
                if w > 1e-9:
                    viol += 1
            r = {"Jz": Jz, "sum_z": float(z.sum()), "sum_eta_z": float((eta * z).sum()), "max_abs_z": float(np.abs(z).max()),
                 "Ezz": float(Jz / 4 * ce.sum()), "B_tight": B_tight, "B_loose": B_loose, "pair_positivity_violations": viol,
                 "pair_positivity_worst_excess": float(worst), "n_edges_with_negative_radicand": int((arg < -1e-12).sum())}
            for k in ekeys:
                r[k] = float(e[k])
            rows.append(r)
        return rows

    # ------------------------------------------------------------------ B, C, D on the label files
    for g in ("skqd_random_flip", "skqd_post_select"):
        rows = table(g, "z_basis_opt", "2_nn_corr_funcs_zz_basis_opt", "2_nn_corr_pairs_zz_basis_opt",
                     ("final_global_energy", "energy_vopt", "ground_state_energy")) if g in groups else []
        if not rows:
            ee = [(fz(j), e) for j, e in groups.get(g, {}).items()]
            if ee:
                dv = [abs(e["final_global_energy"] - e["energy_vopt"]) for _, e in ee]
                print("\n%s: energies only (no label field). max |final_global_energy - energy_vopt| = %.3e over %d couplings" % (g, max(dv), len(ee)))
                out["D"]["%d_%s" % (n, g)] = {"energies_only": True, "max_abs_final_minus_vopt": max(dv)}
            continue
        s = np.array([r["sum_z"] for r in rows]); se = np.array([r["sum_eta_z"] for r in rows])
        sign = 1.0 if se.mean() > 0 else -1.0
        dev = sign * s - M0
        Bres = {"orientation_sign(sum eta z)": sign, "n_couplings": len(rows), "sector_value": M0,
                "sum_z_minus_sector": {"min": float(dev.min()), "max": float(dev.max()), "mean": float(dev.mean()),
                                       "max_abs": float(np.abs(dev).max()), "at_Jz_of_max_abs": rows[int(np.abs(dev).argmax())]["Jz"]},
                "n_within_1e-6": int((np.abs(dev) <= 1e-6).sum()), "n_within_1e-3": int((np.abs(dev) <= 1e-3).sum()),
                "n_within_0.05": int((np.abs(dev) <= 0.05).sum()), "max_abs_z_over_all": float(max(r["max_abs_z"] for r in rows)),
                "per_coupling": [[r["Jz"], float(sign * r["sum_z"] - M0)] for r in rows]}
        out["B"]["%d_%s" % (n, g)] = Bres
        print("\nB. %s, field z_basis_opt: orientation %+d; sum_i <Z_i> minus the sector value %d over %d couplings:" % (g, sign, M0, len(rows)))
        print("   min %+.6f  max %+.6f  mean %+.6f | max |dev| %.6f at Jz = %.1f | within 1e-6: %d, within 1e-3: %d, within 0.05: %d | largest |z_i|: %.6f"
              % (dev.min(), dev.max(), dev.mean(), np.abs(dev).max(), Bres["sum_z_minus_sector"]["at_Jz_of_max_abs"],
                 Bres["n_within_1e-6"], Bres["n_within_1e-3"], Bres["n_within_0.05"], Bres["max_abs_z_over_all"]))
        print("   per coupling (Jz: deviation): " + " ".join("%.1f:%+.4f" % (r["Jz"], sign * r["sum_z"] - M0) for r in rows))
        # C. identity
        for ek in ("final_global_energy", "ground_state_energy"):
            exy = np.array([r[ek] - r["Ezz"] for r in rows]); Bt = np.array([r["B_tight"] for r in rows]); Bl = np.array([r["B_loose"] for r in rows])
            ratio_t = -exy / Bt; ratio_l = -exy / Bl
            Cres = {"energy_field": ek, "exchange_part_E_minus_Ezz": {"min": float(exy.min()), "max": float(exy.max())},
                    "ratio_to_tight_bound": {"min": float(ratio_t.min()), "max": float(ratio_t.max()), "n_above_1": int((ratio_t > 1 + 1e-9).sum()), "n_negative": int((ratio_t < 0).sum())},
                    "ratio_to_loose_bound": {"min": float(ratio_l.min()), "max": float(ratio_l.max()), "n_above_1": int((ratio_l > 1 + 1e-9).sum())},
                    "per_coupling_ratio_tight": [[r["Jz"], float(x)] for r, x in zip(rows, ratio_t)]}
            out["C"]["%d_%s_%s" % (n, g, ek)] = Cres
            print("C. %s, identity with %s: exchange part E - (Jz/4) sum_e <ZZ>_e in [%.4f, %.4f]; as a fraction of its largest allowed size:"
                  % (g, ek, exy.min(), exy.max()))
            print("   tight bound (uses <Z_i>, <Z_j>, <Z_iZ_j>): min %.4f max %.4f, above 1: %d, negative: %d | loose bound (uses <Z_iZ_j> only): min %.4f max %.4f, above 1: %d"
                  % (ratio_t.min(), ratio_t.max(), Cres["ratio_to_tight_bound"]["n_above_1"], Cres["ratio_to_tight_bound"]["n_negative"],
                     ratio_l.min(), ratio_l.max(), Cres["ratio_to_loose_bound"]["n_above_1"]))
            if ek == "final_global_energy":
                print("   per coupling (Jz: fraction of the tight bound): " + " ".join("%.1f:%.3f" % (r["Jz"], x) for r, x in zip(rows, ratio_t)))
        pv = sum(r["pair_positivity_violations"] for r in rows); pw = max(r["pair_positivity_worst_excess"] for r in rows)
        nr = sum(r["n_edges_with_negative_radicand"] for r in rows)
        out["C"]["%d_%s_positivity" % (n, g)] = {"pairs_violating": pv, "worst_excess": pw, "edges_with_negative_radicand": nr}
        print("   positivity of the published pair distributions (|z_i +- z_j| <= 1 +- <Z_iZ_j>, all pairs, all couplings): violations %d, worst excess %.3e" % (pv, pw))
        # D. energies
        dm = groups["dmrg"]
        fv = np.array([abs(r["final_global_energy"] - r["energy_vopt"]) for r in rows])
        above = np.array([r["final_global_energy"] - dm["%.1f" % r["Jz"]]["ground_state_energy"] for r in rows])
        pre = np.array([r["ground_state_energy"] - r["final_global_energy"] for r in rows])
        refs = [(r["Jz"], r["final_global_energy"] - SM["refs"]["%d_%.1f" % (n, r["Jz"])]["E0"]) for r in rows if "%d_%.1f" % (n, r["Jz"]) in SM["refs"]]
        Dres = {"max_abs_final_minus_vopt": float(fv.max()), "n_final_equals_vopt_within_1e-6": int((fv <= 1e-6).sum()),
                "final_minus_authors_dmrg": {"min": float(above.min()), "max": float(above.max()), "n_negative": int((above < 0).sum())},
                "first_stage_minus_final": {"min": float(pre.min()), "max": float(pre.max()), "n_negative": int((pre < 0).sum())},
                "final_minus_project_E0": {"n": len(refs), "min": min(v for _, v in refs), "n_negative": sum(1 for _, v in refs if v < 0)}}
        out["D"]["%d_%s" % (n, g)] = Dres
        print("D. %s energies: max |final_global_energy - energy_vopt| = %.3e (within 1e-6 at %d of %d) | final - authors' DMRG E0: min %.5f max %.5f, negative at %d"
              % (g, fv.max(), Dres["n_final_equals_vopt_within_1e-6"], len(rows), above.min(), above.max(), Dres["final_minus_authors_dmrg"]["n_negative"]))
        print("   first-stage (ground_state_energy) - final: min %.4f max %.4f, negative at %d | final - this project's E0 at %d stored couplings: min %.5f, negative at %d"
              % (pre.min(), pre.max(), Dres["first_stage_minus_final"]["n_negative"], len(refs), Dres["final_minus_project_E0"]["min"], Dres["final_minus_project_E0"]["n_negative"]))

    # ------------------------------------------------------------------ B, C on the authors' DMRG (control), and E
    rows = table("dmrg", "z", "2_nn_corr_funcs_zz", "2_nn_corr_pairs", ("ground_state_energy", "e1"))
    s = np.array([r["sum_z"] for r in rows]); se = np.array([r["sum_eta_z"] for r in rows])
    signs = np.sign(se)
    dev = signs * s - M0
    exy = np.array([r["ground_state_energy"] - r["Ezz"] for r in rows]); Bt = np.array([r["B_tight"] for r in rows])
    out["B"]["%d_dmrg" % n] = {"orientation_signs": dict(collections.Counter(float(x) for x in signs)), "sector_value": M0,
                               "sum_z_minus_sector": {"min": float(dev.min()), "max": float(dev.max()), "max_abs": float(np.abs(dev).max())},
                               "per_coupling": [[r["Jz"], float(d)] for r, d in zip(rows, dev)]}
    out["C"]["%d_dmrg" % n] = {"ratio_to_tight_bound": {"min": float((-exy / Bt).min()), "max": float((-exy / Bt).max())},
                               "pairs_violating": sum(r["pair_positivity_violations"] for r in rows)}
    print("\nB/C control. authors' DMRG (no S^z conservation in their code): orientation signs %s; sum_i <Z_i> minus sector value: min %+.2e max %+.2e (largest |dev| at Jz = %.1f)"
          % (dict(collections.Counter(float(x) for x in signs)), dev.min(), dev.max(), rows[int(np.abs(dev).argmax())]["Jz"]))
    print("   couplings with |dev| > 1e-4: " + (" ".join("%.1f:%+.4f" % (r["Jz"], d) for r, d in zip(rows, dev) if abs(d) > 1e-4) or "none"))
    print("   identity: exchange part as a fraction of the tight bound: min %.4f max %.4f | pair positivity violations: %d"
          % ((-exy / Bt).min(), (-exy / Bt).max(), out["C"]["%d_dmrg" % n]["pairs_violating"]))

    # E. authors' DMRG observables against this project's references (map rows: O_GS; refs: E0, m_s_GS)
    loc = G["local"]; nn2l = [tuple(sorted(p)) for p in G["nn2"]]; el = [tuple(sorted(e)) for e in G["edges"]]
    Eres = collections.defaultdict(list)
    for r in SM["rows"]:
        if r["n"] != n:
            continue
        key = "%.1f" % r["Jz"]
        e = D["dmrg"].get(key)
        if e is None:
            continue
        z = np.array(e["z"], float); sg = 1.0 if float((eta * z).sum()) > 0 else -1.0
        c = dict(zip([tuple(sorted(p)) for p in e["2_nn_corr_pairs"]], e["2_nn_corr_funcs_zz"]))
        loops = {tuple(sorted(l)): v for l, v in zip(e["z_loop_sites"], e["z_loop"])}
        lab = r["label"]
        if lab == "m_s": v = sg * float((eta * z).sum()) / n
        elif lab == "Czz_bar": v = float(np.mean([c[x] for x in el]))
        elif lab == "C2_bar": v = float(np.mean([c[x] for x in nn2l]))
        elif lab == "Z_bulk": v = sg * float(z[loc["bulk_site"]])
        elif lab == "Z_boundary": v = sg * float(z[loc["boundary_site"]])
        elif lab == "Czz_edge": v = float(c[tuple(sorted(loc["edge"]))])
        elif lab == "Z_loop": v = float(loops[tuple(sorted(loc["loop"]))])
        else: continue
        Eres[lab].append((r["Jz"], v - r["O_GS"], (v - r["O_GS"]) / r["tau"], r["O_GS"]))
    print("\nE. authors' DMRG observable minus this project's reference O_GS, at the couplings of the stored map:")
    for lab in ("m_s", "Czz_bar", "C2_bar", "Z_bulk", "Z_boundary", "Czz_edge", "Z_loop"):
        v = Eres.get(lab, [])
        if not v:
            continue
        a = np.array([x[1] for x in v]); t = np.array([x[2] for x in v]); w = int(np.abs(t).argmax())
        out["E"]["%d_%s" % (n, lab)] = {"n_rows": len(v), "max_abs_diff": float(np.abs(a).max()), "max_abs_diff_in_tau": float(np.abs(t).max()),
                                         "at_Jz": v[w][0], "rows": [[x[0], x[1], x[2]] for x in v]}
        print("   %-11s rows %2d | max |diff| %.2e | in units of tau: %.2e (at Jz = %.1f) | rows above 1e-3 tau: %s"
              % (lab, len(v), np.abs(a).max(), np.abs(t).max(), v[w][0], [x[0] for x in v if abs(x[2]) > 1e-3] or "none"))
    de = [(k, D["dmrg"]["%.1f" % r["Jz"]]["ground_state_energy"] - r["E0"], (D["dmrg"]["%.1f" % r["Jz"]]["e1"] - D["dmrg"]["%.1f" % r["Jz"]]["ground_state_energy"]) / r["gap_ours"] - 1)
          for k, r in SM["refs"].items() if r["n"] == n and "%.1f" % r["Jz"] in D["dmrg"]]
    out["E"]["%d_energy" % n] = {"n": len(de), "authors_minus_project_E0": {"min": min(x[1] for x in de), "max": max(x[1] for x in de)},
                                 "authors_gap_over_project_gap_minus_1": {"min": min(x[2] for x in de), "max": max(x[2] for x in de)}}
    print("   energy: authors' E0 - this project's E0 at %d couplings: min %.2e max %.2e | authors' gap (e1 - E0) / this project's smallest gap - 1: min %+.4f max %+.4f"
          % (len(de), min(x[1] for x in de), max(x[1] for x in de), min(x[2] for x in de), max(x[2] for x in de)))

json.dump(out, open(OUTJ, "w", encoding="utf-8"), indent=1)
print("\nwritten", OUTJ)
