"""Numeric side: local-consistency (cluster-marginal) relaxation in dual form = optimized Anderson splitting.

    E0(sector) >= f(Y, mu) = sum_k lambda_min(h_k) - mu * twoS,
    h_k = (terms assigned to cluster k) + sum_{overlaps O=(k,l)} (+Y_O if k<l else -Y_O) (x) 1 + mu * sum_{i in A_k} Z_i
Any real symmetric, Sz-block-diagonal Y_O and any mu give a valid bound, because sum_k h_k = H + mu * sum_i Z_i and
sum_i Z_i = twoS on the sector.  The Y_O also redistribute terms between clusters (they span all Sz-preserving
operators on the overlap).  We maximise a soft-min smoothing of f with L-BFGS (beta continuation), start from the
plain Anderson splitting (every term spread uniformly over the clusters that contain it), then round Y, mu to dyadic
rationals and write a certificate whose claimed bound is re-derived EXACTLY by verify_exact.py (separate script).

usage: python lb_opt.py <graph.json> <task.json> <out_cert.json>
task: {"kind": "H"|"m_s"|"Czz_bar", "Jz": "4", "sigma": 1, "lam": "<exact or float>", "clusters": "vball2"|"eball2"|...,
       "K": 32, "betas": [...], "maxiter": 400, "use_mu": true}
"""
import json
import os
import sys
import time
import hashlib
from fractions import Fraction
from collections import deque

import numpy as np
from scipy.optimize import minimize

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lbcore import load_graph, ham_spec, spec_to_json, terms, frac


def bfs_dist(n, adj, src):
    d = [-1] * n
    d[src] = 0
    q = deque([src])
    while q:
        u = q.popleft()
        for w in adj[u]:
            if d[w] < 0:
                d[w] = d[u] + 1
                q.append(w)
    return d


def make_clusters(g, mode):
    n = g["n"]
    adj = [[] for _ in range(n)]
    for i, j in g["edges"]:
        adj[i].append(j)
        adj[j].append(i)
    D = [bfs_dist(n, adj, v) for v in range(n)]
    kind, r = mode[:5], int(mode[5:])
    cand = []
    if kind == "vball":
        for v in range(n):
            cand.append(frozenset(u for u in range(n) if 0 <= D[v][u] <= r))
    elif kind == "eball":
        for i, j in g["edges"]:
            cand.append(frozenset(u for u in range(n) if min(D[i][u], D[j][u]) <= r))
    else:
        raise ValueError(mode)
    cand = sorted(set(cand), key=lambda s: (len(s), sorted(s)))
    keep = [c for c in cand if not any(c < o for o in cand)]
    return [sorted(c) for c in sorted(keep, key=lambda s: sorted(s))]


def popcount(x):
    return bin(x).count("1")


