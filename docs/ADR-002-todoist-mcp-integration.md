# ADR-002: Todoist Integration via MCP Server Instead of Direct API Integration

## Status
Accepted

## Context

The Daily Briefer application is a crew.ai-based system that generates comprehensive daily briefing documents by synthesizing data from multiple sources including Gmail, Google Calendar, and Todoist. The system needs to integrate with Todoist to retrieve tasks that are due or overdue for a specific date to include in the "Action Items" section of daily briefings.

### Integration Requirements:
- **Task Retrieval**: Get tasks due on a specific date with optional overdue filtering
- **Date Filtering**: Support filtering by due dates and project organization
- **Error Handling**: Robust handling of API failures and status reporting
- **Performance**: Minimal latency for daily briefing generation workflow
- **Configuration**: Simple setup and credential management

### Technical Context:
- **Framework**: Built using crew.ai with multiple specialized agents
- **Architecture**: Agent-based system with dedicated Data Collector and Task Manager agents
- **Error Handling**: Comprehensive tool status tracking and graceful degradation
- **Environment**: Python 3.13+ with async/await support for external integrations

### Business Constraints:
- **Reliability**: Daily briefings must be generated consistently, even if Todoist is temporarily unavailable
- **Maintenance**: Integration should be easy to maintain and update
- **Team Skills**: Development team has experience with crew.ai patterns and MCP protocol
- **Ecosystem Fit**: Should align with existing Google services integration patterns

## Decision

Implement Todoist integration using the Model Context Protocol (MCP) server (@modelcontextprotocol/server-todoist) instead of direct Todoist API integration through the TodoistTool class.

### Implementation Details:
- **MCP Server**: Use @modelcontextprotocol/server-todoist npm package
- **Communication**: Stdio-based MCP client connection
- **Configuration**: Environment variables (TODOIST_API_TOKEN, optional TODOIST_MCP_SERVER_URL)
- **Tool Integration**: Custom TodoistTool extending crew.ai BaseTool with MCP client
- **Error Handling**: Comprehensive status tracking and fallback mechanisms

### Rationale:
1. **Standardized Protocol**: MCP provides a well-defined, standardized interface for external service integration
2. **Separation of Concerns**: MCP server handles Todoist API specifics, while the application focuses on business logic
3. **Framework Alignment**: Aligns with crew.ai's recommended patterns for external tool integration
4. **Future Scalability**: Establishes pattern for additional MCP-based integrations (Gmail, Calendar could follow)
5. **Maintenance Isolation**: Updates to Todoist API are handled at the MCP server level, not application level

## Alternatives Considered

### Option 1: Direct Todoist API Integration
- **Description**: Use Todoist's REST API directly with Python requests/httpx
- **Pros**: 
  - Simpler initial setup (no external server required)
  - Direct control over API calls and error handling
  - Lower architectural complexity
  - Familiar HTTP/REST patterns
- **Cons**: 
  - Tight coupling between application and Todoist API changes
  - Manual handling of authentication, rate limiting, and retries
  - Inconsistent with other external integrations
  - Requires maintaining API client code in application
- **Risk Level**: Medium

### Option 2: MCP Server Integration (Recommended)
- **Description**: Use @modelcontextprotocol/server-todoist via MCP protocol
- **Pros**:
  - Standardized interface consistent across all external services
  - Separation of concerns between business logic and API integration
  - Built-in error handling and status reporting
  - Future-proof for additional MCP-based tools
  - Aligns with crew.ai ecosystem patterns
  - Simplified credential management
- **Cons**:
  - Additional dependency (Node.js MCP server)
  - Slightly higher initial complexity
  - Dependency on MCP server availability
  - Less direct control over API interaction patterns
- **Risk Level**: Low

### Option 3: Third-Party Python Todoist Library
- **Description**: Use existing Python libraries like todoist-python or pytodoist
- **Pros**:
  - Existing Python ecosystem integration
  - Maintained by community
  - No additional runtime dependencies
- **Cons**:
  - Variable maintenance quality and update frequency
  - Inconsistent with MCP-based architecture
  - Potential abandonment or compatibility issues
  - Still requires manual integration with crew.ai patterns
- **Risk Level**: Medium-High

### Option 4: Custom Wrapper Service
- **Description**: Build custom microservice to abstract Todoist API
- **Pros**:
  - Full control over interface and caching
  - Could serve multiple applications
  - Custom optimization opportunities
- **Cons**:
  - Significant development and maintenance overhead
  - Additional infrastructure requirements
  - Over-engineering for current needs
  - Deployment and monitoring complexity
- **Risk Level**: High

### Option 5: Webhook-Based Integration
- **Description**: Use Todoist webhooks for real-time task updates
- **Pros**:
  - Real-time updates without polling
  - Reduced API call volume
  - Event-driven architecture
- **Cons**:
  - Requires persistent server and webhook handling
  - Complex setup and infrastructure
  - Not suitable for on-demand briefing generation
  - Over-engineered for batch processing use case
