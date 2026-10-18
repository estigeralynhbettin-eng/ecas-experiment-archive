package external_pilot

import rego.v1

default allow := false

allow if {
    input.action == "POST /api/resource/Sales Order"
    input.resource.id == "ERPNext:16.0.0"
    input.trusted.customerDisabled == false
}
