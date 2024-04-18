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
        '-i', '--image',
        help="Docker image to deploy",
        required=True
    )
    parser.add_argument(
        '-d', '--domain',
        help="Domain of the deployment",
        required=True
    )
    parser.add_argument(
        '-n', '--namespace',
        help="Namespace to deploy to",
        required=True
    )
    parser.add_argument(
        '-t', '--token',
        help="OpenAI token",
        required=True
    )

    args = parser.parse_args()
    deployment_id = args.id
    image = args.image
    domain = args.domain
    namespace = args.namespace
    token = args.token

    create_namespace(namespace)

    render_and_apply("manifests/gui_node", namespace, {
        "ID": deployment_id,
        "IMAGE": image,
        "DOMAIN": domain,
        "TOKEN": token,
    })


if __name__ == '__main__':
    main()
