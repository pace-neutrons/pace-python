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
from pace_neutrons_cli.utils import release_exists, download_github

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

    desc = re.search('# \[v[0-9\.]*\]\(http.*?\)\n(.*?)# \[v[0-9\.]*\]', changelog,
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
        upload_url = release_exists(pace_ver, retval='upload_url')
        if not upload_url:
            upload_url = _create_gh_release(payload)
        else:
            upload_url = re.search('^(.*)\{\?', upload_url).groups()[0]
        _upload_assets(upload_url)


def release_pypi(test=True):
    # Downloads wheels from github and upload to PyPI
    response = requests.get(
        'https://api.github.com/repos/pace-neutrons/pace-python/releases')
    # Get the latest release
    releases = response.json()
    ids = [r['id'] for r in releases]
    latest = [r for r in releases if r['id'] == max(ids)][0]
    # Creates a custom wheelhouse folder
    try:
        os.mkdir('pace_wheelhouse')
    except FileExistsError:
        pass
    # Loops through assets and downloads all the wheels
    headers = {"Accept":"application/octet-stream"}
    for asset in latest['assets']:
        if asset['name'].endswith('whl'):
            print('Downloading %s' % (asset['name']))
            localfile = os.path.join('pace_wheelhouse', asset['name'])
            download_github(asset['url'], localfile, use_auth=False)
    if not test:
        subprocess.run(['twine', 'upload', 'pace_wheelhouse/*'])


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


def _create_gh_release(payload):
    response = requests.post(
        'https://api.github.com/repos/pace-neutrons/pace-python/releases',
        data=json.dumps(payload),
        headers={"Authorization": "token " + os.environ["GITHUB_TOKEN"]})
    print(response.text)
    if response.status_code != 201:
        raise RuntimeError('Could not create release')
    upload_url = re.search('^(.*)\{\?', json.loads(response.text)['upload_url']).groups()[0]
    return upload_url


def _upload_assets(upload_url):
    wheelpaths = None
    if os.path.exists('dist'):
        wheelpaths = [os.path.join('dist', ff) for ff in os.listdir('dist')]
    elif os.path.exists('wheelhouse'):
        wheelpaths = [os.path.join('wheelhouse', ff) for ff in os.listdir('wheelhouse') if 'manylinux' in ff]
    if wheelpaths is not None:
        for wheelpath in wheelpaths:
            wheelfile = os.path.basename(wheelpath)
            print(f'Uploading wheel {wheelpath}')
            with open(wheelpath, 'rb') as f:
                upload_response = requests.post(
                    f"{upload_url}?name={wheelfile}",
                    headers={"Authorization": "token " + os.environ["GITHUB_TOKEN"],
                             "Content-type": "application/octet-stream"},
                    data=f.read())
                print(upload_response.text)

    _, installer_path, _ = next(os.walk('installer'))
    if installer_path:
        installer_path = [p for p in installer_path if 'Pace_Python_Installer' in p]
    if installer_path:
        installer_path = os.path.join('installer', installer_path[0])
        installer_file0 = [ff for ff in os.listdir(installer_path) if 'MyAppInstaller' in ff][0]
        installer_file = installer_file0.replace('MyAppInstaller', f'pace_neutrons_installer_{sys.platform}')
        print(f'Uploading installer {installer_file}')
        with open(os.path.join(installer_path, installer_file0), 'rb') as f:
            upload_response = requests.post(
                f"{upload_url}?name={installer_file}",
                headers={"Authorization": "token " + os.environ["GITHUB_TOKEN"],
                         "Content-type": "application/octet-stream"},
                data=f.read())
            print(upload_response.text)
    return None


if __name__ == '__main__':
    main()
