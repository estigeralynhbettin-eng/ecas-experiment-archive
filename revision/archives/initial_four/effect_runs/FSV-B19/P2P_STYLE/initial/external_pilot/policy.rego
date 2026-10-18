package external_pilot

import rego.v1

default allow := false

allow if {
    input.subject.id == "authenticated_api_caller"
    input.subject.role == "authenticated_api_caller"
    input.action == "POST /api/resource/Purchase Order"
    input.resource.id == "ERPNext:16.0.0"
    not blocked_supplier
}

blocked_supplier if {
    input.trusted.supplierOnHold == true
    input.trusted.holdType in {"Invoices", "All"}
}