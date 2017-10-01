#!/bin/zsh

#PBS -j oe
#PBS -o PATH/logs/farm/TAG.log
#PBS -m n
#PBS -q N
#PBS -N TAG

savelog() {
    echo "Starting on `hostname`, `date`"
    echo "jobs id: ${PBS_JOBID}"
#---------------------------------------------------------------------------------#
    python main.py --F FFF --B BBB --decaycst DDD --psfwidth PPP --beta EEE --N_tries NNN --getTH GGG
#---------------------------------------------------------------------------------#
    echo "Done, `date`"
}

cd PATH
export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase
source ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh
localSetupSFT --cmtConfig=x86_64-slc6-gcc47-opt external/pyanalysis/1.3_python2.7
savelog 2>&1 | tee PATH/logs/TAG.log
