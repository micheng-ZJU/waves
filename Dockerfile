FROM python:3.9

WORKDIR /app

COPY Flask_BackEnd/ .

RUN pip pip install --proxy=http://proxy.statestr.com:80 --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host=files.pythonhosted.org -r requirements.txt

RUN chmod +x start.sh

CMD ["./start.sh"]