"""Method (b): small Vision-Transformer neural quantum states (factored attention, 2x2 patches), trained by VMC with
stochastic reconfiguration in NetKet, CPU (DECLARATION.md sec. 5b). At the declared checkpoints the full S^z = 0
wavefunction is computed and evaluated exactly with wlib.Ops.

  python vit_w.py <SB> <J2> <size S|M|L> <seed>       -> out/methods/vit_<J2>_<size>_s<seed>.json
"""
import os
import sys
import time

import numpy as np

import wlib

SIZES = {"S": dict(d=8, layers=1, heads=2), "M": dict(d=16, layers=2, heads=2), "L": dict(d=32, layers=2, heads=4)}
CHECKPOINTS = [10, 25, 50, 100, 200, 400, 700, 1000, 1500, 2000]
N_ITER = 2000
WALL_CAP = 80 * 60.0
N_SAMPLES, N_CHAINS, N_DISCARD = 1024, 16, 16
LR = 0.02


def make_model(lat, size):
    import flax.linen as nn
    import jax.numpy as jnp
    cfg = SIZES[size]
    LX, LY, b = lat.LX, lat.LY, 2
    PX, PY = LX // b, LY // b
    P = PX * PY
    rel = np.zeros((P, P), dtype=np.int32)
    for i in range(P):
        for j in range(P):
            dx = ((i // PY) - (j // PY)) % PX
            dy = ((i % PY) - (j % PY)) % PY
            rel[i, j] = dx * PY + dy
    maskA = jnp.asarray((lat.eps == 1).astype(np.float64))
    d, H, nl = cfg["d"], cfg["heads"], cfg["layers"]

    class FactoredAttention(nn.Module):
        @nn.compact
        def __call__(self, x):
            B = x.shape[0]
            alpha = self.param("alpha", nn.initializers.normal(0.02), (H, P))
            A = alpha[:, rel]                                   # (H, P, P), depends on relative patch position only
            v = nn.Dense(d, use_bias=False, param_dtype=jnp.float64)(x).reshape(B, P, H, d // H)
            y = jnp.einsum("hij,bjhc->bihc", A, v).reshape(B, P, d)
            return nn.Dense(d, param_dtype=jnp.float64)(y)

    class Block(nn.Module):
        @nn.compact
        def __call__(self, x):
            x = x + FactoredAttention()(nn.LayerNorm(param_dtype=jnp.float64)(x))
            y = nn.LayerNorm(param_dtype=jnp.float64)(x)
            y = nn.Dense(2 * d, param_dtype=jnp.float64)(y)
            y = nn.gelu(y)
            y = nn.Dense(d, param_dtype=jnp.float64)(y)
            return x + y

    class ViT(nn.Module):
        @nn.compact
        def __call__(self, sigma):
            s = sigma.reshape(-1, LX * LY).astype(jnp.float64)
            g = s.reshape(-1, PX, b, PY, b).transpose(0, 1, 3, 2, 4).reshape(-1, P, b * b)
            x = nn.Dense(d, param_dtype=jnp.float64)(g)
            for _ in range(nl):
                x = Block()(x)
            z = nn.LayerNorm(param_dtype=jnp.float64)(x).sum(axis=1)
            out = nn.Dense(2, param_dtype=jnp.float64, kernel_init=nn.initializers.normal(0.01))(z)
            marshall = jnp.pi * ((s > 0) * maskA).sum(axis=-1)
            res = out[:, 0] + 1j * (out[:, 1] + marshall)
            return res.reshape(sigma.shape[:-1])

    return ViT()


def netket_objects(lat, J2, model, seed, n_samples=N_SAMPLES):
    import netket as nk
    n = lat.n
    hi = nk.hilbert.Spin(s=0.5, N=n, total_sz=0)
    ssm = np.array([[0.25, 0, 0, 0], [0, -0.25, 0.5, 0], [0, 0.5, -0.25, 0], [0, 0, 0, 0.25]])
    bonds = [[i, j] for (i, j, _) in lat.j1()]
    mats = [ssm] * len(bonds)
    if J2 != 0.0:
        b2 = [[i, j] for (i, j) in lat.j2()]
        bonds += b2
        mats += [J2 * ssm] * len(b2)
    Hop = nk.operator.LocalOperator(hi, mats, bonds, dtype=np.float64)
    edges = [(i, j) for (i, j) in bonds]
    graph = nk.graph.Graph(edges=edges)
    sampler = nk.sampler.MetropolisExchange(hi, graph=graph, d_max=1, n_chains=N_CHAINS)
    vs = nk.vqs.MCState(sampler, model, n_samples=n_samples, n_discard_per_chain=N_DISCARD,
                        seed=wlib.seed_of("vit-init", seed), sampler_seed=wlib.seed_of("vit-sampler", seed))
    return nk, hi, Hop, vs


def make_driver(nk, Hop, vs):
    """VMC + SR with lr 0.02 and diag_shift 1e-2 * 0.995^t (floor 1e-4); falls back to VMC_SR if the
    preconditioner keyword is not accepted by this NetKet version (same update rule)."""
    import optax
    ds = optax.exponential_decay(1e-2, transition_steps=1, decay_rate=0.995, end_value=1e-4)
    try:
        sr = nk.optimizer.SR(diag_shift=ds)
        return nk.driver.VMC(Hop, nk.optimizer.Sgd(learning_rate=LR), variational_state=vs, preconditioner=sr), "VMC+SR"
    except TypeError:
        return nk.driver.VMC_SR(Hop, nk.optimizer.Sgd(learning_rate=LR), diag_shift=ds, variational_state=vs), "VMC_SR"


def exact_vector(model, variables, basis, n, chunk=32768):
    import jax
    f = jax.jit(lambda v, x: model.apply(v, x))
    out = []
    for s in range(0, basis.size, chunk):
        out.append(np.asarray(f(variables, wlib.int_to_pm(basis[s:s + chunk], n))))
    lp = np.concatenate(out)
    lp = lp - lp.real.max()
    return np.exp(lp)


def main(SB, J2, size, seed):
    import jax
    import optax
    J2 = float(J2); seed = int(seed)
    od = os.path.join(SB, "out", "methods"); os.makedirs(od, exist_ok=True)
    out = os.path.join(od, "vit_%g_%s_s%d.json" % (J2, size, seed))
    lat = wlib.Lattice(6, 4)
    model = make_model(lat, size)
    nk, hi, Hop, vs = netket_objects(lat, J2, model, (J2, size, seed))
    nparam = int(sum(x.size for x in jax.tree_util.tree_leaves(vs.parameters)))
    print(wlib.now(), "ViT J2=%g size=%s seed=%d params=%d jax %s netket %s devices %s" % (
        J2, size, seed, nparam, jax.__version__, nk.__version__, jax.devices()), flush=True)
    ops = {}
    rows = []
    t_start = time.time()
    state = {"stop": False}

    def evaluate(step, mc):
        if "ops" not in ops:
            ops["ops"] = wlib.Ops(lat, J2)
        o = ops["ops"]
        t0 = time.time()
        v = exact_vector(model, vs.variables, o.basis, lat.n)
        ev = o.evaluate(v)
        row = {"method": "ViT", "J2": J2, "label": "%s_s%d_step%d" % (size, seed, step), "size": size, "seed": seed,
               "step": step, "params": nparam, "mc_energy_per_site": mc, "train_seconds": time.time() - t_start,
               "eval_seconds": time.time() - t0, **ev}
        rows.append(row)
        print(wlib.now(), "step=%d e=%.10f ms=%.8f dim=%.8f S2=%.3e mc=%s eval %.0fs" % (
            step, ev["e"], ev["ms"], ev["dim"], ev["S2"], mc, row["eval_seconds"]), flush=True)
        wlib.dump(out, {"J2": J2, "size": size, "seed": seed, "params": nparam, "rows": rows, "done": False})

    def callback(step, log_data, driver):
        mc = None
        try:
            mc = float(np.real(log_data["Energy"].mean)) / lat.n
        except Exception:
            pass
        if step % 50 == 0:
            print(wlib.now(), "iter %d mc_e=%s elapsed %.0fs" % (step, mc, time.time() - t_start), flush=True)
        if step in CHECKPOINTS:
            evaluate(step, mc)
        if time.time() - t_start > WALL_CAP:
            if step not in CHECKPOINTS:
                evaluate(step, mc)
            state["stop"] = True
            print(wlib.now(), "wall cap reached at step %d" % step, flush=True)
            return False
        return True

    gs, kind = make_driver(nk, Hop, vs)
    print(wlib.now(), "driver", kind, flush=True)
    gs.run(n_iter=N_ITER + 1, callback=callback, show_progress=False)
    wlib.dump(out, {"J2": J2, "size": size, "seed": seed, "params": nparam, "rows": rows, "done": True, "driver": kind,
                    "wall_cap_hit": state["stop"], "seconds": time.time() - t_start, "time": wlib.now()})


if __name__ == "__main__":
    main(*sys.argv[1:])
