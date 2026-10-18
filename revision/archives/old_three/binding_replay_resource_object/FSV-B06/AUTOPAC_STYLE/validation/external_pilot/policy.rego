package external_pilot

import rego.v1

default allow := false

allow if {
	input.subject_role == "authenticated_api_caller"
	input.action == "POST /v1/loans/{loanId}/transactions/{transactionId}?command=undo"
	input.resource_system == "Fineract"
	input.resource_version == "1.14.0"
	not re_age_reversal_blocked
}

re_age_reversal_blocked if {
	input.trusted.reAgeIsLatestTransaction == false
}
