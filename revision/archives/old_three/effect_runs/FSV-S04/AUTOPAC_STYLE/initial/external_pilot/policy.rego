package external_pilot

import rego.v1

default allow := false

allow if {
    input.subject.role == "authenticated_api_caller"
    input.action == "POST /api/resource/Lead"
    input.resource.system == "ERPNext"
    input.resource.version == "16.0.0"
}