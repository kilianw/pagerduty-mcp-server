from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import Alert, ListResponseModel
from pagerduty_mcp.utils import paginate


def list_alerts(incident_id: str, limit: int | None = None) -> ListResponseModel[Alert]:
    """List alerts for a specific incident.

    Args:
        incident_id: The ID of the incident whose alerts should be returned.
        limit: Optional maximum number of alerts to return (defaults to global MAX_RESULTS).

    Returns:
        A ListResponseModel containing Alert instances.
    """
    response = paginate(
        client=get_client(),
        entity=f"incidents/{incident_id}/alerts",
        params={"limit": limit} if limit else {},
        maximum_records=limit or 1000,
    )
    alerts = [Alert(**alert) for alert in response]
    return ListResponseModel[Alert](response=alerts)
