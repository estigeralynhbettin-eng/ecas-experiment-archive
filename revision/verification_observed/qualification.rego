package external_pilot
import rego.v1
default allow := false
allow if { input.probe >= 0 }
