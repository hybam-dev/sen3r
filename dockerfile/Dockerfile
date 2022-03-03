FROM thinkwhere/gdal-python:latest

# thanks to https://github.com/thinkWhere/GDAL-Docker/blob/develop/3.6/Dockerfile

# install SEN3R
RUN git clone https://github.com/hybam-dev/sen3r.git \
	&& cd sen3r \
	&& python -m pip install -r requirements.txt \
	&& python setup.py install

CMD ["sen3r","-h"]