using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using WarrantyCheck.Core.Abstractions;
using WarrantyCheck.Core.Models;
using WarrantyCheck.Infrastructure.Configuration;

namespace WarrantyCheck.ConsoleApp;

class Program
{
    static async Task<int> Main(string[] args)
    {
        try
        {
            var host = CreateHostBuilder(args).Build();
            
            var logger = host.Services.GetRequiredService<ILogger<Program>>();
            logger.LogInformation("Warranty Check application starting...");

            // Test configuration loading
            var configService = host.Services.GetRequiredService<IConfigurationService>();
            var isValid = await configService.ValidateConfigurationAsync();
            
            if (!isValid)
            {
                logger.LogError("Configuration validation failed. Please check your settings.");
                return 1;
            }

            logger.LogInformation("Configuration validation successful");
            logger.LogInformation("Warranty Check application ready");

            // TODO: Implement actual warranty check logic here
            
            return 0;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"An error occurred: {ex.Message}");
            return 1;
        }
    }

    static IHostBuilder CreateHostBuilder(string[] args) =>
        Host.CreateDefaultBuilder(args)
            .ConfigureAppConfiguration((context, config) =>
            {
                config.AddJsonFile("appsettings.json", optional: false, reloadOnChange: true);
                config.AddJsonFile($"appsettings.{context.HostingEnvironment.EnvironmentName}.json", 
                    optional: true, reloadOnChange: true);
                config.AddEnvironmentVariables();
                config.AddCommandLine(args);
            })
            .ConfigureServices((context, services) =>
            {
                // Configure strongly typed settings
                services.Configure<AppSettings>(context.Configuration);
                
                // Register services
                services.AddScoped<IConfigurationService, ConfigurationService>();
                
                // Configure logging
                services.AddLogging(builder =>
                {
                    builder.AddConsole();
                    builder.AddDebug();
                });
                
                // Configure HttpClient
                services.AddHttpClient();
            })
            .UseConsoleLifetime();
}
