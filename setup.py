from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='ffbrank',
    version='0.1.0',
    description='Scrape fantasy football rankings from many experts.',
    long_description=readme(),
    keywords='fantasy football rankings scrape scraper fantasypros',
    url='https://github.com/djcunningham0/FFBrank',
    author='Danny Cunningham',
    author_email='djcunningham0@gmail.com',
    license='MIT',
    packages=['ffbrank'],
    python_requires='>=3',
    install_requires=['pandas', 'bs4', 'requests'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering'
    ]
)
