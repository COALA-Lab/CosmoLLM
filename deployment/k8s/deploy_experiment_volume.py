from argparse import ArgumentParser

from utils import render_and_apply


def execute(
    deployment_id: str,
    namespace: str,
    storage_class: str = "local-storage",
    storage_size: str = "4Gi",
) -> None:
    render_and_apply("manifests/experiment_volume", namespace=namespace, context={
        "ID": deployment_id,
        "STORAGE_CLASS": storage_class,
        "STORAGE_SIZE": storage_size,
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
        '--storage-class',
        help="Storage class to use",
        required=False,
    )
    parser.add_argument(
        '--storage-size',
        help="Storage size",
        required=False,
    )

    args = parser.parse_args()
    deployment_id = args.id
    namespace = args.namespace
    storage_class = args.storage_class
    storage_size = args.storage_size

    optional_kwargs = {}
    if storage_class:
        optional_kwargs["storage_class"] = storage_class
    if storage_size:
        optional_kwargs["storage_size"] = storage_size

    execute(
        deployment_id=deployment_id,
        namespace=namespace,
        **optional_kwargs,
    )
