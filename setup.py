try:
    from pip._internal.req import parse_requirements
except ImportError:  # for pip <= 9.0.3
    from pip.req import parse_requirements

from setuptools import setup, find_packages


VERSION = "2.1"
PACKAGE_NAME = "pyassembly"

reqs = parse_requirements('requirements.txt', session=False)
requirements = [str(ir.req) for ir in reqs]

setup(
    name=PACKAGE_NAME,
    version=VERSION,

    description="Creates an egg or a zip distribution with all its transitive dependencies",

    author="Aleksey Zhukov",
    author_email='alekseyig@hotmail.com',

    license='MIT',
    platforms=["any"],
    url="https://github.com/alekseyig/pyassembly",
    keywords=['egg', 'zip', 'transitive', 'dependencies', 'assembly'],

    packages=find_packages(include=['pyassembly', 'pyassembly.*'],
                           exclude=['*.test.*', '*.test']),

    install_requires=requirements,

    package_data={
        PACKAGE_NAME: ['../requirements.txt']
    },

    entry_points={
        'distutils.commands': ['pyassembly = pyassembly.main:pyassembly']
    }
)
