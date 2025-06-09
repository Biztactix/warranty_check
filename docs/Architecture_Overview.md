# Warranty Check - Architecture Overview

## System Architecture

The Warranty Check application follows **Clean Architecture** principles with clear separation of concerns across multiple layers.

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         WarrantyCheck.ConsoleApp                    │   │
│  │  • Program.cs (Entry Point)                        │   │
│  │  • Dependency Injection Setup                      │   │
│  │  • Configuration Management                        │   │
│  │  • Command Line Interface                          │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Application Layer                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │        WarrantyCheck.Application                    │   │
│  │  • WarrantyService (Orchestration)                 │   │
│  │  • DeviceDiscoveryService                          │   │
│  │  • DuplicateDetectionService                       │   │
│  │  • Business Logic & Workflows                      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Infrastructure Layer                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │       WarrantyCheck.Infrastructure                  │   │
│  │  • Device42RestClient                              │   │
│  │  • ConfigurationService                            │   │
│  │  • HTTP Clients & Resilience                      │   │
│  │  • External Dependencies                           │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Providers Layer                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         WarrantyCheck.Providers                     │   │
│  │  • CiscoWarrantyProvider                           │   │
│  │  • DellWarrantyProvider                            │   │
│  │  • HPWarrantyProvider                              │   │
│  │  • IBMLenovoWarrantyProvider                       │   │
│  │  • MerakiWarrantyProvider                          │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Domain Layer                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           WarrantyCheck.Core                        │   │
│  │  • Domain Models                                   │   │
│  │  • Abstractions & Interfaces                       │   │
│  │  • Business Rules & Constants                      │   │
│  │  • Extensions & Utilities                          │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Layer Responsibilities

### Domain Layer (WarrantyCheck.Core)
- **Pure business logic** with no external dependencies
- **Domain models**: Device, WarrantyInfo, PurchaseRecord
- **Abstractions**: Interfaces for all services and providers
- **Business rules**: Constants, validation rules, business logic
- **Extensions**: Helper methods and utilities

### Providers Layer (WarrantyCheck.Providers)
- **Vendor-specific implementations** of warranty APIs
- **Protocol handling**: OAuth 2.0, API keys, web scraping
- **Data transformation**: Convert vendor responses to domain models
- **Error handling**: Vendor-specific error scenarios

### Infrastructure Layer (WarrantyCheck.Infrastructure)
- **External system integration**: Device42 REST API
- **Cross-cutting concerns**: Logging, configuration, HTTP clients
- **Technical implementations**: Caching, retry policies, circuit breakers
- **Framework dependencies**: Microsoft.Extensions.*, Polly

### Application Layer (WarrantyCheck.Application)
- **Use case orchestration**: Coordinate multiple providers and services
- **Business workflows**: Device discovery → Warranty checking → Data upload
- **Application services**: Higher-level business operations
- **Data flow coordination**: Between layers and external systems

### Presentation Layer (WarrantyCheck.ConsoleApp)
- **User interface**: Command-line interface
- **Dependency injection**: Service registration and container setup
- **Configuration**: appsettings.json management
- **Entry point**: Application startup and shutdown

## Data Flow

```
[Device42] ←→ [Device Discovery] → [Serial Extraction]
                                           │
                                           ▼
[Warranty APIs] ←→ [Warranty Providers] → [Warranty Collection]
                                           │
                                           ▼
[Duplicate Detection] → [Data Processing] → [Upload to Device42]
```

### Detailed Flow

1. **Configuration Loading**
   - Load appsettings.json
   - Validate vendor configurations
   - Set up dependency injection

2. **Device Discovery**
   - Query Device42 for hardware models by vendor
   - Retrieve devices in batches (pagination)
   - Extract serial numbers for warranty checking

3. **Warranty Checking** (per vendor)
   - Authenticate with vendor API (OAuth/API key)
   - Batch serial numbers according to vendor limits
   - Call vendor warranty APIs
   - Parse and normalize responses

