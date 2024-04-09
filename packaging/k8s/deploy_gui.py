import base64
from argparse import ArgumentParser

from utils import create_namespace, render_and_apply


def main():
    parser = ArgumentParser()
    parser.add_argument(
        '--id',
        help="ID of the deployment",
        required=True
    )
    parser.add_argument(
        '-i', '--image',
        help="Docker image to deploy",
        required=True
    )
    parser.add_argument(
        '-d', '--domain',
        help="Domain of the deployment",
        required=True
    )
    parser.add_argument(
        '-n', '--namespace',
        help="Namespace to deploy to",
        required=True
    )
    parser.add_argument(
        '-t', '--token',
        help="OpenAI token",
        required=True
    )
    parser.add_argument(
        '--mpi-hosts',
        help="MPI hosts (comma separated string)",
        required=False,
        default=""
    )
    parser.add_argument(
        '--ssh-public-key-path',
        help="Path to the SSH public key",
        required=False
    )
    parser.add_argument(
        '--ssh-private-key-path',
        help="Path to the SSH private key",
        required=False
    )

    args = parser.parse_args()
    deployment_id = args.id
    image = args.image
    domain = args.domain
    namespace = args.namespace
    token = args.token
    mpi_hosts = args.mpi_hosts
    ssh_public_key_path = args.ssh_public_key_path
    ssh_private_key_path = args.ssh_private_key_path

    ssh_public_key = ""
    ssh_private_key = ""
    if ssh_public_key_path and ssh_private_key_path:
        with open(ssh_public_key_path) as f:
            ssh_public_key = f.read()
            ssh_public_key = base64.b64encode(ssh_public_key.encode()).decode()
        with open(ssh_private_key_path) as f:
            ssh_private_key = f.read()
            ssh_private_key = base64.b64encode(ssh_private_key.encode()).decode()

    create_namespace(namespace)

    render_and_apply("manifests/gui_node", namespace, {
        "ID": deployment_id,
        "IMAGE": image,
        "DOMAIN": domain,
        "TOKEN": token,
        "MPI_HOSTS": mpi_hosts,
        "SSH_PUBLIC_KEY": ssh_public_key,
        "SSH_PRIVATE_KEY": ssh_private_key
    })


if __name__ == '__main__':
    main()
