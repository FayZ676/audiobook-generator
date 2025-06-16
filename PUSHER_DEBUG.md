# Pusher Event Investigation

## Issue
VoiceList component doesn't update automatically when new voice is added through VoiceAddForm, despite pusher events being configured.

## Expected Flow
1. User submits voice through VoiceAddForm
2. Service receives POST /voices request
3. Service uploads voice to S3
4. Service triggers: `pusher_client.trigger("voices-channel", "complete", {"user_id": user_id})`
5. VoiceList component receives pusher event
6. VoiceList calls `handleRevalidateTag("voices")` and `router.refresh()`
7. VoiceList re-renders with updated voice list

## Configuration Verification

### Service Side (Python)
- Channel: `"voices-channel"`
- Event: `"complete"`
- Data: `{"user_id": user_id}`

### Client Side (React)
- Channel: `VOICES_CHANNEL = { channel: "voices-channel", events: ["processing", "complete", "failed"] }`
- Listening for: `"complete"` event (matches service)

## Debugging Steps

### 1. Check Pusher Connection
Look for these console logs:
- `✅ Pusher connected successfully` - Connection established
- `❌ Pusher connection failed` - Connection issues
- Check environment variables are configured

### 2. Check Channel Subscription
Look for these console logs:
- `📡 Subscribing to channel: "voices-channel"` - Subscription attempt
- `✅ Successfully subscribed to channel: "voices-channel"` - Subscription success
- `❌ Failed to subscribe to channel` - Subscription failure

### 3. Check Event Reception
When adding a voice, look for:
- `🚀 VoiceAddForm: Starting to add voice...` - Form submission started
- `✅ VoiceAddForm: Voice added successfully` - Server responded successfully
- `🎉 Pusher event received: "complete" on channel "voices-channel"` - Event received
- `🔔 VoiceList received pusher update` - VoiceList callback triggered

### 4. Potential Issues

#### Environment Variables
Ensure these match between client and service:
- Client: `NEXT_PUBLIC_PUSHER_APP_KEY`
- Client: `NEXT_PUBLIC_PUSHER_CLUSTER`
- Service: `PUSHER_KEY` (should match client key)
- Service: `PUSHER_CLUSTER` (should match client cluster)

#### Timing Issues
- Pusher event might be triggered before client subscription is complete
- Race condition between server pusher event and client-side revalidation

#### Network/Firewall Issues
- Pusher connections might be blocked
- WebSocket connections might not be working

## Next Steps
Based on console output, we can identify:
1. **Connection Issue**: Fix pusher configuration/environment variables
2. **Subscription Issue**: Debug channel subscription problems
3. **Event Issue**: Investigate why events aren't being received
4. **Callback Issue**: Debug why VoiceList update callback isn't working

## Workaround
If pusher events can't be fixed immediately, the `router.refresh()` call in VoiceAddForm provides a temporary solution until the root cause is resolved.