4. **Data Processing**
   - Check for duplicate warranties
   - Transform to Device42 purchase record format
   - Apply business rules and validation

5. **Data Upload**
   - Upload new purchase records to Device42
   - Handle upload errors and retries
   - Log results and metrics

## Design Patterns

### Dependency Injection
- **Constructor injection** throughout the application
- **Service lifetimes**: Scoped for request-based services
- **Interface segregation**: Small, focused interfaces

### Repository Pattern
- `IDevice42Client` abstracts Device42 API operations
- Consistent interface for data access operations
- Testable with mock implementations

### Strategy Pattern
- `IWarrantyProvider` implementations for each vendor
- Runtime vendor selection based on configuration
- Extensible for new vendors

### Factory Pattern
- Service provider resolution for warranty providers
- Dynamic provider instantiation
- Configuration-driven provider selection

### Template Method Pattern
- `WarrantyProviderBase` with common functionality
- Vendor-specific implementations override abstract methods
- Shared error handling and logging

### Circuit Breaker Pattern
- Polly integration for resilience
- Prevents cascading failures
- Automatic recovery mechanisms

## Key Design Decisions

### Asynchronous Programming
- **Async/await** throughout the application
- **CancellationToken** support for operation cancellation
- **ConfigureAwait(false)** for library code

### Configuration Management
- **Strongly-typed** configuration classes
- **IOptions pattern** for configuration binding
- **Environment-specific** settings support

### Error Handling
- **Custom exception hierarchy** with vendor context
- **Structured logging** with correlation IDs
- **Graceful degradation** when vendors fail

### HTTP Client Management
- **HttpClientFactory** for connection pooling
- **Polly** for retry policies and resilience
- **Authentication handlers** for OAuth 2.0

### Testing Strategy
- **Unit tests** for business logic
- **Integration tests** for external APIs
- **Mock implementations** for dependencies
- **Test fixtures** for data setup

## Scalability Considerations

### Horizontal Scaling
- **Stateless design** enables multiple instances
- **Database-driven** coordination for distributed processing
- **Message queues** for async processing (future)

### Performance Optimization
- **Parallel processing** of multiple vendors
- **Batch API calls** to minimize network overhead
- **Connection pooling** for HTTP clients
- **Caching** of frequently accessed data

### Resource Management
- **Proper disposal** of HTTP clients and resources
- **Memory-efficient** streaming for large datasets
- **Configurable timeouts** and limits

## Security Considerations

### Credential Management
- **No hardcoded secrets** in source code
- **Azure Key Vault** integration (configurable)
- **Environment variables** for deployment

### Network Security
- **TLS/SSL** validation for all HTTP calls
- **Certificate pinning** for critical APIs
- **Request/response** logging (without sensitive data)

### Input Validation
- **Serial number** format validation
- **Configuration** parameter validation
- **API response** schema validation

## Monitoring and Observability

### Logging
- **Structured logging** with consistent format
- **Correlation IDs** for request tracing
- **Performance metrics** for API calls

### Health Checks
- **Vendor API** connectivity checks
- **Device42** connectivity validation
- **Configuration** validation status

### Metrics
- **Success/failure rates** per vendor
- **Processing times** and throughput
- **Error rates** and types

## Extension Points

### New Vendor Integration
1. Implement `IWarrantyProvider` interface
2. Add vendor configuration to `VendorConfig`
3. Register in dependency injection container
4. Add vendor-specific constants

### Custom Authentication
1. Implement custom `DelegatingHandler`
2. Register with `HttpClientFactory`
3. Configure for specific vendors

### Additional Data Sources
1. Implement new client interfaces
2. Add to infrastructure layer
3. Integrate in application services

### Alternative Outputs
1. Implement new upload interfaces
2. Add output format providers
3. Configure in application settings

This architecture provides a solid foundation for maintainable, testable, and extensible warranty checking functionality while following modern .NET development practices.