# Sentry Setup Guide for Kong Auth Service

This guide covers the complete Sentry integration that has been implemented for the Kong Auth Service.

## 🎯 What's Been Implemented

### 1. Sentry SDK Integration
- **Sentry SDK**: Full integration with `sentry-sdk[fastapi]`
- **FastAPI Integration**: Native FastAPI support with automatic request tracking
- **Performance Monitoring**: Distributed tracing and profiling
- **Error Tracking**: Automatic exception capture with context

### 2. Sentry Middleware
- **Request Context**: Automatic request ID, path, and method tracking
- **User Context**: User ID, username, and tenant tracking
- **Performance Monitoring**: Slow request detection (>1 second)
- **Error Capture**: Automatic exception capture with full request context

### 3. Configuration Management
- **Environment Variables**: Centralized Sentry configuration
- **Environment-Specific Settings**: Different behavior for dev/staging/prod
- **PII Handling**: Automatic sensitive data redaction
- **Sampling Control**: Configurable trace and profile sampling rates

## 🚀 Quick Start

### 1. Create Environment File
Copy the example configuration and update with your Sentry DSN:

```bash
cp config.env.example .env
```

Edit `.env` and set your Sentry DSN:
```bash
SENTRY_ENABLED=true
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
SENTRY_ENV=development
```

### 2. Test Configuration
Run the test script to verify everything is working:

```bash
python test_sentry.py
```

### 3. Start the Application
```bash
python run.py
```

## ⚙️ Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SENTRY_ENABLED` | `false` | Enable/disable Sentry integration |
| `SENTRY_DSN` | `None` | Your Sentry project DSN |
| `SENTRY_ENV` | `development` | Environment name (dev/staging/prod) |
| `SENTRY_TRACES_SAMPLE_RATE` | `1.0` | Percentage of requests to trace |
| `SENTRY_PROFILES_SAMPLE_RATE` | `1.0` | Percentage of requests to profile |
| `SENTRY_SEND_DEFAULT_PII` | `true` | Send PII in development |

### Automatic Configuration

The system automatically:
- **Redacts sensitive data** (passwords, tokens, API keys)
- **Adjusts sampling rates** based on environment
- **Enables debug mode** in development
- **Sets appropriate PII handling** per environment

## 🔒 Security Features

### Data Redaction
- **Headers**: Authorization, cookies, API keys
- **Body**: Passwords, tokens, secrets, OTPs
- **Query Params**: Sensitive parameters
- **User Data**: Username redaction in production

### PII Protection
- **Development**: Full user context for debugging
- **Production**: Only user ID, no usernames
- **Automatic**: Based on environment setting

## 📊 Monitoring Features

### Request Tracking
- **Request ID**: Unique identifier for each request
- **Path & Method**: HTTP endpoint information
- **Duration**: Response time monitoring
- **User Context**: Authenticated user information
- **Client IP**: Request origin tracking

### Performance Monitoring
- **Slow Request Detection**: Alerts for requests >1 second
- **Distributed Tracing**: End-to-end request flow
- **Profiling**: CPU and memory usage analysis
- **Custom Metrics**: Business-specific measurements

### Error Tracking
- **Automatic Capture**: All unhandled exceptions
- **Context Enrichment**: Request, user, and system context
- **Stack Traces**: Full error context and stack
- **Breadcrumbs**: Request flow leading to errors

## 🛠️ Usage Examples

### Manual Error Capture
```python
from app.middleware.sentry import capture_request_error

try:
    # Your code here
    pass
except Exception as e:
    capture_request_error(e, request=request, operation="custom_operation")
    raise
```

### Custom Message Capture
```python
from app.middleware.sentry import capture_request_message

capture_request_message(
    "User performed important action",
    level="info",
    request=request,
    action="user_action",
    user_id=user.id
)
```

### User Context Setting
```python
from app.observability.sentry import set_user_context

set_user_context(
    user_id="123",
    username="john_doe",
    tenant_id="acme_corp"
)
```

## 🔧 Middleware Integration

### Automatic Features
- **Request Context**: Every request gets Sentry context
- **User Tracking**: Automatic user context from authentication
- **Error Handling**: Automatic exception capture
- **Performance Monitoring**: Automatic timing and profiling

### Customization
- **Slow Request Threshold**: Configurable (default: 1 second)
- **Context Enrichment**: Automatic request and user data
- **Error Filtering**: Custom error processing logic

## 📈 Dashboard Features

### Error Monitoring
- **Error Rates**: Track error frequency over time
- **Error Distribution**: See which endpoints fail most
- **User Impact**: Understand which users are affected
- **Performance Impact**: See how errors affect response times

### Performance Monitoring
- **Response Times**: Track endpoint performance
- **Throughput**: Monitor request volume
- **Resource Usage**: CPU and memory consumption
- **Slow Queries**: Identify performance bottlenecks

### User Experience
- **User Journeys**: Track user flows through your app
- **Error Context**: See exactly what users were doing
- **Performance Impact**: Understand user experience impact
- **Geographic Data**: See where issues occur

## 🚨 Alerting

### Automatic Alerts
- **Error Spikes**: Sudden increases in error rates
- **Performance Degradation**: Response time increases
- **User Impact**: Errors affecting many users
- **Service Health**: Overall service status

### Custom Alerts
- **Business Metrics**: Custom business logic alerts
- **Threshold Alerts**: Custom performance thresholds
- **User Experience**: User-specific error patterns
- **Integration Issues**: Third-party service problems

## 🔍 Troubleshooting

### Common Issues

#### Sentry Not Capturing Events
1. Check `SENTRY_ENABLED` is `true`
2. Verify `SENTRY_DSN` is set correctly
3. Check environment variables are loaded
4. Verify Sentry initialization in logs

#### Missing Context
1. Ensure middleware is added to FastAPI app
2. Check request state for user information
3. Verify authentication is working
4. Check Sentry middleware order

#### Performance Issues
1. Reduce sampling rates in production
2. Check Sentry quotas and limits
3. Monitor network connectivity to Sentry
4. Review Sentry configuration

### Debug Mode
Enable debug mode in development:
```bash
SENTRY_ENABLED=true
SENTRY_DSN=your-dsn
SENTRY_ENV=development
```

### Logs
Check application logs for Sentry-related messages:
```bash
tail -f logs/app.log | grep -i sentry
```

## 📚 Additional Resources

### Documentation
- [Sentry Python SDK](https://docs.sentry.io/platforms/python/)
- [FastAPI Integration](https://docs.sentry.io/platforms/python/guides/fastapi/)
- [Performance Monitoring](https://docs.sentry.io/product/performance/)

### Best Practices
- **Environment Separation**: Use different DSNs for dev/staging/prod
- **Sampling Control**: Adjust rates based on traffic volume
- **Error Filtering**: Customize what gets sent to Sentry
- **Context Enrichment**: Add business-specific context

### Monitoring
- **Dashboard Setup**: Create custom dashboards for your team
- **Alert Rules**: Set up appropriate alerting thresholds
- **Team Access**: Grant appropriate access to team members
- **Integration**: Connect with other monitoring tools

## 🎉 What's Next?

Your Sentry setup is now complete! Here's what you can do next:

1. **Set your actual Sentry DSN** in the `.env` file
2. **Deploy to different environments** with appropriate DSNs
3. **Create custom dashboards** for your team
4. **Set up alerting** for critical issues
5. **Monitor performance** and user experience
6. **Track business metrics** and user journeys

The system will automatically start capturing errors, performance data, and user context as soon as you restart your application with a valid Sentry DSN.
