if __name__ == '__main__':
    from utils import adjust_pythonpath

    adjust_pythonpath()

from argparse import ArgumentParser
from typing import Optional

from deployment.k8s.utils import create_namespace, render_and_apply


def execute(
        deployment_id: str,
        namespace: str,
        compute_id: str,
        image: str,
        cpu_limit: str = "2000m",
        memory_limit: str = "4Gi",
        cpu_request: Optional[str] = None,
        memory_request: Optional[str] = None,
) -> None:
    if not cpu_request:
        cpu_request = cpu_limit
    if not memory_request:
        memory_request = memory_limit

    create_namespace(namespace)

    render_and_apply("manifests/compute_node", namespace, {
        "ID": deployment_id,
        "COMPUTE_ID": compute_id,
        "IMAGE": image,
        "CPU_LIMIT": cpu_limit,
        "MEMORY_LIMIT": memory_limit,
        "CPU_REQUEST": cpu_request,
        "MEMORY_REQUEST": memory_request,
    })


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '--id',
        help="ID of the deployment",
        required=True
    )
    parser.add_argument(
        '-n', '--namespace',
        help="Namespace to deploy to",
        required=True
    )
    parser.add_argument(
        '--compute-id',
        help="ID of the compute deployment",
        required=True
    )
    parser.add_argument(
        '-i', '--image',
        help="Docker image to deploy",
        required=True
    )
    parser.add_argument(
        '--cpu-limit',
        help="CPU resource limit",
        required=False
    )
    parser.add_argument(
        '--memory-limit',
        help="Memory resource limit",
        required=False
    )
    parser.add_argument(
        '--cpu-request',
        help="CPU resource request",
        required=False
    )
    parser.add_argument(
        '--memory-request',
        help="Memory resource request",
        required=False
    )

    args = parser.parse_args()
    deployment_id = args.id
    namespace = args.namespace
    compute_id = args.compute_id
    image = args.image
    cpu_limit = args.cpu_limit
    memory_limit = args.memory_limit
    cpu_request = args.cpu_request
    memory_request = args.memory_request

    optional_kwargs = {}
    if cpu_limit:
        optional_kwargs["cpu_limit"] = cpu_limit
    if memory_limit:
        optional_kwargs["memory_limit"] = memory_limit
    if cpu_request:
        optional_kwargs["cpu_request"] = cpu_request
    if memory_request:
        optional_kwargs["memory_request"] = memory_request

    execute(
        deployment_id=deployment_id,
        namespace=namespace,
        compute_id=compute_id,
        image=image,
        **optional_kwargs,
    )
