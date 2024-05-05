FROM cosmollm:latest

RUN sudo apt-get -y install curl
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
RUN sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

COPY entrypoint.sh /home/cosmollm

CMD ["/home/cosmollm/entrypoint.sh"]
