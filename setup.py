from distutils.core import setup, Extension

setup(name='pycms',
		version='0.0-alpha',
		description='Python for CMSSW',
		author='Jordi Duarte Campderros',
		author_email='Jordi.Duarte.Campderros@cern.ch',
		url='http://devel.ifca.es/~duarte/pytcms/dist',
		packages = ['pycms' ],
		package_dir={'pycms':''},
		#scripts=[],
		)