- **Risk Level**: High

## Consequences

### Positive
- **Architectural Consistency**: Establishes standardized pattern for external service integration across the Daily Briefer system
- **Maintainability**: Todoist API changes are handled at the MCP server level, reducing application maintenance burden
- **Error Resilience**: Built-in status tracking and error handling through ToolStatus integration
- **Development Velocity**: Simplified integration reduces time to add additional external services
- **Framework Alignment**: Follows crew.ai best practices for tool integration patterns
- **Credential Security**: Centralized environment variable management with secure token handling
- **Future Scalability**: Foundation for expanding to additional MCP-based integrations (calendar, email, etc.)

### Negative
- **External Dependency**: Requires Node.js and npm for MCP server installation and management
- **Runtime Complexity**: Additional process management for MCP server lifecycle
- **Debugging Complexity**: Errors may occur at multiple layers (application → MCP client → MCP server → Todoist API)
- **Documentation Overhead**: Team must understand both application code and MCP server configuration
- **Version Management**: Must coordinate updates between application, MCP client library, and MCP server

### Neutral
- **Performance**: Expected similar performance to direct API integration due to local MCP server communication
- **Configuration Complexity**: Similar environment variable management to direct API approach
- **Learning Curve**: MCP protocol concepts required, but consistent with existing crew.ai patterns

## Implementation Notes

### Setup Requirements
1. **MCP Server Installation**:
   ```bash
   npm install -g @modelcontextprotocol/server-todoist
   ```

2. **Environment Configuration**:
   ```bash
   # Required
   TODOIST_API_TOKEN=your_todoist_api_token
   
   # Optional (defaults to stdio://npx -y @modelcontextprotocol/server-todoist)
   TODOIST_MCP_SERVER_URL=stdio://npx -y @modelcontextprotocol/server-todoist
   ```

### Key Implementation Components

#### TodoistTool Class Structure
```python
class TodoistTool(BaseTool):
    """Tool for interacting with Todoist via MCP server."""
    
    # MCP client initialization with error handling
    # Async task retrieval with date filtering
    # Comprehensive status tracking via ToolStatus
    # Graceful degradation on failures
```

#### Error Handling Strategy
- **Connection Failures**: Tool reports unavailable status, briefing continues without Todoist data
- **Authentication Issues**: Clear error messages for missing or invalid TODOIST_API_TOKEN
- **MCP Server Issues**: Fallback to empty task list with status warnings
- **Data Parsing Errors**: Individual task failures don't break entire operation

#### Integration Points
- **Data Collector Agent**: Uses TodoistTool to gather task data during briefing generation
- **Task Manager Agent**: Processes retrieved Todoist tasks and generates suggestions
- **Document Synthesizer**: Formats Todoist tasks in "Action Items" section

### Migration Strategy
This is a new integration (no existing Todoist integration to migrate from), so implementation follows greenfield patterns:

1. **Phase 1**: Core TodoistTool implementation with basic task retrieval
2. **Phase 2**: Integration with Data Collector and Task Manager agents
3. **Phase 3**: Comprehensive error handling and status reporting
4. **Phase 4**: Documentation and operational procedures

### Success Metrics
- **Integration Reliability**: >95% successful task retrieval during daily briefing generation
- **Error Handling**: Graceful degradation when Todoist or MCP server unavailable
- **Performance**: Task retrieval completes within 2 seconds for typical workloads
- **Developer Experience**: Clear setup documentation and error messages for troubleshooting
- **Maintainability**: Zero application code changes required for Todoist API updates

### Monitoring and Observability
- **ToolStatus Integration**: Real-time status reporting for Todoist MCP connection
- **Error Logging**: Comprehensive logging for MCP client connection and API call failures
- **Health Checks**: Regular validation of MCP server availability and authentication
- **Performance Metrics**: Latency tracking for task retrieval operations

### Rollback Plan
Since this is a new integration, rollback involves:
- **Graceful Degradation**: Daily briefings continue without Todoist data if integration fails
- **Feature Toggle**: Environment variable to disable Todoist integration if needed
- **Status Reporting**: Clear indication in briefing when Todoist data unavailable
- **Alternative Data Sources**: Task suggestions still generated from email and calendar analysis

## References
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [@modelcontextprotocol/server-todoist Documentation](https://github.com/modelcontextprotocol/servers/tree/main/src/todoist)
- [crew.ai Tool Integration Guide](https://docs.crewai.com/concepts/tools)
- [Daily Briefer System Architecture - docs/daily-briefer.md](./daily-briefer.md)
- [Todoist REST API Documentation](https://developer.todoist.com/rest/v2/)
- [Python MCP Client Library](https://github.com/modelcontextprotocol/python-sdk)

---

**Document Metadata:**
- Created: 2025-09-11
- Author: Architecture Team  
- Related ADRs: ADR-001 (Gemini LLM Migration)
- Next Review: 2025-12-11 (Quarterly Review)
- Implementation Status: Completed