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
amount_of_hours = 24*365

list_solar_output_day = solar_output_year[:amount_of_hours]
list_eolic_output_day = eolic_output_year[:amount_of_hours]


length_of_a_day = len(list_solar_output_day)



g = GEKKO(remote=False)
g.options.MAX_ITER = 2000
g.options.IMODE = 3


# PV variables
solar_capacity_param = g.Array(g.Param, length_of_a_day)
pv_sizing_corr = g.MV(value=100, lb=0) # 1 MW
pv_sizing_corr.STATUS = 1

# PE variables
eolic_capacity_param = g.Array(g.Param, length_of_a_day)
eol_sizing_corr = g.MV(value=100, lb=0) # 1 MW
eol_sizing_corr.STATUS = 1


solar_power = g.Array(g.Var, length_of_a_day)
eolic_power = g.Array(g.Var, length_of_a_day)
total_energy = g.Array(g.Var, length_of_a_day)



for i in range(length_of_a_day):
        
    #Energy equations
    g.Equation(solar_power[i] == solar_capacity_param[i] * (pv_sizing_corr / solar_ac_ref))
    g.Equation(eolic_power[i] == eolic_capacity_param[i] * (eol_sizing_corr / eolic_ac_ref))
    g.Equation(total_energy[i] == solar_power[i] + eolic_power[i])
    solar_capacity_param[i].value = list_solar_output_day[i]
    eolic_capacity_param[i].value = list_eolic_output_day[i]




g.Equation(g.sum(total_energy) == (850000*(amount_of_hours/8760)))



g.Minimize( pv_sizing_corr* 500000 + eol_sizing_corr * 1100000)
g.options.SOLVER = 1
g.solve(disp=True)
print(pv_sizing_corr.VALUE)
print(eol_sizing_corr.VALUE)
sum = 0
for element in total_energy:
    sum += element.value[0]

print(sum)






