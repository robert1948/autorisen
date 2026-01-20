<?xml version="1.0" encoding="UTF-8"?>
<map version="1.0.1">
  <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="CapeControl Agents System v0.2.2">
    <node CREATED="1699747200000" MODIFIED="1699747200000" POSITION="right" TEXT="Changelog v0.2.2">
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Resolve versioning canon (auto-increment ordering + optional semver display)"/>
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Archived restorability explicit (owner/admin restore + audit)"/>
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Public detail view restricted to published versions + manifest redaction"/>
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Installation &amp; Entitlements placeholders"/>
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Agent Runtime Telemetry placeholders (runs/steps/metrics/logs)"/>
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Guided Discovery (breadcrumbs) aligned to Curiosity Cascade"/>
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Naming normalized: ChatKit Runtime"/>
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Roles made explicit (public/owner/developer/admin/org_admin optional)"/>
    </node>
    <node CREATED="1699747200000" MODIFIED="1699747200000" POSITION="right" TEXT="Agent Registry API">
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="CRUD Operations">
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="List Agents">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="GET /agents"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Filter by owner"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Paginated results"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Auth required"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Create Agent">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="POST /agents"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Auto-generate slug"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Set owner_id from token"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Validate manifest"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Update Agent">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="PUT /agents/{agent_id}"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Owner permission check"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Partial updates allowed"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Delete Agent">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="DELETE /agents/{agent_id}"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Owner permission check"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Cascade delete versions"/>
        </node>
      </node>
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Version Management">
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Create Version">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="POST /agents/{agent_id}/versions"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Auto-increment version"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Draft status by default"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Validate manifest schema"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Publish Version">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="POST /agents/{agent_id}/versions/{version_id}/publish"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Set published_at timestamp"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Make available in marketplace"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Validate manifest completeness"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Archive Version">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="POST /agents/{agent_id}/versions/{version_id}/archive"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Remove from marketplace"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Keep for historical reference"/>
        </node>
      </node>
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Authentication Integration">
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="JWT Token Validation"/>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="get_current_user dependency"/>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Owner-based permissions"/>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Role-based access control"/>
      </node>
    </node>
    <node CREATED="1699747200000" MODIFIED="1699747200000" POSITION="right" TEXT="Marketplace System">
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Public Discovery">
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="List Published Agents">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="GET /marketplace/agents"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Only published versions"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Sorted by updated_at desc"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Include manifest data"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Agent Detail View">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="GET /marketplace/agents/{slug}"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Public: show published versions only"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Owner/Admin: show all versions (draft/published/archived)"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Highlight published version"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Version history (public) excludes drafts/archived"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Manifest Redaction (Public)">
            <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Redact secrets"/>
            <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Redact endpoints/keys"/>
            <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Redact tool config defaults as needed"/>
            <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Expose safe subset (name/description/category/high-level tools list)"/>
          </node>
        </node>
      </node>
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Agent Metadata">
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Basic Info">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Name &amp; description"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Slug for URL routing"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Owner information"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Creation/update timestamps"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Version Info">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Semantic version number"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Status (draft/published/archived)"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Publication timestamp"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Complete manifest data"/>
        </node>
      </node>
    </node>
    <node CREATED="1699747200000" MODIFIED="1699747200000" POSITION="right" TEXT="Schema Validation">
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Agent Schemas">
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="AgentBase">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="name: required string"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="description: required string"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="manifest: required dict"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="slug: auto-generated"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="AgentCreate">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Inherits from AgentBase"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Validates manifest structure"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Generates slug from name"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="AgentUpdate">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="All fields optional"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Partial update support"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Manifest validation if provided"/>
        </node>
      </node>
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Version Schemas">
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="AgentVersionBase">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="manifest: required dict"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="version_int: auto-increment (canonical ordering)"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="version_semver: optional string (Major.Minor.Patch) (display only)"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="status: enum validation"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="AgentVersionCreate">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Inherits from AgentVersionBase"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Validates complete manifest"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Routing &amp; Safety Notes">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Marketplace routing uses agent slug + published version_id"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Never trust client-supplied version numbers"/>
        </node>
      </node>
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Manifest Validation">
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Required Fields">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="name: Agent display name"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="description: Agent purpose"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="placement: UI placement hint"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="tools: Available tool list"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Optional Fields">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="category: Agent classification"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="config: Runtime configuration"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="permissions: Access requirements"/>
        </node>
      </node>
    </node>
    <node CREATED="1699747200000" MODIFIED="1699747200000" POSITION="right" TEXT="Agent Types &amp; Categories">
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Core System Agents">
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="AuthAgent">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Registration &amp; login"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="JWT token management"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Role-based access"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Profile management"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="AuditAgent">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Request logging"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Event tracking"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Middleware cooperation"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="MonitoringAgent">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Health checks"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="System metrics"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Performance monitoring"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="SecurityAgent">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Rate limiting"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Input validation"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Abuse prevention"/>
        </node>
      </node>
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="AI-Assisted Agents">
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="CapeAI Guide Agent">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="In-app guidance"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Onboarding assistance"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Feature discovery"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="DevAgent">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Agent development assistance"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Build &amp; test automation"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Publishing workflow"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="CustomerAgent">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Goal interpretation"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Workflow suggestions"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Process optimization"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="ChatKit Runtime">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Multi-step workflows"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="ChatKit integration"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Conversational flows"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Alias: formerly ChatAgentKit Runtime"/>
        </node>
      </node>
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Domain-Specific Agents">
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="FinanceAgent">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Financial data integration"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Budget tracking"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Payment processing"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="EnergyAgent">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Smart meter integration"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Usage analytics"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Energy optimization"/>
        </node>
      </node>
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Middleware-Bound Agents">
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Request Processing">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="DDoS Protection"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Input Sanitization"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Content Moderation"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Logging &amp; Monitoring">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Audit Logging Middleware"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Performance Monitoring"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Error Tracking"/>
        </node>
      </node>
    </node>
    <node CREATED="1699747200000" MODIFIED="1699747200000" POSITION="left" TEXT="Database Models">
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Agent Model">
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Core Fields">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="id: Primary key"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="name: Display name"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="slug: URL-safe identifier"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="description: Agent purpose"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Ownership &amp; Timestamps">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="owner_id: Foreign key to User"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="created_at: Creation timestamp"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="updated_at: Last modification"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Relationships">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="versions: One-to-many AgentVersion"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="owner: Many-to-one User"/>
        </node>
      </node>
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="AgentVersion Model">
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Version Fields">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="id: Primary key"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="version_int: auto-increment (canonical ordering)"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="version_semver: optional string (Major.Minor.Patch) (display only)"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="manifest: JSON configuration"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="status: Lifecycle state"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Timestamps">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="created_at: Version creation"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="published_at: Publication date"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Relationships">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="agent_id: Foreign key to Agent"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="agent: Many-to-one Agent"/>
        </node>
      </node>
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Status Lifecycle">
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Draft">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Initial state"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Work in progress"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Not publicly visible"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Published">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Available in marketplace"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Set published_at timestamp"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Manifest must be complete"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Archived">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Removed from marketplace"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Historical reference"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Not discoverable/installable"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Restorable by owner/admin"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Restore action must be audit logged"/>
        </node>
      </node>
    </node>
    <node CREATED="1699747200000" MODIFIED="1699747200000" POSITION="left" TEXT="Developer Workflow">
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Agent Creation Flow">
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="1. Design Agent">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Define purpose &amp; scope"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Identify required tools"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Plan user interactions"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="2. Create Agent Record">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="POST /agents with basic info"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="System generates slug"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Agent in draft state"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="3. Develop &amp; Test">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Implement agent logic"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Create manifest configuration"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Test in development environment"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="4. Create Version">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="POST /agents/{id}/versions"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Upload complete manifest"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Version starts as draft"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="5. Publish to Marketplace">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="POST /agents/{id}/versions/{version_id}/publish"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Validate manifest completeness"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Make publicly discoverable"/>
        </node>
      </node>
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Version Management">
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Semantic Versioning">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Auto-increment version numbers"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Major.Minor.Patch format"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Breaking change indicators"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Version States">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Draft: Under development"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Published: Live in marketplace"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Archived: Removed from marketplace"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Publication Requirements">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Complete manifest validation"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Required fields present"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Tools list validated"/>
        </node>
      </node>
    </node>
    <node CREATED="1699747200000" MODIFIED="1699747200000" POSITION="left" TEXT="User Experience Flow">
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Marketplace Discovery">
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Browse Published Agents">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="List view with metadata"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Search and filter options"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Category-based organization"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Guided Discovery (Breadcrumbs)">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Start with a problem statement"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Reveal 3 suggested agents"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Show outcomes before mechanics"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Progressive disclosure into install"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Agent Detail View">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Complete agent information"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Version history display"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Manifest details preview"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Installation instructions"/>
        </node>
      </node>
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Agent Installation">
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="One-Click Install">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Download manifest"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Validate compatibility"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Configure permissions"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Configuration Setup">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Required parameter input"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Optional customization"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Permission grants"/>
        </node>
      </node>
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Agent Usage">
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Integration Points">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Chat interface integration"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Dashboard widget placement"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Workflow automation hooks"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="User Interaction">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Natural language commands"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Guided task completion"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Proactive assistance"/>
        </node>
      </node>
    </node>
    <node CREATED="1699747200000" MODIFIED="1699747200000" POSITION="left" TEXT="Security &amp; Permissions">
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Access Control">
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Roles (Canonical)">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="public"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="owner"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="developer"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="admin"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="org_admin (optional)"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Owner Permissions">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Create agents"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Update own agents"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Delete own agents"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Manage versions"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Public Permissions">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Browse marketplace"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="View published agents"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Install agents"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Admin Permissions">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Moderate marketplace"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Review agent submissions"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Remove violating content"/>
        </node>
      </node>
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Manifest Validation">
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Security Checks">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Tool permission validation"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Resource access limits"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Malicious code detection"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Content Moderation">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Inappropriate content filtering"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Spam prevention"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Quality standards enforcement"/>
        </node>
      </node>
    </node>

    <node CREATED="1699747200000" MODIFIED="1699747200000" POSITION="left" TEXT="Installation &amp; Entitlements">
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="AgentInstall model">
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="user_id"/>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="agent_id"/>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="version_id"/>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="installed_at"/>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="status"/>
      </node>
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Entitlement model">
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="free / paid / subscription / org"/>
      </node>
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Usage limits / quotas (placeholder)"/>
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Uninstall flow (placeholder)"/>
    </node>

    <node CREATED="1699747200000" MODIFIED="1699747200000" POSITION="left" TEXT="Agent Runtime Telemetry">
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="AgentRun model">
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="id"/>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="user_id"/>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="agent_id"/>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="version_id"/>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="started_at"/>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="ended_at"/>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="status"/>
      </node>
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="AgentRunStep">
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="step_index"/>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="tool"/>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="latency_ms"/>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="success"/>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="error"/>
      </node>
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Metrics">
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="success rate"/>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="latency"/>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="cost_units"/>
      </node>
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Logs/traces retention note (placeholder)"/>
    </node>
    <node CREATED="1699747200000" MODIFIED="1699747200000" POSITION="left" TEXT="Integration Architecture">
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Backend Integration">
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="FastAPI Router Module">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="/backend/src/modules/agents/router.py"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="RESTful API endpoints"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Pydantic schema validation"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Database Layer">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="SQLAlchemy models"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Alembic migrations"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Relationship management"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Authentication Layer">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="JWT token validation"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="User context injection"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Permission enforcement"/>
        </node>
      </node>
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Frontend Integration">
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="React Components">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Agent marketplace UI"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Agent management dashboard"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Version control interface"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="API Client">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="TypeScript API definitions"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="HTTP client configuration"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Error handling patterns"/>
        </node>
      </node>
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="External Integrations">
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="ChatKit Runtime">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Conversational workflow support"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Multi-step agent execution"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Context preservation"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Tool Registry">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Available tool enumeration"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Permission validation"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Capability discovery"/>
        </node>
      </node>
    </node>
    <node CREATED="1699747200000" MODIFIED="1699747200000" POSITION="right" TEXT="Future Roadmap">
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Enhanced Marketplace">
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Rating &amp; Review System">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="User ratings and feedback"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Quality metrics tracking"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Popular agents highlighting"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Monetization Support">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Paid agent marketplace"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Usage-based pricing"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Developer revenue sharing"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Advanced Discovery">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="AI-powered recommendations"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Contextual agent suggestions"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Workflow-based discovery"/>
        </node>
      </node>
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Development Tools">
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Agent Builder IDE">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Visual agent design interface"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Code generation assistance"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Testing &amp; debugging tools"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Deployment Automation">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="CI/CD pipeline integration"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Automated testing frameworks"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Performance monitoring"/>
        </node>
      </node>
      <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Enterprise Features">
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Private Marketplaces">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Organization-specific agents"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Private deployment options"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Enterprise security compliance"/>
        </node>
        <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Advanced Analytics">
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Usage analytics dashboard"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="Performance metrics tracking"/>
          <node CREATED="1699747200000" MODIFIED="1699747200000" TEXT="ROI measurement tools"/>
        </node>
      </node>
    </node>
  </node>
</map>