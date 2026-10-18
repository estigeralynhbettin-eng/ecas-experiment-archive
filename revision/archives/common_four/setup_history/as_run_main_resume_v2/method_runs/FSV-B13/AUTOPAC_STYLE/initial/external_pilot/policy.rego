package external_pilot

import rego.v1

default allow := false

# Role Allowed to Over Deliver/Receive: users with this role may exceed the allowance percentage.
allow if {
	input.trusted.authorizedRole
}

# Otherwise, the receipt quantity must not exceed the derived maximum (limit-percent inclusive).
allow if {
	input.request.body.qty <= input.trusted.derivedMaximumQty
}
