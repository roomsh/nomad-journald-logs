GIT_COMMIT=$(shell git log -1 --pretty=format:"%H")

build:
	test -z "`git status --porcelain`" || (echo "git repo is not clean"; exit 1)
	docker build -t roomsh/nomad-journald-logs:latest -t roomsh/nomad-journald-logs:$(GIT_COMMIT) .

upload: build
	docker push roomsh/nomad-journald-logs:latest
	docker push roomsh/nomad-journald-logs:$(GIT_COMMIT)