from setuptools import setup, find_packages

setup(
    version="0.1.0",
    name='orderflow_chart',
    description="A Python package for visualizing order flow data in financial markets.",
    packages=find_packages(),
    scripts=[
    ],
    include_package_data=True,
    install_requires=[
        'pandas',
        'plotly',
        'numpy',
    ],
    license='Apache License 2.0',
    zip_safe=False,
)
