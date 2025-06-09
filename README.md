# Warranty Check - C# Implementation

A modern C# .NET 9 implementation of the warranty check system for Device42.

Originally a <a href="https://biztactix.com.au">Biztactix</a> Fork from the Python version.

## About Device42
[Device42](http://www.device42.com) is a comprehensive data center inventory management and IP Address management software that integrates centralized password management, impact charts and applications mappings with IT asset management.

## Overview
This application automatically checks warranty status for Cisco, Dell, HP, IBM, Lenovo, and Meraki manufactured devices stored in Device42. The C# implementation provides improved performance, type safety, and modern .NET features compared to the original Python version.

## Prerequisites

### System Requirements
- .NET 9.0 or later
- Windows, Linux, or macOS

### Device42 Requirements
- Devices must have hardware model and serial number entered in Device42
- Hardware model manufacturer must contain: "Cisco", "Dell", "Hewlett Packard", "IBM", "LENOVO", or "Meraki"
- Serial numbers must be valid for the respective vendor

### Vendor API Credentials

#### OAuth 2.0 Vendors (Cisco, Dell)
- **Cisco**: Client ID and Client Secret from [Cisco API Console](https://apiconsole.cisco.com/documentation)
  - Follow onboarding: https://www.cisco.com/c/en/us/support/docs/services/sntc/onboarding_guide.html
- **Dell**: Client ID and Client Secret from TechDirect
  - Register at: http://en.community.dell.com/dell-groups/supportapisgroup/

#### API Key Vendors (HP, Meraki)
- **HP**: API Key from HP Developer Portal
  - Register at: https://developers.hp.com/css-enroll
- **Meraki**: API Key from Meraki Dashboard
  - Enable API access in Organization > Settings, then generate key in your profile
  - Details: https://developer.cisco.com/meraki/api/#/rest/getting-started/what-can-the-api-be-used-for

#### Web Scraping Vendors (IBM, Lenovo)
- No API credentials required (uses web scraping)

## Configuration

The application uses `appsettings.json` for configuration. Copy and modify the settings file:

```bash
cd src/src/WarrantyCheck.ConsoleApp
cp appsettings.json appsettings.Production.json
# Edit appsettings.Production.json with your settings
```

### Configuration Structure

```json
{
  "Device42": {
    "BaseUrl": "https://your-device42-instance.com",
    "Username": "your-username",
    "Password": "your-password"
  },
  "Discovery": {
    "Cisco": true,
    "Dell": true,
    "HP": false,
    "IBM": false,
    "Lenovo": false,
    "Meraki": false,
    "ForceUpdate": false
  },
  "Vendors": {
    "Cisco": {
      "Enabled": true,
      "Url": "https://api.cisco.com/sn2info/v2/coverage/summary/serial_numbers",
      "ClientId": "your-client-id",
      "ClientSecret": "your-client-secret"
    }
  }
}
```

## Installation & Usage

### Building from Source

```bash
# Clone the repository
git clone git@github.com:Biztactix/warranty_check.git
cd warranty_check

# Build the solution
dotnet build

# Run the application
cd src/src/WarrantyCheck.ConsoleApp
dotnet run
```

### Cross-Platform Support
- **Windows**: Native .NET 9 support
- **Linux**: Works on all major distributions with .NET 9
- **macOS**: Full compatibility with .NET 9

## Architecture

The C# implementation follows clean architecture principles:

- **WarrantyCheck.Core**: Domain models and abstractions
- **WarrantyCheck.Infrastructure**: External dependencies (HTTP, configuration)
- **WarrantyCheck.Providers**: Vendor-specific warranty implementations
- **WarrantyCheck.Application**: Business logic and orchestration
- **WarrantyCheck.ConsoleApp**: Entry point with dependency injection

## Key Features

- ✅ **Async/Await**: Non-blocking operations throughout
- ✅ **Dependency Injection**: Microsoft.Extensions.DependencyInjection
- ✅ **Structured Logging**: Microsoft.Extensions.Logging
- ✅ **Resilience**: Polly for retry policies and circuit breakers
- ✅ **Type Safety**: Strong typing with nullable reference types
- ✅ **Configuration**: Strongly-typed settings with validation
- ✅ **Cross-Platform**: Runs on Windows, Linux, and macOS

## Known Limitations

- If hardware model or serial number is missing, warranty status won't be checked
- IBM/Lenovo implementations rely on web scraping and may be fragile
- Meraki products with renewal-required licenses set expiration to current date

## Roadmap

- [ ] Device42 REST client implementation
- [ ] Vendor warranty provider implementations
- [ ] Lifecycle event integration for purchase dates
- [ ] Web API for on-demand warranty checks
- [ ] Docker containerization
- [ ] Azure Function deployment option

## Migration from Python

This C# implementation is a complete rewrite of the original Python version with:
- Modern async patterns replacing synchronous requests
- Strong typing instead of dynamic dictionaries  
- Dependency injection instead of global variables
- Structured logging instead of print statements
- Clean architecture instead of monolithic scripts

See `PYTHON_TO_CSHARP_MAPPING.md` for detailed migration guidance.

## Updates

**2025**: Complete C# .NET 9 rewrite with modern architecture and cross-platform support  
**2019**: Updated Dell warranty sync to use version 5 of their API (OAuth2.0)