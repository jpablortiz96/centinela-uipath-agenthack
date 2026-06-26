# UiPath Product Feedback

This document captures integration feedback and product friction points discovered while building and connecting the CENTINELA Runtime API to UiPath Maestro Case.

## 1. Maestro API Workflow Publish Issue
- **Issue**: Attempting to publish a Maestro Case that relies on a connected API Workflow project fails in UiPath Labs.
- **Error**: `No solution tool factory is registered`
- **Impact**: We could not demonstrate a fully connected solution bundle natively through the API Workflow pattern as originally intended.

## 2. Custom Connector Packaging Issue
- **Issue**: Attempting to export/package the solution with a custom Connector Activity fails.
- **Errors**: `Failed to download custom-hackathon26868-centinelaruntimeapi_1.1.0.connector` / `elements unknown`
- **Impact**: It prevents packaging the solution as a single deployable asset.

## 3. Connector Activity Body Serialization
- **Issue**: When using the Integration Service Connector Activity inside Maestro, setting the JSON body for a POST request fails at runtime.
- **Error**: `Integration Services bad request - Could not serialize the following field(s): body`
- **Impact**: Required us to create a workaround by converting our POST endpoint to a GET endpoint (`/uipath/maestro-investigation-default`) that requires no request body.

## 4. Why This Matters for Enterprise Teams
Enterprise teams building Maestro Cases will often need to connect to proprietary internal systems (like core banking APIs). They will encounter these serialization and packaging errors, blocking their CI/CD pipelines and deployment strategies.

## 5. Suggested Improvements
- **Clearer Diagnostics**: Provide actionable error messages rather than "elements unknown".
- **Validation Before Publish**: Validate the solution structure (tool factories, connectors) *before* attempting the cloud build to save time.
- **Connector Export Readiness Check**: Allow developers to explicitly test if their custom connector is valid for solution packaging.
