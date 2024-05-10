from typing import Optional

from frontend.utils.view import View


class ComputeNodeTemplate(View):
    id: str
    image: str = "nikolasocec/cosmollm-compute-node"
    cpuLimit: str = "2000m"
    memoryLimit: str = "4Gi"
    cpuRequest: Optional[str] = None
    memoryRequest: Optional[str] = None
