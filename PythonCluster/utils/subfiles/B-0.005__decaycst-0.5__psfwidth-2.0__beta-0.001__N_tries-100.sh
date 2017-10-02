#!/bin/zsh

#PBS -j oe
#PBS -o /srv01/agrp/mattiasb/course_dataana/SignalProcessingProject/PythonCluster/logs/farm/B-0.005__decaycst-0.5__psfwidth-2.0__beta-0.001__N_tries-100.log
#PBS -m n
#PBS -q N
#PBS -N B-0.005__decaycst-0.5__psfwidth-2.0__beta-0.001__N_tries-100

savelog() {
    echo "Starting on `hostname`, `date`"
    echo "jobs id: ${PBS_JOBID}"
#---------------------------------------------------------------------------------#
    python main.py --F -1 --B 0.005 --decaycst 0.5 --psfwidth 2.0 --beta 0.001 --N_tries 100 --calcmode thrSTD
#---------------------------------------------------------------------------------#
    echo "Done, `date`"
}

cd /srv01/agrp/mattiasb/course_dataana/SignalProcessingProject/PythonCluster
export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase
source ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh
localSetupSFT --cmtConfig=x86_64-slc6-gcc47-opt external/pyanalysis/1.3_python2.7
savelog 2>&1 | tee /srv01/agrp/mattiasb/course_dataana/SignalProcessingProject/PythonCluster/logs/B-0.005__decaycst-0.5__psfwidth-2.0__beta-0.001__N_tries-100.log
