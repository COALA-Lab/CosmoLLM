import base64
from argparse import ArgumentParser

from utils import create_namespace, render_and_apply


def execute(
        namespace: str,
        image: str,
        domain: str,
        kube_config_path: str,
        mongo_url: str,
        mongo_user: str = None,
        mongo_password: str = None,
        admin_user: str = "admin",
        admin_password: str = "admin",
) -> None:
    create_namespace(namespace)

    kube_config = ""
    if kube_config_path:
        with open(kube_config_path) as f:
            kube_config = f.read()
            kube_config = base64.b64encode(kube_config.encode()).decode()

    render_and_apply("manifests/admin_node", namespace, {
        "IMAGE": image,
        "DOMAIN": domain,
        "KUBE_CONFIG": kube_config,
        "MONGO_URL": mongo_url,
        "MONGO_USER": base64.b64encode(mongo_user.encode()).decode() if mongo_user else None,
        "MONGO_PASSWORD": base64.b64encode(mongo_password.encode()).decode() if mongo_password else None,
        "ADMIN_USER": base64.b64encode(admin_user.encode()).decode(),
        "ADMIN_PASSWORD": base64.b64encode(admin_password.encode()).decode(),
    })


if __name__ == '__main__':
    parser = ArgumentParser()
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
        '--kube-config-path',
        help="Path to the kube config file",
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

    args = parser.parse_args()
    namespace = args.namespace
    image = args.image
    domain = args.domain
    kube_config_path = args.kube_config_path
    mongo_url = args.mongo_url
    mongo_user = args.mongo_user
    mongo_password = args.mongo_password
    admin_user = args.admin_user
    admin_password = args.admin_password


    optional_kwargs = {}
    if mongo_user or mongo_password:
        optional_kwargs["mongo_user"] = mongo_user
        optional_kwargs["mongo_password"] = mongo_password
    if admin_user or admin_password:
        optional_kwargs["admin_user"] = admin_user
        optional_kwargs["admin_password"] = admin_password

    execute(
        namespace=namespace,
        image=image,
        domain=domain,
        kube_config_path=kube_config_path,
        mongo_url=mongo_url,
        **optional_kwargs,
    )
