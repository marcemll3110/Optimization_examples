import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as opt



degradation_curve = np.array([1, 0.985, 0.981,	0.977,	0.973,	0.969,	0.965,	0.962,	0.958,	0.954,	0.95,	0.946,	0.943,	0.939,	0.935,	0.931,	0.928,	0.924,	0.920,	0.916])


initial_value_panel = np.array([100, 1, 1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1])

panels = np.ones((20,20))

# Array vacía de 20 x 20 para la degradación
degradation_array = np.zeros((20, 20))

# Fila n: degradación del panel instalado en el año n
for i in range(20):
    degradation_array[i, i:20] = degradation_curve[:20 - i]  # Shift values to the right

print(degradation_array)

# Create an empty 20x20 array filled with ones
panel_active = np.ones((20, 20), dtype=int)



def calculate_values(panels):
    """"
    Args: panles (array): Potencia instalada en cada año
    Returns: (array) La potencia pico de la planta para cada año     
    
    """
    # Se multiplica la potencia pico de cada panel instalado por año por la degradación que tendrá
    values = np.reshape(panels,(20,1)) * degradation_array
    sums = []
    # La suma de cada columna corresponde a la potencia total del parque para cada año
    for j in range(20):
        sums.append(np.sum(values[:,j]))

    return np.array(sums)



def obj_fun(initial_panels):
    """
    Función objetivo a minimizar. Se busca una potencia pico de 100 MW constante durante toda la vida útil del proyecto
    Args: (array) initial_panels: Valor inicial para cada panel instalado en la vida de la planta
    Returns: (float) Función de costo para minimizar

    """
    values = np.reshape(initial_panels,(20,1)) * degradation_array
    sums = []
    for j in range(20):
        sums.append(np.sum(values[:,j]))
    # Se minimiza la diferencia al cuadrado de la potencia pico de cada año menos la potencia objetivo
    return np.sum((np.array(sums)-100)**2)

print(obj_fun(initial_value_panel))


# Recapex año a año
#bounds = [(0,1000) for i in range(20)]
# Recapex cada 5 años
bounds = [(0,1000), (0,0), (0,0),(0,0),(0,0), (0,1000), (0,0), (0,0),(0,0),(0,0),(0,1000), (0,0), (0,0),(0,0),(0,0),(0,1000), (0,0), (0,0),(0,0),(0,0)]


# Se impone esta constraint para que los valores de potencia pico nunca estén por debajo de 100 MWp
c = opt.NonlinearConstraint(calculate_values, 100, 10000)


prob = opt.minimize(obj_fun, initial_value_panel, constraints=c, bounds=bounds)


print(prob.x)

print(calculate_values(prob.x))