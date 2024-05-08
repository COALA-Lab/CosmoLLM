if __name__ == '__main__':
    from utils import adjust_pythonpath

    adjust_pythonpath()

import os
from argparse import ArgumentParser


def execute(
    deployment_id: str,
    namespace: str,
) -> None:
    command = (
        f"kubectl rollout restart deployment cosmollm-gui-{deployment_id} -n {namespace}"
    )

    os.system(command)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '--id',
        help="ID of the deployment",
        required=True,
    )
    parser.add_argument(
        '-n', '--namespace',
        help="Namespace of the deployment",
        required=True,
    )

    args = parser.parse_args()
    deployment_id = args.id
    namespace = args.namespace

    execute(
        deployment_id=deployment_id,
        namespace=namespace,
    )
