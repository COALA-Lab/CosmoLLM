import os
from argparse import ArgumentParser


def execute(
    namespace: str,
    release_name: str = "mongodb",
    mongo_user: str = "root",
    mongo_password: str = "root",
) -> None:
    command = (
        f"helm install {release_name} "
        f"-n {namespace} "
        f"--set auth.rootUser={mongo_user} "
        f"--set auth.rootPassword={mongo_password} "
        "oci://registry-1.docker.io/bitnamicharts/mongodb"
    )

    os.system(command)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '--namespace',
        help="Namespace to deploy to",
        required=True,
    )
    parser.add_argument(
        '--release-name',
        help="Release name",
        required=False,
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

    args = parser.parse_args()
    namespace = args.namespace
    release_name = args.release_name
    mongo_user = args.mongo_user
    mongo_password = args.mongo_password

    optional_kwargs = {}
    if release_name:
        optional_kwargs["release_name"] = release_name
    if mongo_user:
        optional_kwargs["mongo_user"] = mongo_user
    if mongo_password:
        optional_kwargs["mongo_password"] = mongo_password

    execute(namespace, **optional_kwargs)
