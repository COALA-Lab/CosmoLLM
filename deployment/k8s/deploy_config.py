import base64
from argparse import ArgumentParser

from utils import create_namespace, render_and_apply


def execute(
        deployment_id: str,
        namespace: str,
        mongo_url: str,
        mongo_user: str = None,
        mongo_password: str = None,
        admin_user: str = "admin",
        admin_password: str = "admin",
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
        "MONGO_URL": mongo_url,
        "MONGO_USER": base64.b64encode(mongo_user.encode()).decode() if mongo_user else None,
        "MONGO_PASSWORD": base64.b64encode(mongo_password.encode()).decode() if mongo_password else None,
        "ADMIN_USER": base64.b64encode(admin_user.encode()).decode(),
        "ADMIN_PASSWORD": base64.b64encode(admin_password.encode()).decode(),
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
        '--mongo-url',
        help="MongoDB url",
        required=True,
    )
    parser.add_argument(
        '--mongo-user',
        help="MongoDB user",
        required=False,
    )
    parser.add_argument(
        '--mongo-password',
        help="MongoDB password",
        required=False,
    )
    parser.add_argument(
        '--admin-user',
        help="Admin user",
        required=False,
    )
    parser.add_argument(
        '--admin-password',
        help="Admin password",
        required=False,
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
    mongo_url = args.mongo_url
    mongo_user = args.mongo_user
    mongo_password = args.mongo_password
    admin_user = args.admin_user
    admin_password = args.admin_password
    mpi_host_slots = args.mpi_host_slots
    ssh_public_key_path = args.ssh_public_key_path
    ssh_private_key_path = args.ssh_private_key_path

    optional_kwargs = {}
    if mongo_user or mongo_password:
        optional_kwargs["mongo_user"] = mongo_user
        optional_kwargs["mongo_password"] = mongo_password
    if admin_user or admin_password:
        optional_kwargs["admin_user"] = admin_user
        optional_kwargs["admin_password"] = admin_password
    if mpi_host_slots:
        optional_kwargs["mpi_host_slots"] = mpi_host_slots
    if ssh_public_key_path:
        optional_kwargs["ssh_public_key_path"] = ssh_public_key_path
    if ssh_private_key_path:
        optional_kwargs["ssh_private_key_path"] = ssh_private_key_path

    execute(
        deployment_id=deployment_id,
        namespace=namespace,
        mongo_url=mongo_url,
        **optional_kwargs,
    )
