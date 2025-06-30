# Documentation Images

This directory contains images for the Kong Auth Service documentation.

## Required Images

The following images are referenced in the documentation:

### Architecture Images
- `architecture-overview.png` - Main system architecture diagram
- `building-analogy.png` - Building security analogy diagram
- `data-flow.png` - Data flow between components
- `security-layers.png` - Security layers diagram
- `scalability.png` - Scalability architecture diagram

### Component Images
- `kong-gateway-overview.png` - Kong Gateway overview
- `kong-gateway-detail.png` - Kong Gateway detailed view
- `kong-admin-detail.png` - Kong Admin API details
- `auth-service-detail.png` - Auth Service details
- `sample-service-detail.png` - Sample Service details
- `jwt-token-detail.png` - JWT Token details
- `plugins-detail.png` - Plugins details

### JWT Authentication Images
- `jwt-structure.png` - JWT token structure
- `jwt-flow.png` - JWT authentication flow

### Kong Gateway Images
- `kong-architecture.png` - Kong architecture
- `jwt-plugin-flow.png` - JWT plugin flow
- `cors-plugin-flow.png` - CORS plugin flow
- `plugin-interaction.png` - Plugin interaction

### Quick Start Images
- `quick-start-flow.png` - Quick start flow diagram

## Image Requirements

- **Format**: PNG or SVG preferred
- **Size**: Optimized for web (max 800px width)
- **Style**: Consistent with documentation theme
- **Accessibility**: Include alt text in documentation

## Placeholder Images

Until actual images are created, you can use placeholder images or remove the image references from the RST files.

To remove image references temporarily, comment out the image lines in the RST files:

```rst
.. image:: ../_static/images/architecture-overview.png
   :alt: System Architecture
   :align: center
```

Comment out like this:

```rst
.. image:: ../_static/images/architecture-overview.png
   :alt: System Architecture
   :align: center
``` 