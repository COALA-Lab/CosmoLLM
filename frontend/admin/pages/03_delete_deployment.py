from frontend.admin.utils.page_templates import login, delete_view_instance
from frontend.admin.views.gui_node import GUINode


def main():
    if not login():
        return

    delete_view_instance(
        GUINode,
        "This deployment does not exist!",
        "The deployment's ID is required!",
        "Failed to delete deployment!",
        "Deployment deleted!",
        "Deployment ID",
        "Delete deployment",
    )


if __name__ == "__main__":
    main()
