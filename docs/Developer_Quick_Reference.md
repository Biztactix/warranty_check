# Developer Quick Reference

## Quick Start

### 1. Clone and Build
```bash
git clone git@github.com:Biztactix/warranty_check.git
cd warranty_check
dotnet build
```

### 2. Configure
```bash
cd src/src/WarrantyCheck.ConsoleApp
cp appsettings.json appsettings.Development.json
# Edit appsettings.Development.json with your settings
```

### 3. Run
```bash
dotnet run
```

## Project Structure

```
WarrantyCheck/
├── src/
│   ├── WarrantyCheck.Core/               # Domain layer
│   │   ├── Models/                       # Domain models
│   │   ├── Abstractions/                 # Interfaces
│   │   ├── Constants/                    # Business constants
│   │   ├── Exceptions/                   # Custom exceptions
│   │   └── Extensions/                   # Helper extensions
│   ├── WarrantyCheck.Infrastructure/     # Infrastructure layer
│   │   ├── Configuration/                # Config services
│   │   ├── Device42/                     # Device42 client
│   │   └── Http/                         # HTTP utilities
│   ├── WarrantyCheck.Providers/          # Vendor providers
│   │   ├── Base/                         # Base provider
│   │   ├── Cisco/                        # Cisco implementation
│   │   ├── Dell/                         # Dell implementation
│   │   └── [Other vendors]/
│   ├── WarrantyCheck.Application/        # Application layer
│   │   ├── Services/                     # Application services
│   │   └── Orchestration/               # Workflow orchestration
│   └── WarrantyCheck.ConsoleApp/         # Entry point
└── tests/                               # Test projects
```

## Common Interfaces

### IWarrantyProvider
```csharp
Task<WarrantyResult> CheckWarrantyAsync(IEnumerable<string> serialNumbers, ...);
Task<ProcessResult> ProcessResultsAsync(WarrantyResult result, ...);
```

### IDevice42Client
```csharp
Task<ApiResult<DeviceResponse>> GetDevicesAsync(int offset, string models, ...);
Task<ApiResult<object>> UploadPurchaseDataAsync(PurchaseRecord data, ...);
```

### IWarrantyService
```csharp
Task<ProcessResult> RunWarrantyCheckAsync(IEnumerable<string>? vendors = null, ...);
```

## Key Models

### Device
```csharp
public class Device
{
    public int DeviceId { get; set; }
    public string SerialNumber { get; set; }
    public string Manufacturer { get; set; }
    public string HardwareModel { get; set; }
}
```

### WarrantyInfo
```csharp
public class WarrantyInfo
{
    public string SerialNumber { get; set; }
    public string ContractId { get; set; }
    public DateTime StartDate { get; set; }
    public DateTime EndDate { get; set; }
    public string ServiceType { get; set; }
    public string VendorName { get; set; }
}
```

### PurchaseRecord
```csharp
public class PurchaseRecord
{
    public string OrderNumber { get; set; }
    public string ContractId { get; set; }
    public DateTime StartDate { get; set; }
    public DateTime EndDate { get; set; }
    public string SerialNumbers { get; set; }
    public string VendorName { get; set; }
}
```

## Configuration

### appsettings.json Structure
```json
{
  "Device42": {
    "BaseUrl": "https://device42.example.com",
    "Username": "username",
    "Password": "password"
  },
  "Discovery": {
    "Cisco": true,
    "Dell": true,
    "HP": false
  },
  "Vendors": {
    "Cisco": {
      "Enabled": true,
      "Url": "https://api.cisco.com/...",
      "ClientId": "client-id",
      "ClientSecret": "client-secret"
    }
  }
}
```

## Creating a New Warranty Provider

### 1. Create Provider Class
```csharp
public class NewVendorWarrantyProvider : WarrantyProviderBase
{
    public override string VendorName => "NewVendor";

    public override async Task<WarrantyResult> CheckWarrantyAsync(
        IEnumerable<string> serialNumbers, 
        bool retry = true,
        CancellationToken cancellationToken = default)
    {
        var result = new WarrantyResult { VendorName = VendorName };
        
        // Implementation here
        
        return result;
    }

    public override async Task<ProcessResult> ProcessResultsAsync(
        WarrantyResult result, 
        Dictionary<string, PurchaseRecord> existingPurchases,
        CancellationToken cancellationToken = default)
    {
        // Implementation here
    }
}
```

### 2. Register in DI Container
```csharp
services.AddScoped<IWarrantyProvider, NewVendorWarrantyProvider>();
```

### 3. Add Configuration
```csharp
public class DiscoveryConfig
{
    // ... existing properties
    public bool NewVendor { get; set; }
}
```

## Common Patterns

### HTTP Client with Retry
```csharp
var policy = HttpPolicyExtensions
    .HandleTransientHttpError()
    .WaitAndRetryAsync(3, retryAttempt => 
        TimeSpan.FromSeconds(Math.Pow(2, retryAttempt)));

var response = await policy.ExecuteAsync(async () =>
{
    return await _httpClient.GetAsync(url, cancellationToken);
});
```

