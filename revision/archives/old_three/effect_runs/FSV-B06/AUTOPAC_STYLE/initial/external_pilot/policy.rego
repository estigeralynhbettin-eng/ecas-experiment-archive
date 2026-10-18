package external_pilot

import rego.v1

default allow := false

allow if {
    input.subject.role == "authenticated_api_caller"
    input.action == "POST /v1/loans/{loanId}/transactions/{transactionId}?command=undo"
    input.resource.system == "Fineract"
    input.resource.version == "1.14.0"
    input.trusted.reAgeIsLatestTransaction == true
}
