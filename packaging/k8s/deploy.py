import os
from argparse import ArgumentParser


def main():
    parser = ArgumentParser()
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

    args = parser.parse_args()
    image = args.image
    domain = args.domain
    namespace = args.namespace

    token = input("Please enter your OpenAI token: ")

    os.system(f'kubectl create namespace {namespace}')

    for manifest in os.listdir('manifests'):
        with open(f'manifests/{manifest}') as f:
            manifest_data = f.read().replace(
                '{{IMAGE}}', image
            ).replace(
                '{{DOMAIN}}', domain
            ).replace(
                '{{TOKEN}}', token
            )
        os.system("mkdir -p dist")
        with open(f'dist/{manifest}', 'w') as f:
            f.write(manifest_data)
        print(f'Applying {manifest}...')
        os.system(f'kubectl apply -f dist/{manifest} -n {namespace}')


if __name__ == '__main__':
    main()
