from frontend.admin.utils.page_templates import login, new_view_instance
from frontend.admin.views.compute_node_template import ComputeNodeTemplate


def main():
    if not login():
        return

    new_view_instance(
        ComputeNodeTemplate,
        "This compute node already exists!",
        "Failed to add compute node!",
        "Compute node added!",
    )


if __name__ == "__main__":
    main()
