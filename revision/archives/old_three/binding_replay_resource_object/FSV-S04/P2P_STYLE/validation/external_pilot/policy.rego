package external_pilot

import rego.v1

default allow := false

allow if {
	input.subject_role == "authenticated_api_caller"
	input.action == "POST /api/resource/Lead"
	input.resource_system == "ERPNext"
	input.resource_version == "16.0.0"
	is_object(input.request.body)
	is_string(input.request.body.email_id)
}
