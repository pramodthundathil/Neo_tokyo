FROM python:3.10.10

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . Neo_Tokyo_Back_end
WORKDIR /Neo_Tokyo_Back_end

EXPOSE 8000

# runs the production server
ENTRYPOINT ["python", "Neo_tokyo/manage.py"]
CMD ["runserver", "0.0.0.0:8000"]