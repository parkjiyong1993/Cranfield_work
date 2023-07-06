# Cranfield university internship 2023
### School of Aerospace, Transport and Manufacturing
### Centre for Propulsion and Thermal Power Engineering – Rolls-Royce UTC
<br />
<br />

## :  GUI for NPSS(Numerical Propulsion System Simulation) input

<details>   
<summary style="font-size: 20px;">2023-06-27</summary>

#### Data format : 
1. extension : .map
2. standard : Extracted from Turbomatch Map Library (09/2021) by Christos Nixarlidis.

#### Parsing :
1. Re library
2. fan.map  (PR, Wc depends on the same Nc, each beta)<br />
```
   beta_Nc_Wc = re.findall(r'beta = (\d+)\s+{\s+Nc =  {(.*?)\}\s+Wc =  {(.*?)}', data, re.DOTALL) <br />
   beta_Nc_PR = re.findall(r'beta = (\d+)\s+{\s+Nc =  {(.*?)\}\s+PR =  {(.*?)}', data, re.DOTALL)
```

3. turbine.map (dHqT, Wc, each Nc)<br />
```
   turbine_Nc_dHqT= re.findall(r"Nc\s*=\s*(.*?)\s*{\s*dHqT\s*=\s*{(.*?)}", data, re.DOTALL) <br />
   turbine_Nc_Wc = re.findall(r"Nc\s*=\s*(.*?)\s*{\s*dHqT\s*=.*?\s*Wc\s*=\s*{(.*?)}", data, re.DOTALL)
```

4. HPC.map ->

#### Plot : 
1. matplotlib
2. Fan.map -> x axis : pressure ratio(PR) , y axis : corrected mass flow(Wc)
3. Turbine.map ->  x axis : dHqT, y axis : corrected mass flow(Wc)
4. HPC.map ->

</details>


<details>   
<summary style="font-size: 20px;">2023-06-30</summary>

#### HPC(High Performance Computing)

#### Data format :
1. HPC.map :
   
   Table TB_Wc(real beta, real Nc){

VIGV = 0 {
    beta = 1  {
		Nc =  {0.5000, 0.5300, 0.5700, 0.6000, 0.6400}
		Wc =  {21.4000, 22.4900, 23.6960, 25.0040, 26.4140}
	}
    beta = 2  {
		Nc =  {0.5000, 0.5300, 0.5700, 0.6000, 0.6400}
		Wc =  {21.3510, 22.4610, 23.6830, 25.0020, 26.4150}
	}
	
}

VIGV = 3 {
    beta = 1  {
		Nc =  {0.5000, 0.5300, 0.5700, 0.6000, 0.6400}
		Wc =  {21.4000, 22.4900, 23.6960, 25.0040, 26.4140}
	}
    beta = 2  {
		Nc =  {0.5000, 0.5300, 0.5700, 0.6000, 0.6400}
		Wc =  {21.3510, 22.4610, 23.6830, 25.0020, 26.4150}
	}
}
}

1. not nested
2. regular

#### Parsing :

1. root window -> load file -> plot window -> VIGV value selection(another window) -> beta selection -> plot
2. Parsed data form(VIGV, beta, Nc, Wc or PR): 
\[('0', '1', '0.5000, 0.5300, 0.5700, 0.6000, 0.6400', '21.4000, 22.4900, 23.6960, 25.0040, 26.4140'),('0', '2', '0.5000, 0.5300, 0.5700, 0.6000, 0.6400', '21.3510, 22.4610, 23.6830, 25.0020, 26.4150'),('3', '1', '0.5000, 0.5300, 0.5700, 0.6000, 0.6400', '21.4000, 22.4900, 23.6960, 25.0040, 26.4140'), ('3', '2', '0.5000, 0.5300, 0.5700, 0.6000, 0.6400', '21.3510, 22.4610, 23.6830, 25.0020, 26.4150')]

3. HPC.map(VIGV, beta, Nc, Wc or PR): 

