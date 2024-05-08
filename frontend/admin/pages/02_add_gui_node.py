from frontend.admin.utils.page_templates import login, new_view_instance
from frontend.admin.views.gui_node import GUINode


def main():
    if not login():
        return

    new_view_instance(
        GUINode,
        "This GUI node already exists!",
        "Failed to add GUI node!",
        "GUI node added!",
    )


if __name__ == "__main__":
    main()
