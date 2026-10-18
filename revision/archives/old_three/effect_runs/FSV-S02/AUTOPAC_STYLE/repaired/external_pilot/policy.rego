package external_pilot

import rego.v1

default allow := false

allow if {
    input.subject_role == "authenticated_api_caller"
    input.action == "POST /v1/clients/{clientId}/identifiers"
    input.resource_system == "Fineract"
    input.resource_version == "1.14.0"
    valid_body(input.request.body)
}

allowed_keys := {"documentKey", "documentTypeId", "description", "status"}

valid_body(body) if {
    is_object(body)
    keys := object.keys(body)
    every k in keys {
        k in allowed_keys
        valid_field(k, body[k])
    }
    is_string(body.documentKey)
    is_integer(body.documentTypeId)
}

valid_field(k, v) if {
    k == "documentKey"
    is_string(v)
}

valid_field(k, v) if {
    k == "documentTypeId"
    is_integer(v)
}

valid_field(k, v) if {
    k == "description"
    is_string(v)
}

valid_field(k, v) if {
    k == "status"
    is_string(v)
}