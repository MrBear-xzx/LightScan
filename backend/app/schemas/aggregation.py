from pydantic import BaseModel, Field


class SeverityCount(BaseModel):
    critical: int = Field(description='?????')
    high: int = Field(description='?????')
    medium: int = Field(description='?????')
    low: int = Field(description='?????')
    unknown: int = Field(description='???????')


class PluginFindingCount(BaseModel):
    plugin_id: str = Field(description='??ID')
    count: int = Field(description='???')


class AssetAggregation(BaseModel):
    asset_id: int = Field(description='??ID')
    total_findings: int = Field(description='????')
    severity_breakdown: SeverityCount = Field(description='??????')
    top_plugins: list[PluginFindingCount] = Field(description='Top ????')


class ScanAggregationResponse(BaseModel):
    tenant_id: str = Field(description='????')
    total_assets: int = Field(description='?????')
    total_findings: int = Field(description='????')
    severity_breakdown: SeverityCount = Field(description='????????')
    assets: list[AssetAggregation] = Field(description='???????')
