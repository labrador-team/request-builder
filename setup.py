from setuptools import setup


setup(
    name='requests-builder',
    version='1.0.0',
    description='A cool utility to save and reuse requests with the requests library',
    author='Labrador Team',
    author_email='labrador.team@outlook.com',
    license='Apache 2.0',
    license_files=['LICENSE'],
    packages=['requestsbuilder'],
    install_requires=['requests'],
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities'
    ]
)