### OAuth 2.0 Token Management
```csharp
private async Task EnsureValidTokenAsync(CancellationToken cancellationToken)
{
    if (_accessToken == null || _tokenExpiry <= DateTime.UtcNow.AddMinutes(5))
    {
        await AcquireTokenAsync(cancellationToken);
    }
}
```

### Batch Processing
```csharp
var batches = serialNumbers.Chunk(batchSize);
foreach (var batch in batches)
{
    await ProcessBatchAsync(batch, result, cancellationToken);
    await Task.Delay(1000, cancellationToken); // Rate limiting
}
```

### Error Handling
```csharp
try
{
    // Operation
}
catch (HttpRequestException ex)
{
    _logger.LogError(ex, "HTTP error for vendor {Vendor}", VendorName);
    result.FailedSerials.AddRange(serialNumbers);
}
catch (VendorApiException ex)
{
    _logger.LogError(ex, "Vendor API error: {Message}", ex.Message);
    throw;
}
```

## Testing

### Unit Test Example
```csharp
[Fact]
public async Task CheckWarrantyAsync_ValidSerials_ReturnsWarrantyInfo()
{
    // Arrange
    var provider = new CiscoWarrantyProvider(_logger, _httpClient, _config);
    var serials = new[] { "ABC123", "DEF456" };

    // Act
    var result = await provider.CheckWarrantyAsync(serials);

    // Assert
    Assert.NotNull(result);
    Assert.Equal(2, result.Warranties.Count);
    Assert.False(result.HasErrors);
}
```

### Mock Setup
```csharp
var mockHttpClient = new Mock<HttpClient>();
var mockLogger = new Mock<ILogger<CiscoWarrantyProvider>>();
var config = new VendorConfig 
{ 
    Enabled = true, 
    Url = "https://api.cisco.com/test" 
};
```

## Debugging

### Enable Debug Logging
```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Debug",
      "WarrantyCheck": "Debug"
    }
  }
}
```

### Common Debug Points
- Configuration validation
- HTTP request/response logging
- Token acquisition/refresh
- Batch processing logic
- Duplicate detection
- Data transformation

## Performance Tips

### Async Best Practices
```csharp
// Good
await SomeAsyncOperation().ConfigureAwait(false);

// Good - parallel processing
var tasks = items.Select(ProcessItemAsync);
var results = await Task.WhenAll(tasks);

// Avoid - blocking async
var result = SomeAsyncOperation().Result; // Don't do this
```

### Memory Management
```csharp
// Use 'using' for disposable resources
using var httpClient = new HttpClient();

// Streaming for large responses
using var stream = await response.Content.ReadAsStreamAsync();
var data = await JsonSerializer.DeserializeAsync<T>(stream);
```

### Batch Optimization
```csharp
// Vendor-specific batch limits
public static class BatchLimits
{
    public const int Cisco = 70;
    public const int Dell = 50;
    public const int HP = 1;    // Single serial per request
}
```

## Common Extensions

### String Extensions
```csharp
serialNumber.ToCleanSerialNumber()      // Normalize serial
serialNumbers.SplitSerialNumbers()      // Parse comma-separated
serviceType.TruncateToLength(64)        // Truncate to limit
```

### DateTime Extensions
```csharp
date.ToDevice42DateString()             // Format for Device42
unixTimestamp.FromUnixTimestamp()       // Convert from Unix
endDate.IsActive()                      // Check if warranty active
```

### Collection Extensions
```csharp
items.Chunk(50)                         // Split into batches
items.IsNullOrEmpty()                   // Check for null/empty
items.WhereNotNull()                    // Filter null items
```

## Environment Variables

```bash
# Override configuration
export DOTNET_ENVIRONMENT=Development
export Device42__BaseUrl=https://dev.device42.com
export Vendors__Cisco__ClientId=dev-client-id
```

## Build & Deploy

### Build
```bash
dotnet build --configuration Release
```

### Test
```bash
dotnet test
```

### Publish
```bash
dotnet publish --configuration Release --output ./publish
```

### Docker (Future)
```dockerfile
FROM mcr.microsoft.com/dotnet/runtime:9.0
COPY publish/ /app/
WORKDIR /app
ENTRYPOINT ["dotnet", "WarrantyCheck.ConsoleApp.dll"]
```

## Troubleshooting

### Common Issues

1. **Configuration not found**
   - Check appsettings.json is copied to output
   - Verify file paths and JSON syntax

2. **HTTP timeouts**
   - Increase TimeoutSeconds in vendor config
   - Check network connectivity

3. **Authentication failures**
   - Verify API credentials
   - Check token expiration handling

4. **Batch size errors**
   - Reduce batch size for vendor
   - Check vendor API limits

### Logs to Check
- Configuration validation errors
- HTTP request/response details
- Token acquisition failures
- Vendor API error responses
- Device42 upload failures

This quick reference should help developers get started quickly and find common patterns and solutions.