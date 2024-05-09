import os
from typing import Optional
import sys


def create_namespace(namespace: str) -> None:
    os.system(f'kubectl create namespace {namespace}')


def render(template_path: str, context: Optional[dict] = None) -> None:
    cwd = os.getcwd()
    os.chdir(os.path.dirname(__file__))

    if not context:
        context = {}

    for manifest in os.listdir(template_path):
        with open(f'{template_path}/{manifest}') as f:
            manifest_data = f.read()

            for key, value in context.items():
                if value is None:
                    value = ""
                manifest_data = manifest_data.replace("{{" + f"{key}" + "}}", value)

        os.system(f"mkdir -p dist/{template_path}")
        with open(f'dist/{template_path}/{manifest}', 'w') as f:
            f.write(manifest_data)

    os.chdir(cwd)


def render_and_apply(template_path: str, namespace: Optional[str] = None, context: Optional[dict] = None) -> None:
    cwd = os.getcwd()
    os.chdir(os.path.dirname(__file__))

    render(template_path, context)

    if namespace:
        create_namespace(namespace)

    for manifest in os.listdir(f'dist/{template_path}'):
        print(f'Applying {template_path}/{manifest}...')
        os.system(f'kubectl apply -f dist/{template_path}/{manifest} -n {namespace}')

    os.chdir(cwd)


def delete_by_labels(namespace: str, labels: dict) -> None:
    labels = ",".join([f"{key}={value}" for key, value in labels.items()])
    os.system(f'kubectl delete all -l {labels} -n {namespace}')
    os.system(f'kubectl delete pvc -l {labels} -n {namespace}')
    os.system(f'kubectl delete configmap -l {labels} -n {namespace}')
    os.system(f'kubectl delete secret -l {labels} -n {namespace}')
    os.system(f'kubectl delete ingress -l {labels} -n {namespace}')


def delete_by_name(namespace: str, name: str) -> None:
    os.system(f'kubectl delete deployment {name} -n {namespace}')
    os.system(f'kubectl delete service {name} -n {namespace}')
    os.system(f'kubectl delete pvc {name} -n {namespace}')
    os.system(f'kubectl delete configmap {name} -n {namespace}')
    os.system(f'kubectl delete secret {name} -n {namespace}')
    os.system(f'kubectl delete ingress {name} -n {namespace}')


def adjust_pythonpath() -> None:
    # Two dirs up
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir))
    sys.path.append(root_dir)
