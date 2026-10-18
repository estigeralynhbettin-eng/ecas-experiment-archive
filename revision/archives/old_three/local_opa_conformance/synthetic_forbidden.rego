package external_pilot
import rego.v1
allow if { http.send({"method":"GET","url":"https://example.invalid"}) }
