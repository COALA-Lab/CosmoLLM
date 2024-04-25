import base64
from argparse import ArgumentParser

from utils import create_namespace, render_and_apply


def execute(
        deployment_id: str,
        namespace: str,
        mpi_host_slots: int = 2,
        ssh_public_key_path: str = None,
        ssh_private_key_path: str = None,
) -> None:

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

    render_and_apply("manifests/config", namespace, {
        "ID": deployment_id,
        "MPI_HOST_SLOTS": str(mpi_host_slots),
        "SSH_PUBLIC_KEY": ssh_public_key,
        "SSH_PRIVATE_KEY": ssh_private_key,
    })


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '--id',
        help="ID of the deployment",
        required=True,
    )
    parser.add_argument(
        '-n', '--namespace',
        help="Namespace to deploy to",
        required=True,
    )
    parser.add_argument(
        '--mpi-host-slots',
        help="Number of slots per MPI host",
        required=False,
    )
    parser.add_argument(
        '--ssh-public-key-path',
        help="Path to the SSH public key",
        required=False,
    )
    parser.add_argument(
        '--ssh-private-key-path',
        help="Path to the SSH private key",
        required=False,
    )

    args = parser.parse_args()
    deployment_id = args.id
    namespace = args.namespace
    mpi_host_slots = args.mpi_host_slots
    ssh_public_key_path = args.ssh_public_key_path
    ssh_private_key_path = args.ssh_private_key_path

    optional_kwargs = {}
    if mpi_host_slots:
        optional_kwargs["mpi_host_slots"] = mpi_host_slots
    if ssh_public_key_path:
        optional_kwargs["ssh_public_key_path"] = ssh_public_key_path
    if ssh_private_key_path:
        optional_kwargs["ssh_private_key_path"] = ssh_private_key_path

    execute(
        deployment_id=deployment_id,
        namespace=namespace,
        **optional_kwargs,
    )
