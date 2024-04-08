FROM cosmollm:latest

USER root

RUN apt-get install -y openssh-server

RUN mkdir /var/run/sshd
COPY sshd_config /etc/ssh/sshd_config

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D", "-e"]
