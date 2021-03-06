from setuptools import setup, find_packages
import rabidratings

install_requires = [
    'Django>=1.4.5,<1.9',
]

tests_require = [
    'nose',
    'coverage',
]

long_description = open('README.rst').read()

setup(
    name='Django-rabidratings-ng',
    version=rabidratings.__versionstr__,
    description='Rating application based on Django framework',
    long_description=long_description,
    author='Sanoma Media',
    author_email='online-dev@sanoma.cz',
    license='BSD',
    url='https://github.com/SanomaCZ/django-rabidratings-ng',

    packages=find_packages(
        where='.',
        exclude=('doc', 'tests',)
    ),

    include_package_data=True,

    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=install_requires,

    test_suite='tests.run_tests.run_all',
    tests_require=tests_require,
)
