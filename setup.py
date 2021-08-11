import os
import sys
from distutils.command.clean import clean
from distutils.command.install import install
from distutils.command.sdist import sdist

from setuptools import setup

# major, minor, micro, release, serial
__VERSION_INFO__ = (1, 2, 3, 'final', 0)
__VERSION__ = '%d.%d' % (__VERSION_INFO__[0], __VERSION_INFO__[1])


class CAInstall(install):
    def run(self):
        install.run(self)
        c = CAClean(self.distribution)
        c.run()
        os.system('rm -vrf ./*.egg-info ./dist')


class CASDist(sdist):
    def run(self):
        sdist.run(self)
        c = CAClean(self.distribution)
        c.run()
        os.system('rm -vrf MANIFEST ./*.egg-info')


class CAClean(clean):
    description = "Cleans up files generated by install or sdist"

    user_options = [
        ('all', 'a',
         "remove all build output, not just temporary by-products")
    ]

    boolean_options = ['all']

    def initialize_options(self):
        self.all = None

    def finalize_options(self):
        if self.all is None:
            self.all = False

    def run(self):
        c = clean(self.distribution)
        c.all = True
        c.finalize_options()
        c.run()

        if hasattr(self, 'all') and self.all:
            os.system('rm -vrf MANIFEST ./*.pyc ./*.egg-info ./dist')


class CAUninstall(clean):
    description = "Uninstalls this or previous versions of codescanner_analysis."

    user_options = [
        ('all', 'a',
         "remove all found versions")
    ]

    boolean_options = ['other']

    def initialize_options(self):
        py_version = sys.version_info
        py_version_identifier = '%d.%d' % (py_version[0], py_version[1])
        self.all = None
        self.site_packages_path = '/usr/lib/python%s/site-packages/' % py_version_identifier
        self.egg = 'codescanner_analysis-%%s-py%s.egg/' % py_version_identifier

    def finalize_options(self):
        if self.all is None:
            self.all = False

    def run(self):
        # c = clean(self.distribution)
        # c.all = True
        # c.finalize_options()
        # c.run()

        if hasattr(self, 'all') and self.all:
            reg = '*'
            self.egg = self.egg % reg
            rm_str = 'rm -vrf %s%s' % (self.site_packages_path, self.egg)
            os.system(rm_str)
        elif not self.all:
            self.egg = self.egg % __VERSION__
            rm_str = 'rm -vrf %s%s' % (self.site_packages_path, self.egg)
            os.system(rm_str)


def package_files(directory):
    '''
    Pack files into array.

    :param directory: source directory
    :return: packed files array
    '''
    paths = []

    for f in os.listdir(os.path.join(directory)):
        if os.path.isfile(os.path.join(directory, f)):
            paths.append(directory + "/" + f)

    return paths


def package_modules(directory):
    '''
    Pack modules (*.py) into array.

    :param directory: source directory
    :return: packed modules array
    '''
    paths = []

    for f in os.listdir(os.path.join(directory)):
        if os.path.isfile(os.path.join(directory, f)):
            base_name, ext = os.path.splitext(f)
            if base_name == 'setup':
                continue
            if ext == '.py':
                if directory == '.':
                    paths.append(base_name)
                else:
                    paths.append(directory + "/" + base_name)

    return paths


res_data = package_files('res')
res_lib_data = package_files('res/lib')
res_languages_data = package_files('res/lib/languages')

modules = package_modules('.')
util_files = package_modules('utils')


setup(name='codescanner_analysis',
      version=__VERSION__,
      description='Analysis module to classify regions of arbitrary binaries',
      author='Fraunhofer FKIE CA&D, Viviane Zwanger, Henning Braun',
      author_email='viviane.zwanger@fkie.fraunhofer.de, henning.braun@fkie.fraunhofer.de',
      url='https://gitlab.caad.fkie.fraunhofer.de/codescanner/codescanner-analysis',
      download_url='https://gitlab.caad.fkie.fraunhofer.de/codescanner/codescanner-analysis/-/archive/master/codescanner-analysis-master.tar.gz',
      keywords=['codescanner', 'code regions'],
      py_modules=modules + util_files,
      data_files=[('res', res_data),
                  ('res/lib', res_lib_data),
                  ('res/lib/languages', res_languages_data)
                  ],
      install_requires=[
          'matplotlib',
          'numpy'],
      cmdclass={
          # 'install': CAInstall,
          # 'sdist': CASDist,
          'clean': CAClean,
          'uninstall': CAUninstall
      }
      )
