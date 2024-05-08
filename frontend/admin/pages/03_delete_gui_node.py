from frontend.admin.utils.page_templates import login, delete_view_instance
from frontend.admin.views.gui_node import GUINode


def main():
    if not login():
        return

    delete_view_instance(
        GUINode,
        "This GUI node does not exist!",
        "The GUI node's ID is required!",
        "Failed to delete GUI node!",
        "GUI node deleted!",
        "GUI node ID",
        "Delete GUI node",
    )


if __name__ == "__main__":
    main()
