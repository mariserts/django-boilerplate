#
FROM python:3.10

#
WORKDIR /code

#
COPY ./requirements.txt /code/requirements.txt

#
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

#
COPY . /code/

#
CMD ["python", "manage.py" "collectstatic"]
CMD ["python", "manage.py" "migrate"]
CMD ["gunicorn", "demo.wsgi:application", "--host", "0.0.0.0", "--port", "8000"]
