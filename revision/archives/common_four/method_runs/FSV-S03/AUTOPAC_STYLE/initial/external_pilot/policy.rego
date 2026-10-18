package external_pilot

import rego.v1

default allow := false

allow if {
	is_integer(input.request.body.age)
}
