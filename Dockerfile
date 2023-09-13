FROM python:latest
WORKDIR /sr-frank/
COPY .. /sr-frank/
RUN pip3 install --trusted-host pypi.python.org -vr requirements.txt 
CMD ["python3", "src/main.py"]