from time import sleep
from typing import Optional, Type

import streamlit as st

from frontend.utils.auth import Auth
from frontend.utils.view import View


def login() -> bool:
    st.sidebar.title("Actions")

    auth = Auth()

    if auth.login():
        return True

    return False


def display_views(
        view_cls: Type[View],
        primary_value_change_error_message: Optional[str] = None,
        save_error_message: Optional[str] = None,
        update_success_message: Optional[str] = None,
) -> None:
    if primary_value_change_error_message is None:
        primary_value_change_error_message = "The object's primary value cannot be changed!"
    if save_error_message is None:
        save_error_message = "Failed to update object!"
    if update_success_message is None:
        update_success_message = "Object updated!"

    for view in view_cls.filter():
        st.markdown("## " + view.get_primary_value())
        if (updated_view := view_cls.execute_form(view)) is not None:
            if updated_view.get_primary_value() != view.get_primary_value():
                st.error(primary_value_change_error_message)
                continue

            try:
                updated_view.save()
            except Exception as e:
                st.error(f"{save_error_message} error={e}")
                continue
            st.info(update_success_message)


def new_view_instance(
        view_cls: Type[View],
        view_exists_error_message: Optional[str] = None,
        save_error_message: Optional[str] = None,
        new_view_success_message: Optional[str] = None
) -> None:
    if view_exists_error_message is None:
        view_exists_error_message = "The object already exists!"
    if save_error_message is None:
        save_error_message = "Failed to create object!"
    if new_view_success_message is None:
        new_view_success_message = "Object added!"

    if (new_view := view_cls.execute_form()) is not None:
        try:
            view_cls.get(id=new_view.id)
        except Exception:
            # This is a new object
            try:
                new_view.save()
            except Exception as e:
                st.error(f"{save_error_message} error={e}")
                return
            st.info(new_view_success_message)
        else:
            st.error(view_exists_error_message)
            return


def delete_view_instance(
        view_cls: Type[View],
        view_not_found_error_message: Optional[str] = None,
        primary_value_required_error_message: Optional[str] = None,
        delete_error_message: Optional[str] = None,
        view_deleted_message: Optional[str] = None,
        primary_value_input_label: Optional[str] = None,
        form_submit_button_label: Optional[str] = None,
        confirm_delete_button_label: Optional[str] = None,
) -> None:
    if view_not_found_error_message is None:
        view_not_found_error_message = "View instance not found!"
    if primary_value_required_error_message is None:
        primary_value_required_error_message = "Primary value is required!"
    if delete_error_message is None:
        delete_error_message = "Failed to delete view instance!"
    if view_deleted_message is None:
        view_deleted_message = "View instance deleted!"
    if primary_value_input_label is None:
        primary_value_input_label = "Primary value"
    if form_submit_button_label is None:
        form_submit_button_label = "Delete view instance"
    if confirm_delete_button_label is None:
        confirm_delete_button_label = "Confirm deletion"

    def delete_view(view: View):
        def _delete_view():
            try:
                view.delete()
                st.info(view_deleted_message)
            except Exception as e:
                st.error(f"{delete_error_message} error={e}")
                sleep(5)
            finally:
                sleep(2)

        return _delete_view

    form_key = "delete-" + view_cls.__name__
    with st.form(key=form_key):
        view_primary_value = st.text_input(primary_value_input_label)
        submit = st.form_submit_button(form_submit_button_label)

    if not submit:
        return

    if not view_primary_value:
        st.error(primary_value_required_error_message)
        return

    try:
        primary_key = view_cls.get_primary_key()
        view_instance = view_cls.get(**{primary_key: view_primary_value})
    except Exception:
        st.error(view_not_found_error_message)
        return

    st.button(confirm_delete_button_label, on_click=delete_view(view_instance))
