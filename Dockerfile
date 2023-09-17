FROM python:latest
WORKDIR /sr-frank/
COPY . /sr-frank/
RUN python3 -m pip install --trusted-host pypi.python.org -vr ./requirements.txt 
WORKDIR /sr-frank/src
EXPOSE 5000
CMD ["python3", "main.py"]