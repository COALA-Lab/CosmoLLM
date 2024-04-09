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
        '-n', '--namespace',
        help="Namespace to deploy to",
        required=True
    )

    args = parser.parse_args()
    deployment_id = args.id
    compute_id = args.compute_id
    image = args.image
    namespace = args.namespace

    create_namespace(namespace)

    render_and_apply("manifests/compute_node", namespace, {
        "ID": deployment_id,
        "COMPUTE_ID": compute_id,
        "IMAGE": image,
    })


if __name__ == '__main__':
    main()
