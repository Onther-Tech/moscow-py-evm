FROM python:3.6
# Set up code directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
RUN git clone https://github.com/cd4761/eth-ecc.git && cd eth-ecc && git pull
RUN cd eth-ecc && python setup.py install
RUN git clone http://github.com/cd4761/ecc-py-evm.git && cd ecc-py-evm && pip install -e .[dev]  --no-cache-dir

# ENTRYPOINT ["python", "/usr/src/app/eth-ecc/test/ethecc_test.py"]
