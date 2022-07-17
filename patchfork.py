"""Fork, patch, and release open source Python packages.

Automate third-party patching process through a pipeline configured in a YAML file:

1. Fetch source (git or sdist)
2. Apply patch file
3. Build distributions
4. Upload artifacts (PyPI, S3)
"""

import os
import shutil
from typing import List

import yaml


def main():
    config = load_config()
    for name, project_config in config['forks'].items():
        patch_fork(name, project_config)


def patch_fork(name: str, project_config: dict) -> None:
    if os.path.exists(name):
        shutil.rmtree(name)
    os.makedirs(name)
    os.chdir(name)
    source_type, source_value = next(iter(project_config['source'].items()))
    fetch_source(source_type, source_value)
    apply_patch(f'../{name}.patch')
    build(project_config['before_build_script'], project_config['distributions'])
    upload_artifacts(project_config['upload_index'])
    os.chdir('..')
    shutil.rmtree(name)


def load_config():
    with open('patchfork.yml', encoding='utf-8') as fp:
        return yaml.safe_load(fp)


def fetch_source(source_type: str, source_value: str) -> None:
    if source_type == 'git':
        fetch_git_source(source_value)


def fetch_git_source(repo_url: str) -> None:
    assert 0 == os.system(f'git clone {repo_url} .')


def apply_patch(file_path: str) -> None:
    assert 0 == os.system(f'patch -p0 -i {file_path}')


def build(before_build_script: str, distribution_types: List[str]) -> None:
    assert 0 == os.system(before_build_script)
    assert 0 == os.system(f'python setup.py {" ".join(distribution_types)}')


def upload_artifacts(index_type: str) -> None:
    if index_type == 'PyPI':
        assert 0 == os.system('twine upload dist/*')


if __name__ == '__main__':
    main()
