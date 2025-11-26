# sins_poc
Proof of concept for recast with modern architecture
# actors
customer 

service_agent

service_provider
# user stories
as a customer, i want to see if i am listed as a customer

as a service_agent, i want to see if the customer is listed

as a service_agent, i want to create, update or delete customers in the customer list

as a service_provider, i want to maintain the list and provide it to service_agents

as a service_provider, i want to allow a customer to check for themselves or someone similiar in the list

as a service_provider, i want to provide the list to service_agents at multiple distinct locations

as a service_provider, i want to ensure the list is syncronised between multiple distinct locations

as a service_provider, i want to ensure that a service agent can create, update or delete customers in the customer list

as a service_provider, i want to be able to delete customers from the list after a certain period of time

as a service_provider, i need to be able to report all transactions

# proposed architecture
https, python, kafka, ELK.

# environment
containers
