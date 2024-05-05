from argparse import ArgumentParser

from utils import delete_by_labels


def execute(
        deployment_id: str,
        namespace: str,
) -> None:
    delete_by_labels(namespace, {"deploymentId": deployment_id})


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '--id',
        help="ID of the deployment",
        required=True,
    )
    parser.add_argument(
        '-n', '--namespace',
        help="Namespace containing the deployment",
        required=True,
    )

    args = parser.parse_args()
    deployment_id = args.id
    namespace = args.namespace

    execute(
        deployment_id=deployment_id,
        namespace=namespace,
    )
