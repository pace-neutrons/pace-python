from libpymcr.utils import checkPath, stripmex
import os
import sys
import subprocess

if __name__ == '__main__':
    firstrun = True
    for v in ['R2021b', 'R2022a', 'R2022b', 'R2023a', 'R2023b', 'R2024a', 'R2024b']:
        print(f'Compiling for {v}')
        mlPath = checkPath(v, error_if_not_found=False, suppress_output=True)
        if mlPath is not None:
            rv = subprocess.run([os.path.join(mlPath, 'bin', 'matlab'), '-batch', 'build_ctf'], capture_output=True)
            if rv.returncode != 0:
                print(rv.stdout.decode())
                print(rv.stderr.decode())
            else:
                stripmex(v, ctfdir='ctfs', writemex=firstrun)
                if firstrun:
                    firstrun = False
        else:
            print(f'Matlab {v} not found')
