import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from gekko import GEKKO
df = pd.read_excel("PSPEREF.xlsx")



eolic_output_year = df["Parque Eólico Ref [kW]"].to_numpy() / 1000 # MW
solar_output_year = df["Parque Solar Ref [kW]"].to_numpy() / 1000 # MW

eolic_ac_ref = 70 # MW (Palomas vestas)
solar_ac_ref = 50 # MW (La Jacinta)

print(eolic_output_year)

list_solar_output_day = solar_output_year[:10*24]
list_eolic_output_day = eolic_output_year[:10*24]


length_of_a_day = len(list_solar_output_day)



g = GEKKO(remote=False)
g.options.MAX_ITER = 2000
g.options.IMODE = 3
g.options.SOLVER = 1


# PV variables
solar_capacity_param = g.Array(g.Param, length_of_a_day)
pv_sizing_corr = g.MV(value=100, lb=90, ub=150) # 1 MW
pv_sizing_corr.STATUS = 1

# PE variables
eolic_capacity_param = g.Array(g.Param, length_of_a_day)
eol_sizing_corr = g.MV(value=100, lb=90, ub=150) # 1 MW
eol_sizing_corr.STATUS = 1


# Electrolyzer

possbile_h2_prod_from_avail_energy = g.Array(g.Var, length_of_a_day)
switch_electrolyzer_min_1 = g.Array(g.Var, length_of_a_day, integer=True, lb=0,ub=1)
switch_electrolyzer_min_2 = g.Array(g.Var, length_of_a_day, integer=True, lb=0,ub=1)

switch_electrolyzer_max_1 = g.Array(g.Var, length_of_a_day, integer=True, lb=0,ub=1)
switch_electrolyzer_max_2 = g.Array(g.Var, length_of_a_day, integer=True, lb=0,ub=1)


el_sizing = g.MV(value=100, lb=90, ub=120)
el_sizing.STATUS = 1

el_min = g.Var()
g.Equation( el_min == 0.1 * el_sizing)


# Tank
h2_stored = g.Array(g.Var, length_of_a_day)
#tank_max = g.MV(lb= 0, ub=200000)
#tank_max.STATUS = 1
tank_init = g.Param(value=10000)
h2_out_per_hour = g.Param(value= 1000)


solar_power = g.Array(g.Var, length_of_a_day)
eolic_power = g.Array(g.Var, length_of_a_day)
available_energy = g.Array(g.Var, length_of_a_day)

g.Equation(h2_stored[0] == tank_init + possbile_h2_prod_from_avail_energy[0] - h2_out_per_hour)  
#g.Equation(h2_stored[-1] >= tank_init)
#g.Equation(tank_max>=tank_init)

for i in range(length_of_a_day):
    # Tank Equations
    #g.Equation(h2_stored[i] <= tank_max)
    #g.Equation(h2_stored[i] >= 0)
    if i >=1:
        g.Equation(h2_stored[i] == h2_stored[i-1] + possbile_h2_prod_from_avail_energy[i] - h2_out_per_hour)

    
    #Energy equations
    g.Equation(solar_power[i] == solar_capacity_param[i] * (pv_sizing_corr / solar_ac_ref))
    g.Equation(eolic_power[i] == eolic_capacity_param[i] * (eol_sizing_corr / eolic_ac_ref))
    g.Equation(available_energy[i] == solar_power[i] + eolic_power[i])
    
    
    # Electrolyzer Equations
    g.Equation(switch_electrolyzer_min_1[i] * (available_energy[i]-el_min) >=0)
    g.Equation(switch_electrolyzer_min_2[i] * (el_min-available_energy[i]) >=0)
    g.Equation(switch_electrolyzer_min_1[i] + switch_electrolyzer_min_2[i] == 1)

    g.Equation(switch_electrolyzer_max_1[i] * (el_sizing - available_energy[i]) >=0) # if available > than max size then switch = 0
    g.Equation(switch_electrolyzer_max_2[i] * (available_energy[i]-el_sizing) >=0)
    g.Equation(switch_electrolyzer_max_2[i] + switch_electrolyzer_max_1[i] == 1)

    g.Equation(possbile_h2_prod_from_avail_energy[i] == 18 * switch_electrolyzer_min_1[i] * (available_energy[i] * (1-switch_electrolyzer_max_2[i])
                                                                + el_sizing *switch_electrolyzer_max_2[i]))

    

    


#g.Minimize(el_sizing + pv_sizing_corr)




for i in range(length_of_a_day):
    solar_capacity_param[i].value = list_solar_output_day[i]
    eolic_capacity_param[i].value = list_eolic_output_day[i]


g.options.SOLVER = 1
g.solve(disp=True)


print(possbile_h2_prod_from_avail_energy)
print(h2_stored)
print()




