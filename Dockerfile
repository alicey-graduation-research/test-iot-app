FROM python:3.9.10

WORKDIR /opt/app

ADD requirements.txt ./requirements.txt
ADD app/ .

RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt

ENTRYPOINT [ "python", "app.py" ] 

EXPOSE 80