from setuptools import setup, find_packages


def parse_requirements(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='robot_library',
    version='0.0.0',
    packages=find_packages(),
    description='A sample Robot Framework library package.',
    author='Your Name',
    author_email='your.email@example.com',
    install_requires=parse_requirements('requirements.txt'),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)