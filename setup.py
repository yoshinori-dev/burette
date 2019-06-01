# -*- coding: utf-8 -*-

from setuptools import setup


setup(
    name='burette',
    version='0.1',
    description='A micro web framework',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Yoshinori',
    author_email='yoshinori.dev@gmail.com',
    url='https://github.com/yoshinori-akita/burette',
    install_requires=[
        "Jinja2>=2.10.1"
    ],
    license='MIT',
    py_modules=['burette'],
    scripts=['burette.py'],
    classifiers=[
        'Programming Language :: Python :: 3.7'
    ]
)
