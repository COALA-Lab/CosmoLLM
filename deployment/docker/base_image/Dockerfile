FROM ubuntu:22.04

RUN apt-get update
RUN apt-get install -y python3-dev python3-pip python3-mpi4py git sudo

RUN addgroup --gid 1000 cosmollm && \
    adduser --uid 1000 --gid 1000 --disabled-password --gecos "" cosmollm && \
    echo 'cosmollm ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers
RUN chown -R cosmollm:cosmollm /home/cosmollm

RUN mkdir /app
WORKDIR /app
RUN chown -R cosmollm:cosmollm /app
ENV PATH="$PATH:/home/cosmollm/.local/bin"

USER cosmollm
RUN . /etc/profile

# TODO: Change this to main
RUN git clone https://github.com/COALA-Lab/CosmoLLM.git . --recursive --branch feature/multi_user_deployment

RUN SKLEARN_ALLOW_DEPRECATED_SKLEARN_PACKAGE_INSTALL=True pip install -r requirements.txt

COPY entrypoint.sh /home/cosmollm

CMD ["/home/cosmollm/entrypoint.sh"]
