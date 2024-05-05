from argparse import ArgumentParser

from utils import create_namespace, render_and_apply


def execute(
        deployment_id: str,
        namespace: str,
        image: str,
        domain: str,
        token: str,
        mpi_hosts: str = "",
) -> None:
    create_namespace(namespace)

    render_and_apply("manifests/gui_node", namespace, {
        "ID": deployment_id,
        "IMAGE": image,
        "DOMAIN": domain,
        "TOKEN": token,
        "MPI_HOSTS": mpi_hosts,
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
        '-i', '--image',
        help="Docker image to deploy",
        required=True,
    )
    parser.add_argument(
        '-d', '--domain',
        help="Domain of the deployment",
        required=True,
    )
    parser.add_argument(
        '-t', '--token',
        help="OpenAI token",
        required=True,
    )
    parser.add_argument(
        '--mpi-hosts',
        help="MPI hosts (comma separated string)",
        required=False,
    )

    args = parser.parse_args()
    deployment_id = args.id
    namespace = args.namespace
    image = args.image
    domain = args.domain
    token = args.token
    mpi_hosts = args.mpi_hosts

    optional_kwargs = {}
    if mpi_hosts:
        optional_kwargs["mpi_hosts"] = mpi_hosts

    execute(
        deployment_id=deployment_id,
        namespace=namespace,
        image=image,
        domain=domain,
        token=token,
        **optional_kwargs,
    )