```
   	vigv_blocks = re.findall(r'(VIGV = \d+ \{.*?\})', data, re.DOTALL)
   
        beta_Nc_Wc = []
        beta_Nc_PR = []

        # Iterate over each VIGV block
        for block in vigv_blocks:
            # Extract VIGV value
            vigv = re.search(r'VIGV = (\d+)', block).group(1)
            
            # Extract all beta, Nc, Wc within this block
            block_beta_Nc_Wc = re.findall(r'beta = (\d+)\s+{\s+Nc =  {(.*?)\}\s+Wc =  {(.*?)}', data, re.DOTALL)
            # Extract all beta, Nc, PR within this block
            block_beta_Nc_PR = re.findall(r'beta = (\d+)\s+{\s+Nc =  {(.*?)\}\s+PR =  {(.*?)}', data, re.DOTALL)

            # For each beta, Nc, Wc set, append it along with VIGV value to the result
            for beta, nc, wc in block_beta_Nc_Wc:
                beta_Nc_Wc.append((vigv, beta, nc, wc))

            # For each beta, Nc, PR set, append it along with VIGV value to the result
            for beta, nc, pr in block_beta_Nc_PR:
                beta_Nc_PR.append((vigv, beta, nc, pr))

        beta_values = [int(beta) for _, beta, _, _ in beta_Nc_Wc]
```

5. 2 scroll listboxes cannot be selected in one window for Tkinter.
6. Parameter managing for VIGV -> global plot_window -> condition when plot the new window.

#### Plot :
1. The same as a compressor, Fan.map, except the selection of VIGV value in advance.
 
</details>


<details>   
<summary style="font-size: 20px;">2023-07-04</summary>
1. VIGV selection button update, optimized
	
2. subplot vs figure for matlablib

#### Nc plot function for HPC:
   Nc values plotted for every selection of VIGV
  => parsing error for data : ```re.findall``` with ```data``` parameter, it shares the data inside. <br>
  => ```block``` parameter has to be used. (iteration is not necessary)
      
   
	```
	vigv_blocks = re.findall(r'(VIGV\s+=\s+\d+\s+\{[^{}]*?(?:\{[^{}]*?(?:\{[^{}]*?\}[^{}]*?)*?\}[^{}]*?)*?\})', data, re.DOTALL)

        beta_Nc_Wc = []
        beta_Nc_PR = []
        beta_Nc = []

        # Iterate over each VIGV block
        for block in vigv_blocks:
            # Extract VIGV value
            vigv = re.search(r'VIGV\s+=\s+(\d+)', block).group(1)
            #print(block)
            
            beta_blocks = re.findall(r'(beta\s+=\s+\d+\s+\{[^{}]*?(?:\{[^{}]*?\}[^{}]*?)*?\})', block, re.DOTALL)
            
            for beta_block in beta_blocks:
                beta = re.search(r'beta\s+=\s+(\d+)', beta_block).group(1)
                nc = re.search(r'Nc\s+=\s+\{([^\}]*)\}', beta_block).group(1)
                wc = re.search(r'Wc\s+=\s+\{([^\}]*)\}', beta_block).group(1) if re.search(r'Wc\s+=\s+\{([^\}]*)\}', beta_block) else None
                pr = re.search(r'PR\s+=\s+\{([^\}]*)\}', beta_block).group(1) if re.search(r'PR\s+=\s+\{([^\}]*)\}', beta_block) else None
                
                if wc is not None:
                    beta_Nc_Wc.append((vigv, beta, nc, wc))
                
                if pr is not None:
                    beta_Nc_PR.append((vigv, beta, nc, pr))

                beta_Nc.append((vigv, beta, nc))

        beta_values = [int(beta) for _, beta, _, _ in beta_Nc_Wc]
	```
</details>

<details>   
<summary style="font-size: 20px;">2023-07-06</summary>
1. album issue with VIGV selection is corrected.
2. 
</details>


## :  GUI for NPSS(Numerical Propulsion System Simulation) output post-processing

## :  Compressor mean-line code
