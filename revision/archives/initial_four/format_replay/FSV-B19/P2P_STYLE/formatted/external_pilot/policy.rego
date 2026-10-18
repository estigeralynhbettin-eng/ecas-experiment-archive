package external_pilot

import rego.v1

default allow := false

allow if {
	not blocked_supplier
}

blocked_supplier if {
	input.trusted.supplierOnHold == true
	input.trusted.holdType in {"Invoices", "All"}
}
