from frontend.admin.utils.page_templates import login, new_view_instance
from frontend.admin.views.gui_node import GUINode


def main():
    if not login():
        return

    new_view_instance(
        GUINode,
        "This deployment already exists!",
        "Failed to add deployment!",
        "Deployment added!",
    )


if __name__ == "__main__":
    main()
