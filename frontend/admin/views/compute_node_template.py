from typing import Optional

from frontend.utils.view import View
from frontend.admin.utils.validation import validate_id


class ComputeNodeTemplate(View):
    id: str
    image: str = "nikolasocec/cosmollm-compute-node"
    cpuLimit: str = "2000m"
    memoryLimit: str = "4Gi"
    cpuRequest: Optional[str] = None
    memoryRequest: Optional[str] = None

    def save(self, notify: bool = True) -> bool:
        if not validate_id(self.id):
            raise Exception(
                "Compute node template id must use only lowercase letters, numbers and dashes (-)! "
                "It also must start with a letter!"
            )

        return super().save(notify)
