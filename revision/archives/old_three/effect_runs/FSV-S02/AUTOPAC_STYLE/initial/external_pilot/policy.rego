package external_pilot

import rego.v1

default allow := false

allow if {
    input.subject.role == "authenticated_api_caller"
    input.action == "POST /v1/clients/{clientId}/identifiers"
    input.resource.system == "Fineract"
    input.resource.version == "1.14.0"
    input.request.body.documentKey
    input.request.body.documentTypeId
}