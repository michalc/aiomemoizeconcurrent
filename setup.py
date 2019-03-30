import setuptools


def long_description():
    with open('README.md', 'r') as file:
        return file.read()


setuptools.setup(
    name='aiodeduplicate',
    version='0.0.1',
    author='Michal Charemza',
    author_email='michal@charemza.name',
    description='Deduplicate concurrent asyncio Python function calls',
    long_description=long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/michalc/aiodeduplicate',
    py_modules=[
        'aiodeduplicate',
    ],
    python_requires='~=3.5',
    test_suite='test',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Framework :: AsyncIO',
    ],
)
