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
        '--cpu',
        help="CPU resource limit",
        default="2000m",
        required=False
    )
    parser.add_argument(
        '--memory',
        help="Memory resource limit",
        default="4Gi",
        required=False
    )

    args = parser.parse_args()
    deployment_id = args.id
    namespace = args.namespace
    compute_id = args.compute_id
    image = args.image
    cpu = args.cpu
    memory = args.memory

    create_namespace(namespace)

    render_and_apply("manifests/compute_node", namespace, {
        "ID": deployment_id,
        "COMPUTE_ID": compute_id,
        "IMAGE": image,
        "CPU_LIMIT": cpu,
        "MEMORY_LIMIT": memory,
    })


if __name__ == '__main__':
    main()
