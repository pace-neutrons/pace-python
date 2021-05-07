#!/bin/bash

MATLAB_VER=R2020a

# Needed for mcc for some reason
yum install -y libXt

cp -rpa install_dir tmp_install_dir
cp license.lic tmp_install_dir

cat << EOF > tmp_install_dir/installer_input.txt
destinationFolder=/usr/local/MATLAB/${MATLAB_VER}
fileInstallationKey=$(cat installation_key)
agreeToLicense=yes
outputFile=`pwd`/install.log
licensePath=license.lic
product.MATLAB
product.MATLAB_Compiler
product.MATLAB_Compiler_SDK
EOF

cd tmp_install_dir
./install -inputFile installer_input.txt
ln -s /usr/local/MATLAB/${MATLAB_VER}/bin/matlab /usr/local/bin/
ln -s /usr/local/MATLAB/${MATLAB_VER}/bin/mcc /usr/local/bin/

# If you want to build an image from this container uncomment here
#tail -f /dev/null

# If you want to build a set of wheels, uncomment here
./build_script.sh
