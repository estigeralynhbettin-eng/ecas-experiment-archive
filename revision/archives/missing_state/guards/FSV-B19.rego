package ecas_mechanism_guard

import rego.v1

default allow := false

valid_state if { input.trusted.supplierOnHold == false }

valid_state if { input.trusted.supplierOnHold == true; input.trusted.holdType in {"All", "Invoices", "Payments"} }

allow if { data.external_pilot.allow; valid_state }
