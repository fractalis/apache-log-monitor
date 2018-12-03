FROM python:3
RUN touch /var/log/access.log
WORKDIR /usr/src
ADD . /usr/src
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "main.py"]
