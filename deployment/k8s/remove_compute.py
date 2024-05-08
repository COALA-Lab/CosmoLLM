if __name__ == '__main__':
    from utils import adjust_pythonpath

    adjust_pythonpath()

from argparse import ArgumentParser

from deployment.k8s.utils import delete_by_name


def execute(
        deployment_id: str,
        compute_id: str,
        namespace: str,
) -> None:
    delete_by_name(namespace, f"cosmollm-compute-{deployment_id}-{compute_id}")


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
    parser.add_argument(
        '--compute-id',
        help="Compute ID of the node to remove",
        required=True,
    )

    args = parser.parse_args()
    deployment_id = args.id
    namespace = args.namespace
    compute_id = args.compute_id

    execute(
        deployment_id=deployment_id,
        namespace=namespace,
        compute_id=compute_id,
    )
