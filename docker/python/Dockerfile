FROM python:3.8.5 AS production

WORKDIR /app

ENV TZ=Europe/Madrid ENVIRONMENT=production DEBUG=0 PYTHONPATH=.

RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata \
    bash \
    curl \
    apt-utils \
    netcat \
  && rm -rf /var/lib/apt/lists/*

COPY ./docker/python/rootfs /

HEALTHCHECK --interval=1s --timeout=10s CMD /docker-healthcheck.sh

COPY src /app/src/

RUN /install.sh

ENTRYPOINT ["python"]
CMD []

FROM production as development

ENV ENVIRONMENT=development DEBUG=1

COPY ./docker/python/rootfs-dev /

COPY tests /app/tests

RUN /install.sh
