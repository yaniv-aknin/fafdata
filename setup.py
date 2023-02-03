from distutils.core import setup

with open('LICENSE') as handle:
    license = handle.read()

with open('README.md') as handle:
    long_description = handle.read()

setup(
    name='faf-data',
    version='0.1dev',
    packages=['fafdata',],
    license=license,
    long_description=long_description,
    long_description_content_type='text/markdown',
    entry_points = {
        'console_scripts': ['faf.transform=fafdata.main:transform_api_dump_to_jsonl',
                            'faf.extract=fafdata.main:extract_from_faf_api',
                            'faf.parse=fafdata.main:parse_replays_to_pickle',
                            'faf.dump=fafdata.main:dump_replay_commands_to_jsonl'],
    },
    install_requires = [
        'click',
        'requests',
        'URLObject',
        'zstandard',
        'jsonpath-ng',
        'replay_parser @ git+https://github.com/yaniv-aknin/faf-scfa-replay-parser@9d0cb7c#egg=replay_parser',
    ],
    extras_require = {
        'testing': [
            'py',
            'pytest',
            'pytest-cov',
            'pytest-mock',
            'responses',
        ],
    },
)
