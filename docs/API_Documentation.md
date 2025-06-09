# Warranty Check API Documentation

This document provides comprehensive API documentation for the Warranty Check C# .NET 9 package.

## Table of Contents

- [Core Abstractions](#core-abstractions)
- [Models](#models)
- [Configuration](#configuration)
- [Providers](#providers)
- [Services](#services)
- [Extensions](#extensions)
- [Exceptions](#exceptions)
- [Usage Examples](#usage-examples)

## Core Abstractions

### IWarrantyProvider

The main interface for implementing vendor-specific warranty providers.

```csharp
public interface IWarrantyProvider
{
    string VendorName { get; }
    bool IsEnabled { get; }
    
    Task<WarrantyResult> CheckWarrantyAsync(
        IEnumerable<string> serialNumbers, 
        bool retry = true,
        CancellationToken cancellationToken = default);

    Task<ProcessResult> ProcessResultsAsync(
        WarrantyResult result, 
        Dictionary<string, PurchaseRecord> existingPurchases,
        CancellationToken cancellationToken = default);
        
    Task<bool> ValidateConfigurationAsync(CancellationToken cancellationToken = default);
}
```

**Properties:**
- `VendorName`: Gets the name of the vendor (e.g., "Cisco", "Dell", "HP")
- `IsEnabled`: Gets whether this provider is enabled in configuration

**Methods:**
- `CheckWarrantyAsync`: Retrieves warranty information for the provided serial numbers
- `ProcessResultsAsync`: Processes warranty results and creates purchase records
- `ValidateConfigurationAsync`: Validates the vendor's configuration settings

### IDevice42Client

Interface for interacting with the Device42 REST API.

```csharp
public interface IDevice42Client
{
    Task<ApiResult<DeviceResponse>> GetDevicesAsync(
        int offset, 
        string hardwareModels, 
        CancellationToken cancellationToken = default);

    Task<ApiResult<HardwareModelResponse>> GetHardwareModelsAsync(
        CancellationToken cancellationToken = default);

    Task<ApiResult<PurchaseResponse>> GetPurchasesAsync(
        CancellationToken cancellationToken = default);

    Task<ApiResult<object>> UploadPurchaseDataAsync(
        PurchaseRecord purchaseData, 
        CancellationToken cancellationToken = default);

    Task<ApiResult<object>> UploadLifecycleEventAsync(
        Dictionary<string, object> lifecycleData, 
        CancellationToken cancellationToken = default);

    Task<ApiResult<LifecycleEventResponse>> GetLifecycleEventsAsync(
        CancellationToken cancellationToken = default);

    Task<bool> TestConnectionAsync(CancellationToken cancellationToken = default);
}
```

**Methods:**
- `GetDevicesAsync`: Retrieves devices from Device42 with pagination
- `GetHardwareModelsAsync`: Gets all hardware models from Device42
- `GetPurchasesAsync`: Retrieves existing purchase records
- `UploadPurchaseDataAsync`: Uploads new purchase/warranty data
- `UploadLifecycleEventAsync`: Uploads lifecycle event data
- `GetLifecycleEventsAsync`: Retrieves lifecycle events
- `TestConnectionAsync`: Tests connectivity to Device42

### IWarrantyService

Main service orchestrating warranty checks across vendors.

```csharp
public interface IWarrantyService
{
    Task<ProcessResult> RunWarrantyCheckAsync(
        IEnumerable<string>? specificVendors = null,
        CancellationToken cancellationToken = default);

    Task<ProcessResult> RunWarrantyCheckForVendorAsync(
        string vendorName,
        IEnumerable<string> serialNumbers,
        CancellationToken cancellationToken = default);

    Task<DeviceResponse> DiscoverDevicesAsync(
        string vendorName,
        int offset = 0,
        CancellationToken cancellationToken = default);

    Task<Dictionary<string, PurchaseRecord>> GetExistingPurchasesAsync(
        CancellationToken cancellationToken = default);

    Task<bool> ValidateVendorConfigurationAsync(
        string vendorName,
        CancellationToken cancellationToken = default);

    IEnumerable<string> GetEnabledVendors();
}
```

### IConfigurationService

Service for managing application configuration.

```csharp
public interface IConfigurationService
{
    AppSettings GetSettings();
    VendorConfig GetVendorConfig(string vendorName);
    Device42Config GetDevice42Config();
    DiscoveryConfig GetDiscoveryConfig();
    
    Task<bool> ValidateConfigurationAsync(CancellationToken cancellationToken = default);
    Task SaveConfigurationAsync(AppSettings settings, CancellationToken cancellationToken = default);
    Task ReloadConfigurationAsync(CancellationToken cancellationToken = default);
}
```

## Models

### Device

Represents a device in Device42.

```csharp
public class Device
{
    public int DeviceId { get; set; }
    public string SerialNumber { get; set; } = string.Empty;
    public string Manufacturer { get; set; } = string.Empty;
    public string HardwareModel { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string? Notes { get; set; }
    public DateTime? LastUpdated { get; set; }
}
```

### WarrantyInfo

Represents warranty information for a device.

```csharp
public class WarrantyInfo
{
    public string SerialNumber { get; set; } = string.Empty;
    public string ContractId { get; set; } = string.Empty;
    public DateTime StartDate { get; set; }
    public DateTime EndDate { get; set; }
    public string ServiceType { get; set; } = string.Empty;
    public string ContractType { get; set; } = "Warranty/Service";
    public string VendorName { get; set; } = string.Empty;
    public string? ServiceLevel { get; set; }
    public string? Notes { get; set; }
    
    // Computed Properties
    public bool IsActive => EndDate >= DateTime.UtcNow;
    public TimeSpan RemainingTime => EndDate > DateTime.UtcNow ? EndDate - DateTime.UtcNow : TimeSpan.Zero;
}
```

### PurchaseRecord

Represents a purchase/warranty record to be uploaded to Device42.

```csharp
public class PurchaseRecord
{
    public int? PurchaseId { get; set; }
    public string OrderNumber { get; set; } = string.Empty;
    public int LineNumber { get; set; }
    public string ContractId { get; set; } = string.Empty;
    public DateTime StartDate { get; set; }
    public DateTime EndDate { get; set; }
    public DateTime PurchaseDate { get; set; }
    public string VendorName { get; set; } = string.Empty;
    public string SerialNumbers { get; set; } = string.Empty;
    public string ServiceType { get; set; } = string.Empty;
    public string ContractType { get; set; } = "Warranty/Service";
    public string LineItemType { get; set; } = "device";
    public string LineType { get; set; } = "contract";
    public bool Completed { get; set; } = true;
    public bool LineCompleted { get; set; } = true;
    public bool ForceUpdate { get; set; }
    public string? Notes { get; set; }
    
    // Computed Properties
    public string Hash => GenerateHash();
    
    private string GenerateHash()
    {
        return $"{SerialNumbers}_{ContractId}_{StartDate:yyyy-MM-dd}_{EndDate:yyyy-MM-dd}";
    }
}
```

### ApiResult<T>

Generic wrapper for API operation results.

```csharp
public class ApiResult<T>
{
    public bool Success { get; set; }
    public T? Data { get; set; }
    public string? ErrorMessage { get; set; }
    public Exception? Exception { get; set; }
    public int? StatusCode { get; set; }

    public static ApiResult<T> SuccessResult(T data);
    public static ApiResult<T> FailureResult(string errorMessage, Exception? exception = null, int? statusCode = null);
}
```

### WarrantyResult

Result of a warranty check operation.

```csharp
public class WarrantyResult
{
    public List<WarrantyInfo> Warranties { get; set; } = new();
    public List<string> ProcessedSerials { get; set; } = new();
    public List<string> FailedSerials { get; set; } = new();
    public string VendorName { get; set; } = string.Empty;
    public DateTime ProcessedAt { get; set; } = DateTime.UtcNow;
    public TimeSpan ProcessingTime { get; set; }
    
    // Computed Properties
    public bool HasErrors => FailedSerials.Any();
    public int SuccessCount => ProcessedSerials.Count;
    public int ErrorCount => FailedSerials.Count;
}
```

### ProcessResult

Result of processing warranty data.

```csharp
public class ProcessResult
{
    public int UploadedCount { get; set; }
    public int SkippedCount { get; set; }
    public int ErrorCount { get; set; }
    public List<string> ErrorMessages { get; set; } = new();
    public Dictionary<string, PurchaseRecord> CreatedPurchases { get; set; } = new();
    
    // Computed Properties
    public bool HasErrors => ErrorCount > 0;
}
```

## Configuration

### AppSettings

Root configuration object.

```csharp
public class AppSettings
{
    public Device42Config Device42 { get; set; } = new();
    public DiscoveryConfig Discovery { get; set; } = new();
    public Dictionary<string, VendorConfig> Vendors { get; set; } = new();
    public GeneralSettings General { get; set; } = new();
}
```

### Device42Config

Configuration for Device42 connection.

```csharp
public class Device42Config
{
    public string BaseUrl { get; set; } = string.Empty;
    public string Username { get; set; } = string.Empty;
    public string Password { get; set; } = string.Empty;
    public bool VerifySsl { get; set; } = true;
    public int TimeoutSeconds { get; set; } = 30;
}
```

### VendorConfig

Configuration for vendor-specific settings.

```csharp
public class VendorConfig
{
    public bool Enabled { get; set; }
    public string Url { get; set; } = string.Empty;
    public string? ClientId { get; set; }        // For OAuth vendors
    public string? ClientSecret { get; set; }    // For OAuth vendors
    public string? ApiKey { get; set; }          // For API key vendors
    public string? ApiSecret { get; set; }       // For API secret vendors
    public int TimeoutSeconds { get; set; } = 30;
    public int RetryCount { get; set; } = 3;
    public int BatchSize { get; set; } = 50;
}
```

### DiscoveryConfig

Configuration for device discovery.

```csharp
public class DiscoveryConfig
{
    public bool Cisco { get; set; }
    public bool Dell { get; set; }
    public bool HP { get; set; }
    public bool IBM { get; set; }
    public bool Lenovo { get; set; }
    public bool Meraki { get; set; }
    public bool ForceUpdate { get; set; }
    public int BatchSize { get; set; } = 50;
}
```

## Providers

### Base Provider Pattern

All warranty providers should inherit from a base class implementing `IWarrantyProvider`:

```csharp
public abstract class WarrantyProviderBase : IWarrantyProvider
{
    protected readonly ILogger<WarrantyProviderBase> _logger;
    protected readonly HttpClient _httpClient;
    protected readonly VendorConfig _config;

    public abstract string VendorName { get; }
    public virtual bool IsEnabled => _config.Enabled;

    protected WarrantyProviderBase(
        ILogger<WarrantyProviderBase> logger,
        HttpClient httpClient,
        VendorConfig config)
    {
        _logger = logger;
        _httpClient = httpClient;
        _config = config;
    }

    public abstract Task<WarrantyResult> CheckWarrantyAsync(
        IEnumerable<string> serialNumbers, 
        bool retry = true,
        CancellationToken cancellationToken = default);

    public abstract Task<ProcessResult> ProcessResultsAsync(
        WarrantyResult result, 
        Dictionary<string, PurchaseRecord> existingPurchases,
        CancellationToken cancellationToken = default);

    public virtual async Task<bool> ValidateConfigurationAsync(CancellationToken cancellationToken = default)
    {
        // Base validation logic
        return !string.IsNullOrWhiteSpace(_config.Url);
    }

    protected string GenerateRandomOrderNumber()
    {
        var random = new Random();
        return string.Concat(Enumerable.Range(0, 9).Select(_ => random.Next(0, 10)));
    }
}
```

### Vendor-Specific Implementations

#### OAuth 2.0 Providers (Cisco, Dell)

```csharp
public class CiscoWarrantyProvider : WarrantyProviderBase
{
    public override string VendorName => "Cisco";
    
    private string? _accessToken;
    private DateTime? _tokenExpiry;

    public override async Task<WarrantyResult> CheckWarrantyAsync(
        IEnumerable<string> serialNumbers, 
        bool retry = true,
        CancellationToken cancellationToken = default)
    {
        await EnsureValidTokenAsync(cancellationToken);
        
        var result = new WarrantyResult { VendorName = VendorName };
        var startTime = DateTime.UtcNow;
        
        try
        {
            // Cisco API allows max 70 serials per request
            var batches = serialNumbers.Chunk(70);
            
            foreach (var batch in batches)
            {
                await ProcessBatchAsync(batch, result, cancellationToken);
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error checking Cisco warranty for serials: {Serials}", 
                string.Join(",", serialNumbers));
            result.FailedSerials.AddRange(serialNumbers);
        }
        
        result.ProcessingTime = DateTime.UtcNow - startTime;
        return result;
    }

    private async Task EnsureValidTokenAsync(CancellationToken cancellationToken)
    {
        if (_accessToken == null || _tokenExpiry <= DateTime.UtcNow.AddMinutes(5))
        {
            await AcquireTokenAsync(cancellationToken);
        }
    }

    private async Task AcquireTokenAsync(CancellationToken cancellationToken)
    {
        var tokenRequest = new Dictionary<string, string>
        {
            {"grant_type", "client_credentials"},
            {"client_id", _config.ClientId!},
            {"client_secret", _config.ClientSecret!}
        };

        using var content = new FormUrlEncodedContent(tokenRequest);
        var response = await _httpClient.PostAsync("oauth2/token", content, cancellationToken);
        
        response.EnsureSuccessStatusCode();
        
        var tokenResponse = await response.Content.ReadFromJsonAsync<TokenResponse>(cancellationToken);
        _accessToken = tokenResponse.AccessToken;
        _tokenExpiry = DateTime.UtcNow.AddSeconds(tokenResponse.ExpiresIn - 60); // 1 minute buffer
    }
}
```

#### API Key Providers (HP, Meraki)

```csharp
public class HPWarrantyProvider : WarrantyProviderBase
{
    public override string VendorName => "HP";

    public override async Task<WarrantyResult> CheckWarrantyAsync(
        IEnumerable<string> serialNumbers, 
        bool retry = true,
        CancellationToken cancellationToken = default)
    {
        var result = new WarrantyResult { VendorName = VendorName };
        var startTime = DateTime.UtcNow;
        
        _httpClient.DefaultRequestHeaders.Clear();
        _httpClient.DefaultRequestHeaders.Add("X-API-Key", _config.ApiKey);
        
        try
        {
            foreach (var serial in serialNumbers)
            {
                await ProcessSerialAsync(serial, result, cancellationToken);
                
                // Rate limiting
                await Task.Delay(1000, cancellationToken);
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error checking HP warranty for serials: {Serials}", 
                string.Join(",", serialNumbers));
            result.FailedSerials.AddRange(serialNumbers);
        }
        
        result.ProcessingTime = DateTime.UtcNow - startTime;
        return result;
    }
}
```

## Services

### Dependency Injection Setup

```csharp
public static class ServiceCollectionExtensions
{
    public static IServiceCollection AddWarrantyCheck(this IServiceCollection services, IConfiguration configuration)
    {
        // Configuration
        services.Configure<AppSettings>(configuration);
        services.AddScoped<IConfigurationService, ConfigurationService>();
        
        // Core services
        services.AddScoped<IWarrantyService, WarrantyService>();
        services.AddScoped<IDuplicateDetectionService, DuplicateDetectionService>();
        services.AddScoped<IDeviceDiscoveryService, DeviceDiscoveryService>();
        
        // Device42 client
        services.AddHttpClient<IDevice42Client, Device42RestClient>();
        
        // Warranty providers
        services.AddScoped<IWarrantyProvider, CiscoWarrantyProvider>();
        services.AddScoped<IWarrantyProvider, DellWarrantyProvider>();
        services.AddScoped<IWarrantyProvider, HPWarrantyProvider>();
        services.AddScoped<IWarrantyProvider, IBMLenovoWarrantyProvider>();
        services.AddScoped<IWarrantyProvider, MerakiWarrantyProvider>();
        
        // HTTP resilience
        services.AddHttpClient<CiscoWarrantyProvider>()
            .AddPolicyHandler(GetRetryPolicy());
            
        return services;
    }

    private static IAsyncPolicy<HttpResponseMessage> GetRetryPolicy()
    {
        return HttpPolicyExtensions
            .HandleTransientHttpError()
            .OrResult(msg => msg.StatusCode == HttpStatusCode.TooManyRequests)
            .WaitAndRetryAsync(
                3,
                retryAttempt => TimeSpan.FromSeconds(Math.Pow(2, retryAttempt)));
    }
}
```

## Extensions

### String Extensions

```csharp
public static class StringExtensions
{
    public static string TruncateToLength(this string value, int maxLength);
    public static bool ContainsIgnoreCase(this string source, string value);
    public static string ToCleanSerialNumber(this string serialNumber);
    public static IEnumerable<string> SplitSerialNumbers(this string serialNumbers, char separator = ',');
    public static string GenerateRandomOrderNumber(this Random random, int length = 9);
}
```

### DateTime Extensions

```csharp
public static class DateTimeExtensions
{
    public static string ToDevice42DateString(this DateTime dateTime);
    public static string ToDevice42DateTimeString(this DateTime dateTime);
    public static DateTime FromUnixTimestamp(this long unixTimestamp);
    public static long ToUnixTimestamp(this DateTime dateTime);
    public static bool IsExpired(this DateTime endDate);
    public static bool IsActive(this DateTime endDate);
    public static TimeSpan GetRemainingTime(this DateTime endDate);
}
```

### Enumerable Extensions

```csharp
public static class EnumerableExtensions
{
    public static IEnumerable<IEnumerable<T>> Chunk<T>(this IEnumerable<T> source, int chunkSize);
    public static async Task<IEnumerable<TResult>> SelectAsync<TSource, TResult>(
        this IEnumerable<TSource> source, Func<TSource, Task<TResult>> selector);
    public static bool IsNullOrEmpty<T>(this IEnumerable<T>? source);
    public static IEnumerable<T> WhereNotNull<T>(this IEnumerable<T?> source) where T : class;
}
```

## Exceptions

### Exception Hierarchy

```csharp
public class WarrantyCheckException : Exception
{
    public string? VendorName { get; }
    public int? StatusCode { get; }
    
    // Multiple constructors for different scenarios
}

public class Device42Exception : WarrantyCheckException
{
    public Device42Exception(string message) : base(message, "Device42") { }
}

public class VendorApiException : WarrantyCheckException
{
    public VendorApiException(string message, string vendorName) : base(message, vendorName) { }
}

public class ConfigurationException : WarrantyCheckException
{
    public ConfigurationException(string message) : base(message) { }
}
```

## Usage Examples

### Basic Warranty Check

```csharp
// Setup dependency injection
var services = new ServiceCollection();
services.AddWarrantyCheck(configuration);
services.AddLogging();

var serviceProvider = services.BuildServiceProvider();

// Get the warranty service
var warrantyService = serviceProvider.GetRequiredService<IWarrantyService>();

// Run warranty check for all enabled vendors
var result = await warrantyService.RunWarrantyCheckAsync();

Console.WriteLine($"Processed: {result.UploadedCount} records");
Console.WriteLine($"Errors: {result.ErrorCount}");
```

### Vendor-Specific Check

```csharp
// Check warranty for specific vendor
var result = await warrantyService.RunWarrantyCheckForVendorAsync(
    "Cisco", 
    new[] { "ABC123", "DEF456", "GHI789" });

if (result.HasErrors)
{
    foreach (var error in result.ErrorMessages)
    {
        Console.WriteLine($"Error: {error}");
    }
}
```

### Custom Provider Implementation

```csharp
public class CustomWarrantyProvider : WarrantyProviderBase
{
    public override string VendorName => "CustomVendor";

    public override async Task<WarrantyResult> CheckWarrantyAsync(
        IEnumerable<string> serialNumbers, 
        bool retry = true,
        CancellationToken cancellationToken = default)
    {
        var result = new WarrantyResult { VendorName = VendorName };
        
        // Implement custom warranty check logic
        foreach (var serial in serialNumbers)
        {
            try
            {
                var warranty = await GetWarrantyInfoAsync(serial, cancellationToken);
                result.Warranties.Add(warranty);
                result.ProcessedSerials.Add(serial);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get warranty for {Serial}", serial);
                result.FailedSerials.Add(serial);
            }
        }
        
        return result;
    }

    private async Task<WarrantyInfo> GetWarrantyInfoAsync(string serial, CancellationToken cancellationToken)
    {
        // Custom implementation
        var response = await _httpClient.GetAsync($"warranty/{serial}", cancellationToken);
        response.EnsureSuccessStatusCode();
        
        // Parse response and return WarrantyInfo
        return new WarrantyInfo
        {
            SerialNumber = serial,
            VendorName = VendorName,
            // ... other properties
        };
    }
}
```

### Configuration Validation

```csharp
var configService = serviceProvider.GetRequiredService<IConfigurationService>();

if (!await configService.ValidateConfigurationAsync())
{
    Console.WriteLine("Configuration validation failed");
    return;
}

// Check specific vendor configuration
if (!await warrantyService.ValidateVendorConfigurationAsync("Cisco"))
{
    Console.WriteLine("Cisco configuration is invalid");
}
```

### Error Handling

```csharp
try
{
    var result = await warrantyService.RunWarrantyCheckAsync();
    
    if (result.HasErrors)
    {
        // Handle partial failures
        foreach (var error in result.ErrorMessages)
        {
            _logger.LogWarning("Warranty check warning: {Error}", error);
        }
    }
}
catch (WarrantyCheckException ex)
{
    _logger.LogError(ex, "Warranty check failed for vendor {Vendor}", ex.VendorName);
}
catch (Device42Exception ex)
{
    _logger.LogError(ex, "Device42 connection failed");
}
```

## Constants

### VendorConstants

```csharp
public static class VendorConstants
{
    public static class Vendors
    {
        public const string Cisco = "Cisco";
        public const string Dell = "Dell";
        public const string HP = "Hewlett Packard";
        public const string IBM = "IBM";
        public const string Lenovo = "LENOVO";
        public const string Meraki = "Meraki";
    }

    public static class ServiceLimits
    {
        public const int MaxServiceTypeLength = 64;
        public const int CiscoBatchLimit = 70;
        public const int DefaultBatchSize = 50;
        public const int DefaultRetryCount = 3;
        public const int DefaultTimeoutSeconds = 30;
    }
}
```

This documentation provides a comprehensive overview of the Warranty Check package API, including all interfaces, models, configuration options, and usage examples. The API is designed to be extensible, testable, and maintainable following modern C# .NET best practices.