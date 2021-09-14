# SLA Report for pending requests

This report provides a list of all requests that are pending to be fulfilled in your account.

In order to provide better analysis the report asks to define 2 different zones:

* Yellow Zone
* Red Zone
  
This zones are used to check if the fulfillment sla has been broken or not:

Requests will be marked in green zone if time passed between creation date and amount of days
to consider it yellow zone did not pass. Requests will be marked as yellow if creation date exceeds 
amount of days of yellow zone but is below red one and marked as red otherwise.
