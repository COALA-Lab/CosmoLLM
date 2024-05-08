from frontend.admin.utils.page_templates import login, display_views
from frontend.admin.views.compute_node_template import ComputeNodeTemplate


def main():
    if not login():
        return

    display_views(
        ComputeNodeTemplate,
        "It is forbidden to change the ID of a node!",
        "Failed to update compute node template!",
        "Compute node template updated!",
    )


if __name__ == "__main__":
    main()
