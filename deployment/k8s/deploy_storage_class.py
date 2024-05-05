from argparse import ArgumentParser

from utils import render_and_apply


def execute(
    name: str = "local-storage",
    provisioner: str = "microk8s.io/hostpath",
    reclaim_policy: str = "Delete",
    volume_binding_mode: str = "Immediate",
) -> None:
    render_and_apply("manifests/storage_class", namespace=None, context={
        "NAME": name,
        "PROVISIONER": provisioner,
        "RECLAIM_POLICY": reclaim_policy,
        "VOLUME_BINDING_MODE": volume_binding_mode,
    })


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '--name',
        help="Name of the storage class",
        required=False,
    )
    parser.add_argument(
        '--provisioner',
        help="Provisioner to use",
        required=False,
    )
    parser.add_argument(
        '--reclaim-policy',
        help="Reclaim policy",
        required=False,
    )
    parser.add_argument(
        '--volume-binding-mode',
        help="Volume binding mode",
        required=False,
    )

    args = parser.parse_args()
    name = args.name
    provisioner = args.provisioner
    reclaim_policy = args.reclaim_policy
    volume_binding_mode = args.volume_binding_mode

    optional_kwargs = {}
    if name:
        optional_kwargs["name"] = name
    if provisioner:
        optional_kwargs["provisioner"] = provisioner
    if reclaim_policy:
        optional_kwargs["reclaim_policy"] = reclaim_policy
    if volume_binding_mode:
        optional_kwargs["volume_binding_mode"] = volume_binding_mode

    execute(**optional_kwargs)
