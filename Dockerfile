FROM python:3.8

RUN mkdir blockchain/

Add . blockchain/

RUN pip install -r blockchain/requirements.txt

EXPOSE 5000

CMD ["python", "blockchain/api.py"]

