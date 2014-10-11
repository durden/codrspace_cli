from distutils.core import setup

setup(name='codrspace_cli',
      version='0.3',
      description='Create/update/export posts on codrspace.com via command-line',
      author='Luke Lee',
      author_email='durdenmisc@gmail.com',
      url='https://github.com/durden/codrspace_cli',
      py_modules=['create', 'export'],
      install_requires = ['requests>=0.14.2', 'click>=3.1'],
      entry_points={
        "console_scripts": [
            "codrspace_import = create:main",
            "codrspace_export = export:cli",
        ]
    },
)
