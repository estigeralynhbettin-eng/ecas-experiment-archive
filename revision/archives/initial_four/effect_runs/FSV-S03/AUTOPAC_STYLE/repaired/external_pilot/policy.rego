package external_pilot

import rego.v1

default allow := false

allow if {
	input.subject.role == "authenticated_api_caller"
	input.action == "POST /v1/clients/{clientId}/familymembers"
	input.resource.id == "Fineract:1.14.0"
	is_object(input.request.body)
	is_number(input.request.body.age)
}