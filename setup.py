from setuptools import setup

setup(
    name='ff_bot',

    packages=['ff_bot'],

    include_package_data=True,

    version='0.2.0',

    description='ESPN fantasy football GroupMe Bot',

    author='Dean Carlson',

    author_email='deantcarlson@gmail.com',

    install_requires=['requests>=2.0.0,<3.0.0', 'ff_espn_api>=1.1.0', 'apscheduler>3.0.0'],

    test_suite='nose.collector',

    tests_require=['nose', 'requests_mock'],

    url='https://github.com/dtcarls/ff_bot',

    classifiers=[
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
