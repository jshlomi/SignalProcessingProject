# Instructions to run on cluster:
## Setup
```
source setup.sh
```
In order to setup python with required libraries

## main.py
This main script is used to evaluate threshold and completeness values given a single set of parameters. It has three modes:

###### 1) calculating threshold values S_th and F_th (use --calcmode 'thr')

Inputs:
 - Selected parameters

Outputs:
 - results/TAG.txt (relevant parameters and calculated thresholds)
 - plots/TAG/ (plots of template signal, pdf of S, ...)
 
###### 2) calculating completeness with a given S_th and F_th (use --calcmode 'comp')

Inputs:
 - Selected parameters
 - results/TAG.txt (from before to get the threshold values)

Outputs:
 - results/TAG.txt (updated with completeness value for a given flux)
 - plots/out.csv (table of thresholds for given parameters)

###### 3) calculating the stdev of threshold values (use --calcmode 'thrSTD')

Inputs:
 - Selected parameters

Outputs:
 - results/TAG.csv (table of output threshold values)

Notes:
- 2) depends on 1) so they need to be run in this order
- Many parameters can be fixed, such as the bkg mean value, signal PSF width, overall flux of simulated signal, ...

For a complete list use:

```
python main.py --help
```
- The TAG is automatically generated based on the selected parameters

## run.py
This script is used for steering, submitting jobs and outputing plots. The jobs are running the main.py script described above. It will loop on provided lists of parameters.

Use for submitting jobs 'thr' and 'comp':
```
python run.py submit
```
Use for reading job results 'thr' and 'comp':
```
python run.py read
```
Use for reading job results 'thr' and 'comp' and resubmit if missing:
```
python run.py read resubmit
```
Use for submitting jobs 'thrSTD':
```
python run.py submitSTD
```
Use for reading job results 'thrSTD':
```
python run.py readSTD
```


## Suggested workflow 'thr' and 'comp':

1) In 'run.py' line 7, change value of "farmuser" to your farm username

2) In 'run.py' from line 199 edit parameters:
- fluxes - list of simulated signal overall flux values to test (the x-axis in the plots)
- paramdct_base - dictionnary of the base values for parameters B, decaycst, psfwidth and beta
- bkgmeans, decaycsts, psfwidths, betas - lists of parameter values to loop over
- N_tries - Number of tries to calculate completeness

    Note: The way the plotter is setup, it will make a plot of only of the first 3 values entered. If you add more the results will still be available in          the 'results/TAG.txt' file.
    
    Note: If you add the same value than that of the paramdct_base the job will be skipped, permitting to add the base_plot without rerunning each time on the base_parameter values.

3) python run.py submit

This command will loop on the parameters. For each parameter set, it will submit:
- 1 job to calculate threshold values
- N jobs (1 for each flux value chosen) to calculate completeness per flux value. These N jobs will be on hold until completion of the previous one.

4) python run.py read

(Upon completion of jobs)

This will loop on the result txt files and output result plots.

## Suggested workflow 'thrSTD':

1) No NEED

2) In 'run.py' from line 199 edit parameters:
- fluxes - NO NEED
- paramdct_base - dictionnary of the base values for parameters B, decaycst, psfwidth and beta
- bkgmeans, decaycsts, psfwidths, betas - NO NEED
- N_tries - Number of tries to generate pdf of the thresholds

    Note: Currently this mode will only be run once, on the basic parameter values 

3) python run.py submitSTD

For the basic parameter set, it will submit N_tries jobs to calculate N_tries distinct values of the thresholds

4) python run.py readSTD

(Upon completion of jobs)

This will loop on the result csv file and output result plots.

## Notes
- The statistics used to generate the PDF of S and calculate the thresholds is determined by the dimension of the 'large image' (--Nxy and --Nt in main.py) since we use a builtin cross-correlation method for this
- To run a quick test uncomment line 195 'RUNTEST=False' in run.py

