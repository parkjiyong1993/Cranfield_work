# Cranfield university internship 2023
### School of Aerospace, Transport and Manufacturing
### Centre for Propulsion and Thermal Power Engineering – Rolls-Royce UTC
<br />
<br />

## :  GUI for NPSS(Numerical Propulsion System Simulation) input

## 2023-06-27
#### Data format : 
1. extension : .map
2. standard : Extracted from Turbomatch Map Library (09/2021) by Christos Nixarlidis.

#### Parsing :
1. Re library
2. fan.map  (PR, Wc depends on the same Nc, each beta)<br />
   beta_Nc_Wc = re.findall(r'beta = (\d+)\s+{\s+Nc =  {(.*?)\}\s+Wc =  {(.*?)}', data, re.DOTALL) <br />
   beta_Nc_PR = re.findall(r'beta = (\d+)\s+{\s+Nc =  {(.*?)\}\s+PR =  {(.*?)}', data, re.DOTALL)

4. turbine.map (dHqT, Wc, each Nc)<br />
   turbine_Nc_dHqT= re.findall(r"Nc\s*=\s*(.*?)\s*{\s*dHqT\s*=\s*{(.*?)}", data, re.DOTALL) <br />
   turbine_Nc_Wc = re.findall(r"Nc\s*=\s*(.*?)\s*{\s*dHqT\s*=.*?\s*Wc\s*=\s*{(.*?)}", data, re.DOTALL)

5. HPC.map ->

#### Plot : 
1. matplotlib
2. Fan.map -> x axis : pressure ratio(PR) , y axis : corrected mass flow(Wc)
3. Turbine.map ->  x axis : dHqT, y axis : corrected mass flow(Wc)
4. HPC.map ->

