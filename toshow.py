import numpy as np
import matplotlib.pyplot as plt
# 一个交作业的版本
def _delta_energy(spins, i, j, J):
    L = spins.shape[0]
    nn = spins[(i + 1) % L, j] + spins[(i - 1) % L, j] + spins[i, (j + 1) % L] + spins[i, (j - 1) % L]
    return 2 * J * spins[i, j] * nn


def _metropolis_sweep(spins, beta, J, rng):
    L = spins.shape[0]
    for _ in range(L * L):
        i = rng.integers(L)
        j = rng.integers(L)
        dE = _delta_energy(spins, i, j, J)
        if dE <= 0 or rng.random() < np.exp(-beta * dE):
            spins[i, j] *= -1


def simulate_ising(L, beta, J, burn_in, samples, rng=None):
    rng = np.random.default_rng() if rng is None else rng
    spins = rng.choice([-1, 1], size=(L, L)).astype(np.int8)
    for _ in range(burn_in):
        _metropolis_sweep(spins, beta, J, rng)

    snapshots = np.empty((L, L, samples), dtype=np.int8)
    for t in range(samples):
        _metropolis_sweep(spins, beta, J, rng)
        snapshots[:, :, t] = spins
    return snapshots


def measure(snapshots, J, beta):
    L = snapshots.shape[0]
    N = L * L
    down = np.roll(snapshots, -1, axis=0)
    right = np.roll(snapshots, -1, axis=1)

    E = (-J * (snapshots * (down + right)).sum(axis=(0, 1))).astype(float)
    M = snapshots.sum(axis=(0, 1)).astype(float)

    e = E.mean() / N
    m = np.abs(M).mean() / N
    c = beta**2 * (np.mean(E**2) - np.mean(E) ** 2) / N
    return e, m, c


def plot_curve(T, y, name):
    plt.figure(figsize=(12, 5))
    plt.plot(T, y, marker='o')
    plt.title(f'{name} vs Temperature')
    plt.xlabel('Temperature')
    plt.ylabel(name)
    plt.show()

def main():
    L, J = 20, 1.0
    burn_in, samples = 10_000, 1_000
    T = np.linspace(1.0, 4.0, 20)

    energy, magnetization, capacity = [], [], []
    rng = np.random.default_rng()

    for temp in T:
        beta = 1.0 / temp
        snaps = simulate_ising(L, beta, J, burn_in, samples, rng=rng)
        e, m, c = measure(snaps, J, beta)
        energy.append(e)
        magnetization.append(m)
        capacity.append(c)
        print(f'T={temp:.2f}, E={e:.4f}, M={m:.4f}, C={c:.4f}')

    plot_curve(T, energy, 'Energy')
    plot_curve(T, magnetization, 'Magnetization')
    plot_curve(T, capacity, 'Capacity')

if __name__ == "__main__":
    main()