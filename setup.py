from setuptools import setup, find_packages



setup(
    name='fast-man',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'fastapi',
        'pydantic',
        'requests'
    ],
    entry_points={
        'console_scripts': [
            'fast-man=fast_man.converter:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)