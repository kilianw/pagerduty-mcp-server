from datetime import datetime
from typing import Any, Literal

from pydantic import AliasChoices, BaseModel, Field, computed_field

from pagerduty_mcp.models.references import IncidentReference, ServiceReference


class Alert(BaseModel):
    """Fuller representation of a PagerDuty Alert.

    Fields remain optional where appropriate to stay resilient to API variations
    while providing richer context for tools and UIs.
    """

    # Core identifiers and status
    id: str = Field(description="The ID of the alert")
    summary: str | None = Field(default=None, description="A short summary of the alert")
    status: str | None = Field(default=None, description="The current status of the alert")
    severity: str | None = Field(default=None, description="The severity of the alert")
    created_at: datetime | None = Field(default=None, description="When the alert was created")
    updated_at: datetime | None = Field(default=None, description="When the alert was last updated")

    # Relationships
    incident: IncidentReference | None = Field(default=None, description="Incident this alert belongs to")
    service: ServiceReference | None = Field(default=None, description="Service associated with this alert")

    # Common metadata present on Alerts
    html_url: str | None = Field(default=None, description="URL to view the alert in PagerDuty UI")
    alert_key: str | None = Field(default=None, description="A unique key used to correlate deduplicated alerts")
    source: str | None = Field(default=None, description="The unique location of the affected system, e.g., hostname")
    component: str | None = Field(default=None, description="The part or component of the affected system")
    group: str | None = Field(default=None, description="A cluster or grouping of sources")
    klass: str | None = Field(
        default=None,
        validation_alias=AliasChoices("klass", "class"),
        serialization_alias="class",
        description="The class/type of the event",
    )

    # Flexible structures to avoid being overly prescriptive
    body: dict[str, Any] | None = Field(default=None, description="Structured body returned by the API")
    details: dict[str, Any] | None = Field(default=None, description="Additional details for the alert")
    integration: dict[str, Any] | None = Field(default=None, description="Integration information for the alert")

    @computed_field
    @property
    def type(self) -> Literal["alert"]:
        return "alert"
