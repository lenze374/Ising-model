# filepath: 
import numpy as np
import matplotlib.pyplot as plt
from numba import jit, prange # 引入 Numba
from concurrent.futures import ProcessPoolExecutor # 引入多进程
import time

# 1. 使用 Numba 加速核心计算函数
# nopython=True 表示完全编译为机器码，不使用 Python 解释器
@jit(nopython=True)
def _get_dE(site, i, j, J):
    L = site.shape[0]
    # Numba 不支持负索引取模的某些写法，最好显式处理
    ip = (i + 1) % L
    im = (i - 1 + L) % L
    jp = (j + 1) % L
    jm = (j - 1 + L) % L
    
    dE = 2 * J * site[i,j] * (site[ip,j] + site[i,jp] + site[im,j] + site[i,jm])
    return dE

@jit(nopython=True)
def solve_ising_numba(L, beta, J, n_steps, c_steps):
    # 冷启动
    site = np.ones((L, L), dtype=np.int8)
    
    # 预热阶段
    for step in range(n_steps):
        for _ in range(L*L):
            i = np.random.randint(0, L)
            j = np.random.randint(0, L)
            dE = _get_dE(site, i, j, J)
            if dE <= 0 or np.random.random() < np.exp(-beta * dE):
                site[i,j] *= -1

    # 测量阶段 (在线计算)
    energy_sum = 0.0
    magnetization_sum = 0.0
    energy2_sum = 0.0
    
    for step in range(c_steps):
        # Metropolis Sweep
        for _ in range(L*L):
            i = np.random.randint(0, L)
            j = np.random.randint(0, L)
            dE = _get_dE(site, i, j, J)
            if dE <= 0 or np.random.random() < np.exp(-beta * dE):
                site[i,j] *= -1
        
        # 计算当前帧的 E 和 M
        # 虽然这里有双重循环，但因为是在 Numba 内部，速度非常快
        current_E = 0.0
        current_M = 0.0
        for i in range(L):
            for j in range(L):
                ip = (i + 1) % L
                jp = (j + 1) % L
                # 只计算右和下邻居
                current_E -= J * site[i,j] * (site[ip,j] + site[i,jp])
                current_M += site[i,j]
        
        energy_sum += current_E
        magnetization_sum += abs(current_M)
        energy2_sum += current_E ** 2

    # 计算统计平均值
    energy_avg = energy_sum / c_steps / (L * L)
    magnetization_avg = magnetization_sum / c_steps / (L * L)
    
    term1 = energy2_sum / c_steps / (L * L)
    term2 = (energy_avg ** 2) * (L * L)
    capacity = beta**2 * (term1 - term2)
    
    return energy_avg, magnetization_avg, capacity

# 2. 包装单个任务函数，用于多进程调用
def run_single_temperature(args):
    T, L, J, n_steps, c_steps = args
    beta = 1.0 / T
    # 直接返回计算结果，不再传递巨大的 site 数组
    return T, *solve_ising_numba(L, beta, J, n_steps, c_steps)

def plot_properties(temperatures, property , property_name):
    plt.figure(figsize=(10, 5))
    plt.plot(temperatures, property, 'o-', markersize=5)
    plt.title(f'{property_name} vs Temperature')
    plt.xlabel('Temperature')
    plt.ylabel(f'{property_name}')
    plt.grid(True)
    plt.show()


def main():
    L = 200
    J = 1.0
    n_steps = 200000 # 增加步数，因为现在速度很快
    c_steps = 100000
    temperatures = np.linspace(1.0, 2.0, 10).tolist() + np.linspace(2.0, 2.5, 40).tolist() + np.linspace(2.5, 4.0, 15).tolist() # 增加采样点
    
    properties = {'energy': [], 'magnetization': [], 'capacity': []}
    
    # 准备参数列表
    tasks = [(T, L, J, n_steps, c_steps) for T in temperatures]
    
    print(f"Starting simulation on {len(tasks)} temperatures using Multiprocessing + Numba...")
    start_time = time.time()

    # 3. 使用 ProcessPoolExecutor 进行多核并行
    # max_workers 默认等于 CPU 核心数
    results = []
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(run_single_temperature, tasks))
    
    # 排序结果（因为多进程返回顺序可能乱序，虽然 map 通常保持顺序，但保险起见）
    results.sort(key=lambda x: x[0])
    
    # 解包数据
    sorted_temps = []
    for res in results:
        T, e, m, c = res
        sorted_temps.append(T)
        properties['energy'].append(e)
        properties['magnetization'].append(m)
        properties['capacity'].append(c)
        print(f'T: {T:.2f}, E: {e:.4f}, M: {m:.4f}, Cv: {c:.4f}')

    print(f"Total time: {time.time() - start_time:.2f} seconds")

    plot_properties(sorted_temps, properties['energy'], 'Energy')
    plot_properties(sorted_temps, properties['magnetization'], 'Magnetization')
    plot_properties(sorted_temps, properties['capacity'], 'Capacity')

if __name__ == "__main__":
    main()