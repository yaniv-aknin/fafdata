from distutils.core import setup

with open('LICENSE') as handle:
    license = handle.read()

with open('README.md') as handle:
    long_description = handle.read()

setup(
    name='fafscrape',
    version='0.1dev',
    packages=['fafscrape',],
    license=license,
    long_description=long_description,
    long_description_content_type='text/markdown',
    entry_points = {
        'console_scripts': ['faf.transform=fafscrape.main:transform_api_dump_to_jsonl',
                            'faf.extract=fafscrape.main:extract_from_faf_api',
                            'faf.unpack=fafscrape.main:unpack_replays_to_pickle',
                            'faf.parse=fafscrape.main:parse_replay_commands_to_jsonl'],
    }
)
