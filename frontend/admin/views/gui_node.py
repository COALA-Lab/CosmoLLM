from typing import Optional, List

from deployment.k8s.deploy_compute import execute as deploy_compute
from deployment.k8s.deploy_config import execute as deploy_config
from deployment.k8s.deploy_experiment_volume import execute as deploy_experiment_volume
from deployment.k8s.deploy_gui import execute as deploy_gui
from deployment.k8s.remove_compute import execute as remove_compute
from deployment.k8s.remove_deployment import execute as remove_deployment
from deployment.k8s.remove_gui import execute as remove_gui
from deployment.k8s.restart_gui import execute as restart_gui
from frontend.admin.utils.rsa import generate_ssh_keys
from frontend.admin.views.compute_node_template import ComputeNodeTemplate
from frontend.utils.view import View
from models.db_model import ChangeType, DBModel


class GUINode(View):
    id: str
    namespace: str = "cosmollm"
    image: str
    domain: str
    apiToken: str
    computeNodeTemplateId: str
    computeNodeCount: int = 1
    adminUser: str = "admin"
    adminPassword: str = "admin"
    mpiHostSlots: int = 2
    storageClass: str = "local-storage"
    storageSize: str = "4Gi"
    mongoUrl: str
    mongoUser: Optional[str] = None
    mongoPassword: Optional[str] = None

    def save(self) -> bool:
        try:
            old_state = self.get(id=self.id)
        except Exception:
            old_state = None

        if old_state:
            self._update_deployment()
        else:
            self._create_deployment()

        return super().save()

    def delete(self) -> None:
        self._delete_deployment()

    def _create_deployment(self):
        Deployment(
            id=self.id,
            gui_node=self,
        ).create()

    def _update_deployment(self):
        old_deployment = Deployment.get(id=self.id)
        new_deployment = old_deployment.model_copy()
        new_deployment.gui_node = self
        new_deployment.update(old_deployment)

    def _delete_deployment(self):
        deployment = Deployment.get(id=self.id)
        deployment.delete()


class Deployment(DBModel):
    id: str
    gui_node: GUINode
    deployed_compute_ids: List[str] = []

    def on_event(self, compute_node: ComputeNodeTemplate, change_type: ChangeType) -> None:
        if change_type == ChangeType.DELETE:
            raise Exception(
                f"Deployment {id} depends on compute node {compute_node.id}, but you are trying to delete it!"
            )
        elif change_type == ChangeType.UPDATE:
            self._update_compute_nodes()
        else:
            raise Exception(f"Cannot handle change type {change_type}!")

    def create(self) -> None:
        self._create_volume()
        self._update_config()
        self._update_compute_nodes()
        self._update_gui_node()

        ComputeNodeTemplate.get(id=self.gui_node.computeNodeTemplateId).subscribe(self)

        self.save()

    def update(self, old_state: 'Deployment') -> None:
        changed_fields = self.get_field_diff(old_state)

        storage_changes = {"storageSize", "storageClass",}
        if storage_changes.intersection(set(changed_fields)):
            raise Exception("Cannot change storage size or class after deployment!")

        if "namespace" in changed_fields:
            raise Exception("Cannot change namespace after deployment!")

        config_changes = {"mongoUrl", "mongoUser", "mongoPassword", "adminUser", "adminPassword", "mpiHostSlots"}
        if config_changes.intersection(set(changed_fields)):
            self._update_config()

        if "computeNodeTemplateId" in changed_fields or "computeNodeCount" in changed_fields:
            if "computeNodeTemplateId" in changed_fields:
                old_node_template = ComputeNodeTemplate.get(id=old_state.gui_node.computeNodeTemplateId)
                old_node_template.unsubscribe(self)
                old_node_template.save()
                new_node_template = ComputeNodeTemplate.get(id=self.gui_node.computeNodeTemplateId)
                new_node_template.subscribe(self)
                new_node_template.save()

            self._update_compute_nodes()

        gui_node_changes = {"image", "domain", "apiToken"}
        if gui_node_changes.intersection(set(changed_fields)):
            self._update_gui_node()

        self.save()

    def delete(self) -> None:
        remove_deployment(
            deployment_id=self.id,
            namespace=self.gui_node.namespace,
        )

        ComputeNodeTemplate.get(id=self.gui_node.computeNodeTemplateId).unsubscribe(self)

        super().delete()

    def _create_volume(self):
        deploy_experiment_volume(
            deployment_id=self.id,
            namespace=self.gui_node.namespace,
            storage_class=self.gui_node.storageClass,
            storage_size=self.gui_node.storageSize,
        )

    def _update_config(self):
        public_key, private_key = generate_ssh_keys()

        deploy_config(
            deployment_id=self.id,
            namespace=self.gui_node.namespace,
            mongo_url=self.gui_node.mongoUrl,
            mongo_user=self.gui_node.mongoUser,
            mongo_password=self.gui_node.mongoPassword,
            admin_user=self.gui_node.adminUser,
            admin_password=self.gui_node.adminPassword,
            mpi_host_slots=self.gui_node.mpiHostSlots,
            ssh_public_key=public_key,
            ssh_private_key=private_key,
        )

    def _update_compute_nodes(self):
        compute_node_template = ComputeNodeTemplate.get(id=self.gui_node.computeNodeTemplateId)

        for compute_id in self.deployed_compute_ids:
            remove_compute(
                deployment_id=self.id,
                namespace=self.gui_node.namespace,
                compute_id=compute_id,
            )

        for i in range(self.gui_node.computeNodeCount):
            compute_id = str(i)
            deploy_compute(
                deployment_id=self.id,
                namespace=self.gui_node.namespace,
                compute_id=f"{self.id}-{compute_id}",
                image=compute_node_template.image,
                cpu_limit=compute_node_template.cpuLimit,
                memory_limit=compute_node_template.memoryLimit,
                cpu_request=compute_node_template.cpuRequest,
                memory_request=compute_node_template.memoryRequest,
            )
            self.deployed_compute_ids.append(compute_id)

        restart_gui(
            deployment_id=self.id,
            namespace=self.gui_node.namespace,
        )

    def _update_gui_node(self):
        remove_gui(
            deployment_id=self.id,
            namespace=self.gui_node.namespace,
        )

        mpi_hosts = ",".join(
            [f"cosmollm-compute-{self.id}-{compute_id}" for compute_id in self.deployed_compute_ids]
        )

        deploy_gui(
            deployment_id=self.id,
            namespace=self.gui_node.namespace,
            image=self.gui_node.image,
            domain=self.gui_node.domain,
            token=self.gui_node.apiToken,
            mpi_hosts=mpi_hosts,
        )
