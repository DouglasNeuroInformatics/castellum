import json
from urllib.request import urlopen


def iter_requirements():
    with open('requirements.txt') as fh:
        for line in fh:
            yield line.split()[0].split('==')


def get_hashes(name, version):
    print('get hashes for {}=={}'.format(name, version))
    with urlopen('https://pypi.org/pypi/{}/json'.format(name)) as fh:
        data = json.load(fh)
        for f in data['releases'][version]:
            yield f['digests']['sha256']


if __name__ == '__main__':
    lines = []
    for name, version in iter_requirements():
        line = '{}=={}'.format(name, version)
        for h in get_hashes(name, version):
            line += ' --hash=sha256:' + h
        lines.append(line)

    with open('requirements.txt', 'w') as fh:
        for line in lines:
            fh.write(line + '\n')
