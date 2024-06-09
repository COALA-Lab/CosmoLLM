from frontend.admin.utils.page_templates import login, display_views
from frontend.admin.views.gui_node import GUINode


def main():
    if not login():
        return

    display_views(
        GUINode,
        "It is forbidden to change the ID of a deployment!",
        "Failed to update deployment!",
        "Deployment updated!",
    )


if __name__ == "__main__":
    main()
