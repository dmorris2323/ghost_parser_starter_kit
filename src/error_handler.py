from fusion_logger import log_event

def safe_run(module_name, func, *args, **kwargs):
    """
    Run a module function with automatic
    error catching, logging, and safe failure.
    Modules themselves handle 'completed' logging on success.
    """
    try:
        result = func(*args, **kwargs)
        # Do NOT log 'completed' here – that lives in the module.
        return result

    except FileNotFoundError as e:
        msg = f"Missing file: {e}"
        print(f"❌ {module_name} – {msg}")
        log_event(module_name, "missing_file", msg)
        return None

    except Exception as e:
        msg = f"Unexpected error: {e}"
        print(f"⚠️ {module_name} – {msg}")
        log_event(module_name, "error", msg)
        return None

