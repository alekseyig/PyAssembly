import os
import sys
import shutil
import zipfile

from setuptools import setup, find_packages

from distutils.cmd import Command
from pip.commands import WheelCommand
from pip.req import parse_requirements

PACKAGE_NAME = "pyassembly"
VERSION = "1.0"

reqs = parse_requirements('requirements.txt', session=False)
requirements = [str(ir.req) for ir in reqs]




class BotocoreData(Command):
    description = "create a zip file with botocore and awscli config data"
    user_options = []

    def initialize_options(self):
        self.wheel_dir = 'spark_dist'

    def finalize_options(self):
        pass

    def run(self):
        # we need to import it here, so we can find its module root
        import botocore
        import awscli

        botocore_data_archive = '{}-botocore_data-{}'.format(PACKAGE_NAME, VERSION)

        if not os.path.exists(self.wheel_dir):
            os.makedirs(self.wheel_dir)

        botocore_data = os.path.join(sys.modules['botocore'].BOTOCORE_ROOT, 'data')
        archive = shutil.make_archive(base_name=os.path.join(self.wheel_dir, botocore_data_archive),
                                      format='zip', root_dir=botocore_data)

        awscli_data = os.path.join(os.path.dirname(sys.modules['awscli'].__file__), 'data')
        z = zipfile.ZipFile(archive, 'a')
        os.chdir(awscli_data)
        z.write('cli.json')
        z.close()


setup(
    name=PACKAGE_NAME,
    version=VERSION,

    description="PySpark jobs for delivery data analysis",

    author="Aleksey Zhukov",
    author_email='alekseyig@hotmail.com',

    platforms=["any"],
    url="https://github.com",

    packages=find_packages(include=['pyassembly', 'pyassembly.*'],
                           exclude=['*.test.*', '*.test']),

    install_requires=requirements,

    package_data={
        PACKAGE_NAME: ['../requirements.txt']
    },

    entry_points={
        'console_scripts': ['pyassembly = pyassembly:main'],
        'distutils.commands': ['pyassembly = pyassembly.commands:pyassembly']
    },

    cmdclass={
        "bdist_spark": BdistSpark,
        "botocore_data": BotocoreData
    }
)
