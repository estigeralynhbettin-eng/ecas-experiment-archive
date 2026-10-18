package external_pilot

import rego.v1

default allow := false

allow if {
    not blocked_from_purchase_order
}

blocked_from_purchase_order if {
    input.trusted.supplierOnHold == true
    input.trusted.holdType in {"Invoices", "All"}
}