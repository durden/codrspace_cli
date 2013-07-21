from distutils.core import setup

setup(name='codrspace_cli',
      version='0.1',
      description='Create/update posts on codrspace.com via command-line',
      author='Luke Lee',
      author_email='durdenmisc@gmail.com',
      url='https://github.com/durden/codrspace_cli',
      py_modules=['codrspace'],
      install_requires = ['requests>=0.14.2'],
      entry_points={
        "console_scripts": [
            "codrspace_cli = codrspace:main",
        ]
    },
)
