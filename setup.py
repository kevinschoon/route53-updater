from setuptools import setup, find_packages

setup(
    name='53Updater',
    version='0.0.2',
    packages=find_packages(),
    package_dir={'53updater': 'updater'},
    entry_points={'console_scripts': ['53Updater = updater.cli:main']},
    include_package_data=True,
    install_requires=['boto', 'aiohttp', 'aioprocessing'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4'
    ]
)
