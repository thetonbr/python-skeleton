FROM public.ecr.aws/lambda/python:3.9 as production

WORKDIR /app

ENV ENVIRONMENT=production

COPY LICENSE pyproject.toml pyscript.sh README.md requirements.txt ./

RUN yum upgrade -y && yum install -y gcc && python3 -m pip install --upgrade pip && sh pyscript.sh install

COPY project ./project/

USER python

ENTRYPOINT ["sh", "pyscript.sh", "entrypoint"]
CMD []

FROM production as development

HEALTHCHECK --interval=1s --timeout=10s CMD sh pyscript.sh healthcheck

USER root

ENV ENVIRONMENT=development

COPY .pre-commit-config.yaml Makefile requirements-dev.txt ./

RUN yum install -y net-tools procps && sh pyscript.sh install

COPY tests ./tests

ENTRYPOINT ["sh", "pyscript.sh", "entrypoint"]
CMD []
