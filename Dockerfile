FROM python:latest
WORKDIR /sr-frank/
COPY .. /sr-frank/
RUN pip3 install --trusted-host pypi.python.org -r requirements.txt --user
CMD ["python3", "src/main.py"]