pip freeze
coverage run -m --source=pyexcel_pdfr pytest --doctest-modules && coverage report --show-missing
