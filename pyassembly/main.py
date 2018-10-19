import os
import sys
import shutil

from distutils.cmd import Command
from distutils.sysconfig import get_python_version

try:
    from pip._internal.commands import InstallCommand
except ImportError:  # for pip <= 9.0.3
    from pip.commands import InstallCommand

from pkg_resources import get_build_platform, Distribution


class pyassembly(Command):
    description = "create an egg or zip distribution with all its transitive dependencies"
    user_options = [
        ('requirements-file=', 'r',
         'install dependencies from the given requirements file. [default: requirements.txt]'),
        ('destination-format=', 'f', 'assembly formats: zip or egg. [default: egg]'),
        ('assembly-dir=', 'd', 'build the assembly into this dir. [default: pyassembly_dist]')]

    boolean_options = ['keep-temp']

    def initialize_options(self):
        self.requirements_file = None
        self.assembly_dir = None
        self.destination_format = None

    def finalize_options(self):
        self.bdist_base = self.get_finalized_command('bdist').bdist_base
        self.build_base = self.get_finalized_command('build').build_base
        self.egg_info = self.get_finalized_command('egg_info').egg_info

        if self.requirements_file is None:
            self.requirements_file = 'requirements.txt'

        if self.assembly_dir is None:
            self.assembly_dir = 'pyassembly_dist'

        if self.destination_format is None:
            self.destination_format = 'egg'

        if not self.destination_format == 'zip' and not self.destination_format == 'egg':
            print('ERROR: destination-format can be egg or zip only')
            sys.exit(1)

    def run(self):
        if os.path.exists(self.bdist_base):
            shutil.rmtree(self.bdist_base)
        os.makedirs(self.bdist_base)

        if os.path.exists(self.assembly_dir):
            shutil.rmtree(self.assembly_dir)

        dist_dir = os.path.join(self.bdist_base, 'pyassembly')

        # install deps, if needed
        if os.path.exists(self.requirements_file):
            install_command = InstallCommand(isolated=False)
            install_command.main(args=['-r', self.requirements_file, '-t', dist_dir])

        bdist_egg = self.distribution.get_command_obj('bdist_egg')  # type: Command
        bdist_egg.bdist_dir = dist_dir
        bdist_egg.dist_dir = self.assembly_dir
        bdist_egg.keep_temp = 1  # wtf?, it is True or False and not 1 or 0
        bdist_egg.ensure_finalized()

        if self.destination_format == 'zip':
            cmd = self.reinitialize_command('build')
            cmd.build_purelib = dist_dir
            self.run_command('build')

            basename = Distribution(None, None, self.distribution.get_name(),
                                    self.distribution.get_version(), get_python_version(),
                                    self.distribution.has_ext_modules() and get_build_platform()).egg_name()
            shutil.make_archive(base_name=os.path.join(self.assembly_dir, basename), format='zip', root_dir=dist_dir)

        else:
            bdist_egg.run()
            shutil.rmtree(self.egg_info)

        shutil.rmtree(self.build_base)
