from frontend.admin.utils.page_templates import login, delete_view_instance
from frontend.admin.views.compute_node_template import ComputeNodeTemplate


def main():
    if not login():
        return

    delete_view_instance(
        ComputeNodeTemplate,
        "This compute node does not exist!",
        "The compute node's ID is required!",
        "Failed to delete compute node!",
        "Compute node deleted!",
        "Compute node ID",
        "Delete compute node",
    )


if __name__ == "__main__":
    main()