class Relax:
    def __init__(self, g, sp, clusters, use_mu=True, min_overlap=1):
        self.g, self.sp, self.cl = g, sp, clusters
        self.use_mu = use_mu
        n = g["n"]
        self.T = terms(g, sp)
        self.twoS = g["twoS"]
        sets = [set(c) for c in clusters]
        # overlaps
        self.ov = []
        for k in range(len(clusters)):
            for l in range(k + 1, len(clusters)):
                O = sorted(sets[k] & sets[l])
                if len(O) >= min_overlap:
                    self.ov.append((k, l, O))
        # parameter layout per overlap: pairs (a<=b) with equal popcount
        self.par = []
        P = 0
        for (k, l, O) in self.ov:
            q = len(O)
            pairs = [(a, b) for a in range(2 ** q) for b in range(a, 2 ** q) if popcount(a) == popcount(b)]
            self.par.append((P, pairs))
            P += len(pairs)
        self.P = P
        # base assignment: first cluster containing the support
        self.assign = []
        for (typ, sup, c) in self.T:
            k = next(k for k in range(len(clusters)) if set(sup) <= sets[k])
            self.assign.append(k)
        self.site_assign = [next(k for k in range(len(clusters)) if i in sets[k]) for i in range(n)]
        # per-cluster structures
        self.C = []
        for k, sk in enumerate(clusters):
            m = len(sk)
            Dk = 2 ** m
            pos = {s: p for p, s in enumerate(sk)}
            xs = np.arange(Dk)
            bits = ((xs[:, None] >> np.arange(m)[None, :]) & 1)
            z = 2 * bits - 1
            pc = bits.sum(1)
            blocks = [np.where(pc == w)[0] for w in range(m + 1)]
            h0 = np.zeros((Dk, Dk))
            for t, (typ, sup, c) in enumerate(self.T):
                if self.assign[t] != k:
                    continue
                self._add_term(h0, typ, [pos[s] for s in sup], float(c), z, xs)
            zs = np.zeros(Dk)
            for i in range(n):
                if self.site_assign[i] == k:
                    zs += z[:, pos[i]]
            idx, pidx, sgn = [], [], []
            for o, (kk, ll, O) in enumerate(self.ov):
                if k not in (kk, ll):
                    continue
                s = 1.0 if k == kk else -1.0
                p0, pairs = self.par[o]
                q = len(O)
                pm = np.full((2 ** q, 2 ** q), -1, dtype=np.int64)
                for t, (a, b) in enumerate(pairs):
                    pm[a, b] = p0 + t
                    pm[b, a] = p0 + t
                A, B = np.nonzero(pm >= 0)
                op = np.array([pos[x] for x in O], dtype=np.int64)
                rest = np.array([p for p in range(m) if p not in set(op.tolist())], dtype=np.int64)
                cfg = np.arange(2 ** len(rest))
                bases = (((cfg[:, None] >> np.arange(len(rest))[None, :]) & 1) << rest[None, :]).sum(1)                     if len(rest) else np.zeros(1, dtype=np.int64)
                aa = np.arange(2 ** q)
                emb = (((aa[:, None] >> np.arange(q)[None, :]) & 1) << op[None, :]).sum(1)
                loc = bases[:, None] | emb[None, :]
                idx.append((loc[:, A] * Dk + loc[:, B]).ravel())
                pidx.append(np.tile(pm[A, B], len(bases)))
                sgn.append(np.full(len(A) * len(bases), s))
            idx = np.concatenate(idx) if idx else np.zeros(0, dtype=np.int64)
            pidx = np.concatenate(pidx) if pidx else np.zeros(0, dtype=np.int64)
            sgn = np.concatenate(sgn) if sgn else np.zeros(0)
            self.C.append(dict(m=m, D=Dk, h0=h0, zs=zs, blocks=blocks, idx=idx.astype(np.int64),
                               pidx=pidx.astype(np.int64), sgn=sgn, pos=pos, z=z, xs=xs))

    @staticmethod
    def _add_term(h, typ, ps, c, z, xs):
        if typ == "xy":
            p, q = ps
            bp, bq = (xs >> p) & 1, (xs >> q) & 1
            sel = np.where(bp != bq)[0]
            ys = sel ^ (1 << p) ^ (1 << q)
            h[ys, sel] += 2.0 * c
        elif typ == "zz":
            p, q = ps
            h[xs, xs] += c * z[:, p] * z[:, q]
        elif typ == "z":
            h[xs, xs] += c * z[:, ps[0]]

    def op_on_overlap(self, typ, sup, c, O):
        """Matrix of one term on the overlap O (local bit order = order of O)."""
        q = len(O)
        pos = {s: p for p, s in enumerate(O)}
        xs = np.arange(2 ** q)
        z = 2 * ((xs[:, None] >> np.arange(q)[None, :]) & 1) - 1
        h = np.zeros((2 ** q, 2 ** q))
        self._add_term(h, typ, [pos[s] for s in sup], c, z, xs)
        return h

    def anderson_start(self):
        """theta that spreads every term uniformly over all clusters containing its support."""
        th = np.zeros(self.P)
        sets = [set(c) for c in self.cl]
        ovi = {(k, l): o for o, (k, l, O) in enumerate(self.ov)}
        for t, (typ, sup, c) in enumerate(self.T):
            K = [k for k in range(len(self.cl)) if set(sup) <= sets[k]]
            k1 = self.assign[t]
            w = 1.0 / len(K)
            for k in K:
                if k == k1:
                    continue
                a, b = min(k, k1), max(k, k1)
                o = ovi[(a, b)]
                O = self.ov[o][2]
                M = self.op_on_overlap(typ, sup, float(c), O)
                Y = (-w * M) if k1 < k else (w * M)
                p0, pairs = self.par[o]
                for tt, (x, y) in enumerate(pairs):
                    th[p0 + tt] += Y[x, y]
        return th

    def hk(self, k, th, mu):
        C = self.C[k]
        h = C["h0"].copy().ravel()
        if len(C["idx"]):
            h += np.bincount(C["idx"], weights=th[C["pidx"]] * C["sgn"], minlength=C["D"] ** 2)
        h = h.reshape(C["D"], C["D"])
        if mu:
            h[np.arange(C["D"]), np.arange(C["D"])] += mu * C["zs"]
        return h

    def evaluate(self, x, beta=None):
        th = x[:self.P]
        mu = x[self.P] if self.use_mu else 0.0
        f = -mu * self.twoS
        g = np.zeros(self.P)
        gmu = -float(self.twoS)
        hard = -mu * self.twoS
        for k, C in enumerate(self.C):
            h = self.hk(k, th, mu)
            ev, vecs = [], []
            for I in C["blocks"]:
                w, v = np.linalg.eigh(h[np.ix_(I, I)])
                ev.append(w)
                vecs.append(v)
            allw = np.concatenate(ev)
            lmin = allw.min()
            hard += lmin
            if beta is None:
                continue
            e = np.exp(-beta * (allw - lmin))
            Z = e.sum()
            f += lmin - np.log(Z) / beta
            rho = np.zeros((C["D"], C["D"]))
            off = 0
            for I, w, v in zip(C["blocks"], ev, vecs):
                p = e[off:off + len(w)] / Z
                off += len(w)
                sel = p > 1e-14
                if sel.any():
                    vv = v[:, sel]
                    rho[np.ix_(I, I)] += (vv * p[sel]) @ vv.T
            if len(C["idx"]):
                g += np.bincount(C["pidx"], weights=C["sgn"] * rho.ravel()[C["idx"]], minlength=self.P)
            gmu += float(np.dot(np.diag(rho), C["zs"]))
        if beta is None:
            return hard
        grad = np.concatenate([g, [gmu]]) if self.use_mu else g
        return f, grad, hard


