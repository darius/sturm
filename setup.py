from distutils.core import setup

version = '0.1.0dev'

setup(name = 'Sturm',
      version = version,
      author = 'Darius Bacon',
      author_email = 'darius@wry.me',
      py_modules = ['sturm'],
      url = 'https://github.com/darius/sturm',
      description = "ANSI terminal I/O.",
      long_description = open('README.md').read(),
      license = 'GNU General Public License (GPL)',
      classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
      keywords = 'ansi,console,terminal',
      )
