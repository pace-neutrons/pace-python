#!/bin/bash
cd /mnt/installer
matlab -nodesktop -r "try, run('make_package.m'), catch ME, fprintf('%s: %s\n', ME.identifier, ME.message), end, exit"