def run(graph_path, task, out_path):
    t0 = time.time()
    g = load_graph(graph_path)
    lam = frac(task.get("lam", 0))
    sp = ham_spec(g, task["kind"], frac(task["Jz"]), int(task.get("sigma", 0)), lam)
    cl = make_clusters(g, task["clusters"])
    R = Relax(g, sp, cl, use_mu=task.get("use_mu", True))
    log = dict(n_clusters=len(cl), sizes=sorted(len(c) for c in cl), n_overlaps=len(R.ov), n_params=R.P)
    print("clusters", log["n_clusters"], "sizes", sorted(set(log["sizes"])), "overlaps", len(R.ov), "params", R.P,
          flush=True)
    th0 = R.anderson_start()
    x = np.concatenate([th0, [0.0]]) if R.use_mu else th0
    f_and = R.evaluate(x)
    print("plain Anderson bound %.6f  (%.1fs)" % (f_and, time.time() - t0), flush=True)
    hist = [dict(stage="anderson", bound=f_and, t=time.time() - t0)]
    best_x, best = x.copy(), f_and
    for beta in task.get("betas", [3, 10, 30, 100, 300, 1000, 3000]):
        res = minimize(lambda y: tuple(-v for v in R.evaluate(y, beta)[:2]), x, jac=True, method="L-BFGS-B",
                       options=dict(maxiter=int(task.get("maxiter", 400)), maxcor=30, ftol=1e-13, gtol=1e-9))
        x = res.x
        hb = R.evaluate(x)
        if hb > best:
            best, best_x = hb, x.copy()
        hist.append(dict(stage="beta=%g" % beta, bound=hb, smooth=-res.fun, nit=int(res.nit), t=time.time() - t0))
        print("beta %-6g smooth %.6f hard %.6f nit %d (%.1fs)" % (beta, -res.fun, hb, res.nit, time.time() - t0),
              flush=True)
    # dyadic rounding of the multipliers and the claimed per-cluster lower bounds
    K = int(task.get("K", 32))
    sc = 2 ** K
    th_i = np.rint(best_x[:R.P] * sc).astype(np.int64)
    mu_i = int(np.rint(best_x[R.P] * sc)) if R.use_mu else 0
    thr = th_i / sc
    mur = mu_i / sc
    t_claim = []
    for k in range(len(cl)):
        h = R.hk(k, thr, mur)
        lmin = min(np.linalg.eigvalsh(h[np.ix_(I, I)]).min() for I in R.C[k]["blocks"])
        marg = 1e-9 * (1.0 + np.abs(h).sum(1).max())
        t_claim.append(int(np.floor((lmin - marg) * sc)))
    E_claim = Fraction(sum(t_claim), sc) - Fraction(mu_i, sc) * g["twoS"]
    cert = dict(graph=graph_path.replace("\\", "/").split("/")[-1],
                graph_sha256=hashlib.sha256(open(graph_path, "rb").read()).hexdigest(),
                task=task, spec=spec_to_json(sp), clusters=cl, overlaps=[[k, l, O] for (k, l, O) in R.ov],
                term_assign=R.assign, site_assign=R.site_assign, K=K,
                Y=[[[a, b, int(th_i[p0 + t])] for t, (a, b) in enumerate(pairs) if th_i[p0 + t] != 0]
                   for (p0, pairs) in R.par],
                mu=mu_i, t=t_claim, E_claim=str(E_claim), E_claim_float=float(E_claim), bound_float=best,
                anderson=f_and, history=hist, info=log, time_s=time.time() - t0)
    json.dump(cert, open(out_path, "w"))
    print("claimed E_LB %.9f (float bound %.9f, Anderson %.6f) %.1fs" % (float(E_claim), best, f_and,
                                                                       time.time() - t0), flush=True)
    return cert


if __name__ == "__main__":
    run(sys.argv[1], json.load(open(sys.argv[2])), sys.argv[3])
