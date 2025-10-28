# Testing Guide - Response Tracker Agent

## Overview

The Response Tracker Agent monitors email campaign performance using Apollo API to track opens, clicks, replies, and other engagement metrics.

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# Apollo API Configuration
APOLLO_API_KEY=your_apollo_api_key_here
APOLLO_CAMPAIGN_ID=your_campaign_sequence_id_here
```

### Available Campaign IDs

Based on your Apollo account, you have the following campaign(s):

- **Campaign ID**: `68f48e9009062e00111792e2`
- **Name**: test
- **Status**: Inactive
- **Created**: 2025-10-19

## Running Tests

### Test Response Tracker Agent

```bash
python test_response_tracker.py
```

This will:
1. Initialize the Response Tracker Agent with Apollo API
2. Track responses for the configured campaign ID
3. Calculate engagement metrics (open rate, click rate, reply rate)
4. Display sample responses and activities
5. Verify Apollo API connectivity
6. List available campaigns in your account

### Test Google Sheets Feedback Agent

```bash
python test_google_sheets.py
```

This will:
1. Initialize Google Sheets client
2. Create required sheets (Recommendations, Performance, Campaign_Data)
3. Write test recommendations
4. Write performance metrics
5. Provide link to view results in Google Sheets

## Using Real Campaign Data

To test with your actual campaign:

1. **Update your `.env` file**:
   ```bash
   APOLLO_CAMPAIGN_ID=68f48e9009062e00111792e2
   ```

2. **Run the test**:
   ```bash
   python test_response_tracker.py
   ```

3. **Expected Output**:
   - Campaign activities and responses
   - Engagement metrics (open/click/reply rates)
   - Contact information for responders
   - Activity timestamps and types

## Integration Testing

To test the complete workflow (Response Tracker → Feedback Trainer):

1. **Track campaign responses**:
   ```python
   from agents.response_tracker_agent import ResponseTrackerAgent
   from agents.base_agent import AgentInput
   
   tracker = ResponseTrackerAgent(
       agent_id="response_tracker",
       instructions="Monitor campaign responses",
       tools=[{"name": "ApolloAPI", "config": {"api_key": "..."}}]
   )
   
   result = tracker.execute(AgentInput(
       agent_id="response_tracker",
       data={"campaign_id": "68f48e9009062e00111792e2"}
   ))
   ```

2. **Analyze with Feedback Trainer**:
   ```python
   from agents.feedback_trainer_agent import FeedbackTrainerAgent
   
   trainer = FeedbackTrainerAgent(
       agent_id="feedback_trainer",
       instructions="Analyze campaign performance",
       tools=[{"name": "GoogleSheets", "config": {...}}]
   )
   
   feedback = trainer.execute(AgentInput(
       agent_id="feedback_trainer",
       data={
           "responses": result.data["responses"],
           "engagement_metrics": result.data["engagement_metrics"]
       }
   ))
   ```

## Troubleshooting

### No Responses Found

If you see "No responses found", this could mean:
- The campaign ID doesn't exist
- The campaign has no activities yet
- The campaign is inactive

**Solution**: Use an active campaign with sent emails.

### API Authentication Error

If you see 422 or authentication errors:
- Verify your `APOLLO_API_KEY` is correct
- Check that the API key is active in Apollo settings
- Ensure you're using the X-Api-Key header format

### Campaign Not Found (404)

If you see 404 errors:
- Verify the campaign ID is correct
- Check that the campaign exists in your Apollo account
- Use the campaign ID from Test 3 output

## API Rate Limits

Apollo API has rate limits:
- Free tier: Limited requests per day
- Paid tier: Higher limits

Monitor your usage to avoid hitting limits during testing.

## Next Steps

1. Create an active email campaign in Apollo
2. Send test emails to real contacts
3. Wait for engagement (opens, clicks, replies)
4. Run the Response Tracker to see real metrics
5. Feed the data to Feedback Trainer for AI recommendations
6. Review recommendations in Google Sheets

## Support

For issues or questions:
- Check Apollo API documentation: https://docs.apollo.io/
- Review agent logs in console output
- Verify environment variables are set correctly
