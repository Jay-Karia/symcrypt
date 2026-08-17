import customtkinter

_LOG_TARGETS = {}
_LOG_COLORS = {}


def register_log_target(target_id, widget, text_color="white"):
    """Map a target ID to a CTk widget that should receive log messages."""
    _LOG_TARGETS[target_id] = widget
    _LOG_COLORS[target_id] = text_color


def create_log_target(root, target_id, *, width=600, height=120, text_color="white", **kwargs):
    """Create a log textbox and register it under the given target ID."""
    widget = customtkinter.CTkTextbox(root, width=width, height=height, **kwargs)
    widget.configure(state="disabled")
    register_log_target(target_id, widget, text_color=text_color)
    return widget


def log(message, target_id="default", text_color=None):
    """Display a message in the widget registered for the provided ID."""
    widget = _LOG_TARGETS.get(target_id)

    clear_log(target_id)

    if widget is None:
        print(f"[{target_id}] {message}")
        return

    # Use provided color or fall back to registered color for this target
    color = text_color or _LOG_COLORS.get(target_id, "white")

    try:
        if hasattr(widget, "configure") and hasattr(widget, "get") and hasattr(widget, "insert"):
            widget.configure(state="normal", text_color=color)
            current_text = widget.get("1.0", "end")
            if current_text and not current_text.endswith("\n"):
                widget.insert("end", "\n")
            widget.insert("end", f"{message}\n")
            widget.see("end")
            widget.configure(state="disabled")
            return
    except Exception:
        pass

    try:
        widget.configure(text=str(message), text_color=color)
    except Exception:
        print(f"[{target_id}] {message}")


def clear_log(target_id="default"):
    widget = _LOG_TARGETS.get(target_id)
    if widget is None:
        return

    try:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.configure(state="disabled")
    except Exception:
        try:
            widget.configure(text="")
        except Exception:
            pass
