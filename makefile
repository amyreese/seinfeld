
server:
	uwsgi --http 0.0.0.0:8000 --file app.wsgi --touch-reload app.wsgi

shell:
	python2 -i app.wsgi

.PHONY:
submodules:
	git submodule init && git submodule sync && git submodule update

.PHONY:
clean:
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete

