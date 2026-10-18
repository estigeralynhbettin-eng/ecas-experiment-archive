package external_pilot

import rego.v1

default allow := false

allow if {
	not blocked_for_purchase_order
}

blocked_for_purchase_order if {
	input.trusted.supplierOnHold == true
	input.trusted.holdType in {"Invoices", "All"}
}
