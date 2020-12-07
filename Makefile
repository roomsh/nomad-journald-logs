GIT_COMMIT=$(shell git log -1 --pretty=format:"%H")
GIT_DESC=$(shell git describe --tags)

build:
	test -z "`git status --porcelain`" || (echo "git repo is not clean"; exit 1)
	docker build -t roomsh/nomad-journald-logs:latest -t roomsh/nomad-journald-logs:$(GIT_COMMIT) -t roomsh/nomad-journald-logs:$(GIT_DESC) .

upload: build
	docker push roomsh/nomad-journald-logs:latest
	docker push roomsh/nomad-journald-logs:$(GIT_COMMIT)
	docker push roomsh/nomad-journald-logs:$(GIT_DESC)
