#!/usr/bin/env sh

set -e

_help() {
  echo "Usage:  $0 [OPTIONS] COMMAND

Commands:
  entrypoint <api|cli>                Start Python application
  healthcheck                         Check MongoDB connection
  install                             Install Python dependencies
  fmt                                 Format Python code
  security_analysis                   Analyze security of Python code
  static_analysis                     Analyze rules of Python code
  test [unit|integration|functional]  Run Python tests (default all suites)
  coverage                            Run Python test coverage
  clean                               Remove Python rubbish produced

Options:
  -h, --help      Show this help message and exit
  -v, --version   Show program's version number and exit"
}

_version() {
  echo "${VERSION:-unknown}"
}

_entrypoint() {
  app=$1
  test -z "$app" && echo >&2 "error: missing app name" && exit 1
  shift 1
  if [ "${AWS_LAMBDA_FUNCTION_VERSION:-unknown}" != "unknown" ]; then
    sh /lambda-entrypoint.sh "$project"/apps/"$app" "$@"
  else
    exec python3 "$project"/apps/"$app" "$@"
  fi
}

_healthcheck() {
  wget -qO /dev/null "${MONGODB_HOST:-mongodb}:${MONGODB_PORT:-27017}"
}

_install() {
  if [ "${ENVIRONMENT:-production}" = production ]; then
    python3 -m pip install -r requirements.txt
  else
    python3 -m pip install -r requirements-dev.txt
    pre-commit install --hook-type commit-msg > /dev/null|| true
  fi
}

_fmt() {
  python3 -m autoflake --in-place --remove-all-unused-imports --remove-unused-variables --recursive "$project" tests
  python3 -m black "$project" tests
  python3 -m isort "$project" tests
}

_security_analysis() {
  python3 -m liccheck -r requirements-dev.txt
  python3 -m bandit -s B101,B104,B311 -r "$project"
}

_static_analysis() {
  shellcheck pyscript.sh
  python3 -m mypy \
    --strict \
    --allow-subclassing-any \
    --allow-untyped-decorators \
    --no-warn-return-any \
    --follow-imports=skip \
    --ignore-missing-imports \
    --allow-any-generics \
    --cache-dir=var/cache/.mypy_cache \
    "$project"
  python3 -m pylint "$project"
}

_test() {
  python3 -m pytest "tests/$1"
}

_coverage() {
  python3 -m pytest --cov-report=html:var/log/.pytest_coverage --cov="${project}" --cov-fail-under=95 tests
  rm -rf .coverage &
}

_clean() {
  find . \( -name "__pycache__" -o -name "*.pyc" \) -print0 | xargs -0 rm -rf
  rm -rf var
}

project=project
function=$1

test "$#" -ne 0 && shift 1
test -z "$function" && function=help

set -a
env_file=.env"$(if [ "$LOCAL" = 1 ]; then if [ ! -f .env.local ]; then cp .env .env.local; fi && echo .local; fi)"
# shellcheck disable=SC1090
test -f "$env_file" && . "./${env_file}"
# shellcheck disable=SC1091
tox_pyversion=$(grep "envlist" <"pyproject.toml" | sed "s/[^0-9]*//")
# shellcheck disable=SC1090,SC1091
[ "$LOCAL" = 1 ] && [ -e "var/tox/py$tox_pyversion/bin/activate" ] && . "var/tox/py$tox_pyversion/bin/activate"
set +a

export PYTHONPATH=.
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1

# shellcheck disable=SC2269
case "$function" in
-h | --help) function=help ;;
-v | --version) function=version ;;
security-analysis | static-analysis) function=$(echo $function | sed 's/\-/\_/g') ;;
help | version | entrypoint | healthcheck | install | fmt | security_analysis | static_analysis | test | coverage | clean) function=$function ;;
*) echo >&2 "pyscript: '$function' is not a pyscript command." && exit 1 ;;
esac

eval "_$function" "$@"
