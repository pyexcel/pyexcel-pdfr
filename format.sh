isort $(find pyexcel_pdfr -name "*.py"|xargs echo) $(find tests -name "*.py"|xargs echo)
black -l 79 pyexcel_pdfr
black -l 79 tests
