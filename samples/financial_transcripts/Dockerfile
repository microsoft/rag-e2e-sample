FROM mambaorg/micromamba:0.15.3
USER root
RUN apt-get update && DEBIAN_FRONTEND=“noninteractive” apt-get install -y --no-install-recommends \
       nginx \
       ca-certificates \
       apache2-utils \
       certbot \
       python3-certbot-nginx \
       sudo \
       cifs-utils \
       && \
    rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get -y install cron
RUN mkdir /opt/chatbot
RUN chmod -R 777 /opt/chatbot
WORKDIR /opt/chatbot
USER micromamba
EXPOSE 8000
COPY ../../rag_skills /opt/chatbot/rag_skills
COPY ../../environment.yaml ./environment.yaml
COPY ../../llm.env llm.env
RUN micromamba install -y -n base -f environment.yaml && \
   micromamba clean --all --yes
COPY /samples/financial_transcripts/ /opt/chatbot/
USER root
RUN chmod -R 777 /opt/chatbot
USER micromamba
ENTRYPOINT ["streamlit", "run"]
CMD ["st_main.py","--server.port","8000","--theme.base","dark"]

