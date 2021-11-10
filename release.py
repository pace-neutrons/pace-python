import argparse
import json
import os
import re
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

    desc = re.search('# (\[v[0-9\.]*\]\(http.*\)\n.*?)# \[v[0-9\.]*\]', changelog,
                     re.DOTALL | re.MULTILINE).groups()[0].strip()
    payload = {
        "tag_name": pace_ver,
        "target_commitish": "master",
        "name": pace_ver,
        "body": desc,
        "draft": False,
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
