"""Stable integration boundary for the future feature/ML pipeline."""
from pathlib import Path
from .models import TelemetryImport

REQUIRED_TELEMETRY_COLUMNS = {
    "timestamp", "aircraft_id", "subsystem", "vibration_mm_s",
    "temperature_c", "pressure_psi", "oil_level_pct",
}


def validate_telemetry_headers(import_record: TelemetryImport) -> None:
    """Validate CSV headings without loading the upload into application memory."""
    with import_record.file.open("rb") as uploaded:
        header = uploaded.readline().decode("utf-8-sig").strip()
    received = {column.strip() for column in header.split(",")}
    missing = REQUIRED_TELEMETRY_COLUMNS - received
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")


def refresh_features_and_predictions(import_id: int) -> None:
    """Placeholder worker entrypoint; replace the body with the ML pipeline later.

    This intentionally runs outside the request path when a worker is introduced.
    """
    import_record = TelemetryImport.objects.get(pk=import_id)
    import_record.status = TelemetryImport.Status.PROCESSING
    import_record.save(update_fields=["status"])
    try:
        validate_telemetry_headers(import_record)
        # TODO: aggregate daily records, invoke model service, persist scores/explanations.
        import_record.status = TelemetryImport.Status.COMPLETE
        import_record.error_message = ""
    except (UnicodeDecodeError, ValueError) as exc:
        import_record.status = TelemetryImport.Status.FAILED
        import_record.error_message = str(exc)
    import_record.save(update_fields=["status", "error_message"])
