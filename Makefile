setup:
	python setup.py

check:
	python scout.py doctor
	python -m py_compile scout.py setup.py

scout:
	python scout.py new-scout
	python scout.py run scout
