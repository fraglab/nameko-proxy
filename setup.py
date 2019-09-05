from setuptools import setup, find_packages


setup(
    name='nameko-proxy',
    version='0.0.6',
    author='Sergey Suglobov',
    author_email='s.suglobov@gmail.com',
    packages=find_packages(),
    keywords="nameko, standalone, proxy",
    url='https://github.com/fraglab/nameko-proxy',
    description='Standalone async proxy to communicate with Nameko microservices ',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3 :: Only'
    ],
    install_requires=[
        'setuptools',
        'nameko'
    ]
)
