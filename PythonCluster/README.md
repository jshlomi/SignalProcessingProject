# Instructions to run on cluster:
## Setup
```
source setup.sh
```
In order to setup python with required libraries

## main.py
This main script is used to evaluate the method given a single set of parameters. It has two functions:

1) calculating threshold values S_th and F_th (use --getTh 1)
Inputs:
 - Selected parameters
Outputs:
 - results/TAG.txt (relevant parameters and calculated thresholds)
 - plots/TAG/ (plots of template signal, pdf of S, ...)
 
2) calculating completeness with a given S_th and F_th (use --getTH 0)
Inputs:
 - Selected parameters
 - results/TAG.txt (from before to get the threshold values)
Outputs:
 - results/TAG.txt (updated with completeness value for a given flux)
 - plots/out.csv (table of thresholds for given parameters)

Note: 2) depends on 1) so they need to be run in this order
      Many parameters can be fixed, such as the bkg mean value, signal PSF width, overall flux of simulated signal, ...
      For a complete list use:
```
python main.py --help
```
Note: The TAG is automatically generated based on the selected parameters

## run.py
This script is used for steering, submitting jobs and outputing plots. The jobs are running the main.py script described above. It will loop on provided lists of parameters.

Use for submitting jobs:
```
python run.py submit
```
Use for reading job results:
```
python run.py read
```
Use for reading job results and resubmit if missing:
```
python run.py read resubmit
```

## Suggested workflow

1) In 'run.py' line 7, change value of "farmuser" to your farm username

2) In 'run.py' from line 175 edit parameters:
fluxes - list of simulated signal overall flux values to test (the x-axis in the plots)
paramdct_base - dictionnary of the base values for parameters B, decaycst, psfwidth and beta
bkgmeans, decaycsts, psfwidths, betas - lists of parameter values to loop over
Ntries - Number of tries to calculate completeness
    Note: The way the plotter is setup, it will make a plot of only of the first 3 values entered. If you add more the results will still be available in          the 'results/TAG.txt' file.
    Note: If you add the same value than that of the paramdct_base the job will be skipped, permitting to add the base_plot without rerunning each time on the base_parameter values.

3) python run.py submit
This command will loop on the parameters. For each parameter set, it will submit:
- 1 job to calculate threshold values
- N jobs (1 for each flux value chosen) to calculate completeness per flux value. These N jobs will be on hold until completion of the previous one.

4) python run.py read
(Upon completion of jobs)
This will loop on the result txt files and output result plots.

## Notes
- The statistics used to generate the PDF of S and calculate the thresholds is determined by the dimension of the 'large image' (--Nxy and --Nt in main.py) since we use a builtin cross-correlation method for this

