FROM mcr.microsoft.com/azure-functions/python:2.0

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true

ENV FUNCTIONS_WORKER_RUNTIME=python

RUN apt install -y gcc unixodbc-dev python3-dev build-essential libssl-dev libffi-dev

COPY . /home/site/wwwroot

RUN cd /home/site/wwwroot && \
    pip install -r requirements.txt
