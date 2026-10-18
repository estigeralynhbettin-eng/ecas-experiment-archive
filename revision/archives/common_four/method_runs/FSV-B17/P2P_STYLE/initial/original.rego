package external_pilot

import rego.v1

default allow := false

allow if {
    not input.trusted.customerDisabled
}