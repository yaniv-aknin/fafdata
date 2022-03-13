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
        'console_scripts': ['transform_api_dump_to_jsonl=fafscrape.main:transform_api_dump_to_jsonl',
                            'extract_from_faf_api=fafscrape.main:extract_from_faf_api'],
    }
)
