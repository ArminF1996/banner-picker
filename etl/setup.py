from setuptools import find_packages, setup

setup(
    name='assignment_etl',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=False,
    zip_safe=False,
    install_requires=[
        'kafka-python==2.0.2',
        'python-snappy==0.6.0',
        'SQLAlchemy==2.0.7',
        'PyMySQL==1.0.2',
    ],
)
