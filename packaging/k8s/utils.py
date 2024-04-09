import os


def create_namespace(namespace: str) -> None:
    os.system(f'kubectl create namespace {namespace}')


def render_and_apply(template_path: str, namespace: str, context: dict) -> None:
    for manifest in os.listdir(template_path):
        with open(f'{template_path}/{manifest}') as f:
            manifest_data = f.read()

            for key, value in context.items():
                manifest_data = manifest_data.replace("{{" + f"{key}" + "}}", value)

        os.system(f"mkdir -p dist/{template_path}")
        with open(f'dist/{template_path}/{manifest}', 'w') as f:
            f.write(manifest_data)
        print(f'Applying {template_path}/{manifest}...')
        os.system(f'kubectl apply -f dist/{template_path}/{manifest} -n {namespace}')
