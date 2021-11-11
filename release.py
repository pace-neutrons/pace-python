import argparse
import json
import os
import re
import sys
import requests
import subprocess
from importlib_resources import open_text
import yaml
from pace_neutrons import __version__


def main():
    parser = get_parser()
    args = parser.parse_args()

    test = not args.notest
    if args.github:
        release_github(test)

    if args.pypi:
        release_pypi(test)


def release_github(test=True):
    with open('CHANGELOG.md') as f:
        changelog = f.read()
    with open('CITATION.cff') as f:
        citation = yaml.safe_load(f)

    pace_ver = 'v' + __version__
    version_dict = {}
    version_dict['CHANGELOG.md'] = re.findall('# \[(.*)\]\(http', changelog)[0]
    version_dict['CITATION.cff'] = 'v' + citation['version']
    for ver_name, ver in version_dict.items():
        if pace_ver != ver:
            raise Exception(f'version mismatch! __version__: {pace_ver}; {ver_name}: {ver}')

    desc = re.search('# \[v[0-9\.]*\]\(http.*\)\n(.*?)# \[v[0-9\.]*\]', changelog,
                     re.DOTALL | re.MULTILINE).groups()[0].strip()
    payload = {
        "tag_name": pace_ver,
        "target_commitish": "main",
        "name": pace_ver,
        "body": desc,
        "draft": True,
        "prerelease": True
    }
    if test:
        print(payload)
    else:
        response = requests.post(
            'https://api.github.com/repos/pace-neutrons/pace-python/releases',
            data=json.dumps(payload),
            headers={"Authorization": "token " + os.environ["GITHUB_TOKEN"]})
        print(response.text)

    wheelfile = None
    if os.path.exists('dist'):
        wheelfile = [ff for ff in os.listdir('dist')][0]
        wheelpath = os.path.join('dist', wheelfile)
    elif os.path.exists('wheelhouse'):
        wheelfile = [ff for ff in os.listdir('wheelhouse') if 'manylinux' in ff][0]
        wheelpath = os.path.join('wheelhouse', wheelfile)
    if wheelfile is not None and not test:
        print(f'Uploading wheel {wheelpath}')
        upload_url = re.search('^(.*)\{\?', json.loads(response.text)['upload_url']).groups()[0]
        with open(wheelpath, 'rb') as f:
            upload_response = requests.post(
                f"{upload_url}?name={wheelfile}",
                headers={"Authorization": "token " + os.environ["GITHUB_TOKEN"],
                         "Content-type": "application/octet-stream"},
                data=f.read())
            print(upload_response.text)

    installer_path = os.path.join('installer', 'Pace_Python_Installer')
    if os.path.exists(installer_path) and not test:
        installer_file0 = [ff for ff in os.listdir(installer_path) if 'MyAppInstaller' in ff][0]
        installer_file = installer_file0.replace('MyAppInstaller', f'pace_neutrons_installer_{sys.platform}')
        os.rename(os.path.join(installer_path, installer_file0), installer_file)
        print(f'Uploading installer {installer_file}')
        with open(installer_file, 'rb') as f:
            upload_response = requests.post(
                f"{upload_url}?name={installer_file}",
                headers={"Authorization": "token " + os.environ["GITHUB_TOKEN"],
                         "Content-type": "application/octet-stream"},
                data=f.read())
            print(upload_response.text)
    

def release_pypi(test=True):
    subprocess.run(['rm','-r','dist'])
    subprocess.run(['rm','-r','build'])
    subprocess.run(['python', 'setup.py', 'sdist'])
    if not test:
        subprocess.run(['twine', 'upload', 'dist/*'])


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--github',
        action='store_true',
        help='Release on Github')
    parser.add_argument(
        '--pypi',
        action='store_true',
        help='Release on PyPI')
    parser.add_argument(
        '--notest',
        action='store_true',
        help='Actually send/upload')
    return parser


if __name__ == '__main__':
    main()
