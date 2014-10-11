local_reinstall:
	pip uninstall codrspace_cli
	pip install .

upload_test_dist:
	python setup.py register -r pypi-test
	python setup.py sdist upload -r pypi-test

install_test_dist:
	# Must install the requirements separately b/c they aren't
	# available on test server
	pip install requests
	pip install click
	pip install -i https://testpypi.python.org/pypi codrspace_cli

test_install:
	codrspace_export --help
	codrspace_import

upload_release:
	python setup.py sdist upload -r pypi
