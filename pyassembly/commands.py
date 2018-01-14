import os
import shutil
import zipfile

from distutils.cmd import Command
from pip.commands import WheelCommand

from pkg_resources import (
    parse_requirements, safe_name, parse_version, Distribution,
    safe_version, yield_lines, EntryPoint, iter_entry_points, to_filename)

from pkg_resources import get_build_platform, Distribution, ensure_directory
from distutils.sysconfig import get_python_lib, get_python_version


from setuptools.command.bdist_egg import make_zipfile


class PyAssembly(Command):
    description = "create an egg or zip distribution with all its transitive dependencies"
    user_options = [
        ('requirements-file=', 'r',
         'install dependencies from the given requirements file. [default: requirements.txt]'),
        ('destination-format=', 'f', 'assembly formats - zip or egg. [default: egg]'),
        ('assembly-dir=', 'd', 'build the assembly into dir. [default: pyassembly_dist]')]

    def initialize_options(self):
        self.requirement = 'requirements.txt'
        self.assembly_dir = 'dist'

    def finalize_options(self):
        assert os.path.exists(self.requirement), (
            "requirements file '{}' does not exist.".format(self.requirement))

        ei_cmd = self.ei_cmd = self.get_finalized_command("egg_info")
        self.egg_info = ei_cmd.egg_info

        if self.bdist_dir is None:
            bdist_base = self.get_finalized_command('bdist').bdist_base
            self.bdist_dir = os.path.join(bdist_base, 'egg')

        if self.plat_name is None:
            self.plat_name = get_build_platform()

        self.set_undefined_options('bdist', ('dist_dir', 'dist_dir'))

        if self.egg_output is None:

            # Compute filename of the output egg
            basename = Distribution(
                None, None, ei_cmd.egg_name, ei_cmd.egg_version,
                get_python_version(),
                self.distribution.has_ext_modules() and self.plat_name
            ).egg_name()

            self.egg_output = os.path.join(self.dist_dir, basename + '.egg')

    def run(self):
        # Ensure metadata is up-to-date
        self.egg_name = safe_name(self.distribution.get_name())

        build_py = self.get_finalized_command('bdist_egg')  # type: Command
        #build_py.inplace()

        build_py.inplace = 0
        build_py.run()
        bpy_cmd = self.get_finalized_command("build_py")
        build_path = bpy_cmd.build_lib


class pyas(Command):
    description = "create a built (binary) distribution with all its transitive dependencies"
    user_options = [
        ('requirements=', 'r', 'Install from the given requirements file. [default: requirements.txt]'),
        ('wheel-dir=', 'w', 'Build deps into dir. [default: spark_dist]')
    ]

    def initialize_options(self):
        self.requirement = 'requirements.txt'
        self.wheel_dir = 'spark_dist'
        self.driver = 'driver.py'

    def finalize_options(self):
        assert os.path.exists(self.requirement), (
            "requirements file '{}' does not exist.".format(self.requirement))

    def run(self):
        if os.path.exists(self.wheel_dir):
            shutil.rmtree(self.wheel_dir)

        # generating deps wheels
        wheel_command = WheelCommand(isolated=False)
        wheel_command.main(args=['-r', self.requirement, '-w', self.wheel_dir])

        temp_dir = os.path.join(self.wheel_dir, '.temp')
        os.makedirs(temp_dir)

        z = zipfile.ZipFile(file=os.path.join(temp_dir, '{}-deps-{}.zip'.format(PACKAGE_NAME, VERSION)), mode='w')

        # making "fat" zip file with all deps from each wheel
        for dirname, _, files in os.walk(self.wheel_dir):
            self.rezip(z, dirname, files)
        z.close()

        cmd = self.reinitialize_command('bdist_wheel')
        cmd.dist_dir = temp_dir
        self.run_command('bdist_wheel')

        # make final rearrangements
        for dirname, _, files in os.walk(self.wheel_dir):
            for fname in files:
                if not fname.startswith(PACKAGE_NAME):
                    os.remove(os.path.join(self.wheel_dir, fname))
                else:
                    if fname.endswith('whl'):
                        os.renames(os.path.join(temp_dir, fname),
                                   os.path.join(self.wheel_dir, '{}-{}.zip'.format(PACKAGE_NAME, VERSION)))
                    else:
                        os.renames(os.path.join(temp_dir, fname), os.path.join(self.wheel_dir, fname))

        # copy driver.py into self.wheel_dir dir and version it
        p, e = os.path.splitext(self.driver)
        versioned_driver = '{0}-{1}-{2}{3}'.format(PACKAGE_NAME, p, VERSION, e)
        shutil.copyfile(os.path.join(PACKAGE_NAME, self.driver), os.path.join(self.wheel_dir, versioned_driver))

    def rezip(self, z, dirname, files):
        if dirname == self.wheel_dir:
            for fname in files:
                full_fname = os.path.join(dirname, fname)
                w = zipfile.ZipFile(file=full_fname, mode='r')
                for file_info in w.filelist:
                    z.writestr(file_info, w.read(file_info.filename))
