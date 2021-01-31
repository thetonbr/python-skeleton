FROM python:3.9.1 as production

WORKDIR /app

ENV ENVIRONMENT=production

COPY LICENSE pyproject.toml pyscript.sh README.md requirements.txt ./
COPY project ./project/

HEALTHCHECK --interval=1s --timeout=10s CMD sh pyscript.sh healthcheck

RUN python3 -m pip install --upgrade pip && sh pyscript.sh install

USER python

ENTRYPOINT ["sh", "pyscript.sh", "entrypoint"]
CMD []

FROM production as development

ENV ENVIRONMENT=development

USER root

COPY .pre-commit-config.yaml Makefile requirements-dev.txt ./
COPY tests ./tests

RUN sh pyscript.sh install

ENTRYPOINT ["sh", "pyscript.sh", "entrypoint"]
CMD []
