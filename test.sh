pip freeze
nosetests --with-cov --cover-package pyexcel_pdf --cover-package tests --with-doctest --doctest-extension=.rst README.rst tests docs/source pyexcel_pdf && flake8 . --exclude=.moban.d --builtins=unicode,xrange,long
