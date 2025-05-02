from radioforms.models.dataclass_forms import ICS213Form
import inspect

# Examine the method signature directly
print(inspect.signature(ICS213Form.reply))

# Create a simple instance to check the bound method
form = ICS213Form()
bound_method = form.reply
print(inspect.signature(bound_method))

# Print the actual method source
print(inspect.getsource(ICS213Form.reply))

# Handle the form in a proper sequence
form = ICS213Form(form_id="test-123")
form.state = form.state.RECEIVED  # Set the state to RECEIVED directly
form.reply("Test reply", "Test signature")
print(f"Reply added: {form.reply}")  # This might be confusing as reply is both a field and a method
print(f"State: {form.state}")
print(f"Recipient signature: {form.recipient_signature}")
