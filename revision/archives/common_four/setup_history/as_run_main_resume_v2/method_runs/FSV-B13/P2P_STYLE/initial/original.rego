package external_pilot

import rego.v1

default allow := false

allow if {
    input.request.body.qty <= input.trusted.derivedMaximumQty
}

allow if {
    input.trusted.authorizedRole == true
}
