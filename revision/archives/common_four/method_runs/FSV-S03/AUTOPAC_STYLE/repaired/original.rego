package external_pilot

import rego.v1

default allow := false

allow if {
    typeof(input.request.body.age) == "number"
    regex.match(`^-?[0-9]+$`, sprintf("%v", [input.request.body.age]))
}