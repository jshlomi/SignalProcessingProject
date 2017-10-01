## Used to get access to python with required libraries installed
export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase
source ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh
localSetupSFT --cmtConfig=x86_64-slc6-gcc47-opt external/pyanalysis/1.3_python2.7
