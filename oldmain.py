import numpy as np
import matplotlib.pyplot as plt
# 2-D Ising Model Simulation
def _get_dE(site, i, j, J):
    L = site.shape[0]
    dE = 2 * J * site[i,j] * (site[(i+1)%L,j] + site[i,(j+1)%L] + site[(i-1)%L,j] + site[i,(j-1)%L])
    return dE

def ising_simulation(L, beta, J, n_steps, c_steps):
    site = np.random.choice([-1, 1], size=(L, L))
    sites = np.zeros((L, L, c_steps)) 
    L = site.shape[0]
    for step in range(n_steps):
        for _ in range(L*L):
            i = np.random.randint(0, L)
            j = np.random.randint(0, L)
            dE = _get_dE(site, i, j, J)
            if dE <= 0 or np.random.rand() < np.exp(-beta * dE):
                site[i,j] *= -1
    for step in range(c_steps):
        for _ in range(L*L):
            i = np.random.randint(0, L)
            j = np.random.randint(0, L)
            dE = _get_dE(site, i, j, J)
            if dE <= 0 or np.random.rand() < np.exp(-beta * dE):
                site[i,j] *= -1
        sites[:,:,step] = site
    return sites

def get_one_site_properties(site, J, L):
    term_down = np.roll(site, -1, axis=0)
    term_right = np.roll(site, -1, axis=1)
    
    energy = -J * np.sum(site * (term_down + term_right))
    magnetization = np.sum(site)
    return energy, magnetization

def _get_properties(sites, J, beta):
    L = sites.shape[0]
    steps = sites.shape[2]
    energy = 0.0
    magnetization = 0.0
    energy2 = 0.0
    for _ in range(steps):
        e, m = get_one_site_properties(sites[:,:, _], J, L)
        energy += e
        magnetization += abs(m)
        energy2 += e ** 2
    energy /= steps * (L * L)
    magnetization /= steps * (L * L)
    capacity = beta**2 * (energy2 / steps / (L * L)- energy ** 2 * (L * L))
    return energy, magnetization, capacity

def plot_properties(temperatures, property , property_name):
    plt.figure(figsize=(12, 5))
    plt.plot(temperatures, property, marker='o')
    plt.title(f'{property_name} vs Temperature')
    plt.xlabel('Temperature')
    plt.ylabel(f'{property_name}')
    plt.show()

def main():
    L = 20
    J = 1.0
    n_steps = 10000
    c_steps = 1000
    temperatures = np.linspace(1.0, 4.0, 20)
    beta_linspace =  1.0 / temperatures
    properties = {'energy': [], 'magnetization': [], 'capacity': []}

    for beta in beta_linspace:
        site = ising_simulation(L, beta, J, n_steps, c_steps)
        energy, magnetization, capacity = _get_properties(site, J, beta)
        properties['energy'].append(energy)
        properties['magnetization'].append(magnetization)
        properties['capacity'].append(capacity)
        print(f'Temperature: {1/beta:.2f}, Energy: {energy:.4f}, Magnetization: {magnetization:.4f}, Capacity: {capacity:.4f}')
    
    plot_properties(temperatures, properties['energy'], 'Energy')
    plot_properties(temperatures, properties['magnetization'], 'Magnetization')
    plot_properties(temperatures, properties['capacity'], 'Capacity')

if __name__ == "__main__":
    main()