# Nightscout Inventory
> Super basic Inventory / Stock monitoring for diabetes consumables needles, lancets, test strips using Nightscout

![pic-selected-230526-1020-03](https://github.com/ghomasHudson/nightscout_inventory/assets/13795113/5219f1f2-f24b-44f5-8efe-c7b488ae6a94)

A basic tool to track diabetes consumables from nightscout logs. Currently this is highly 'me-specific', based on my needs on MDI and makes the following assumptions:

- Basal insulin is given once per day before 10AM
- Each fingerprick test uses 1 test strip and 1 lancet.
- Each Bolus uses 1 needle.

If you wanted to use it, you'd have to modify all this to suit your needs. If there's demand, I'll make it more configurable.

## Config

The following env variables are required:
- `NIGHTSCOUT_URL` - the `https://www.nightscout.mydomain.com` address to your nightscout server
- `ACCESS_TOKEN` - A nightscout access token so you can authenticate. Make a new subject in the "Admin Tools" section with read access for this to work.
- `GLUCOSE_METER_DEVICE` - Put a string in here which uniquely identifies the bluetooth device you're using for fingerpricks
