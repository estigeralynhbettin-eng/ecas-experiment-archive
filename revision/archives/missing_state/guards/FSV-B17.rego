package ecas_mechanism_guard

import rego.v1

default allow := false

valid_state if { is_boolean(input.trusted.customerDisabled) }

allow if { data.external_pilot.allow; valid_state }
