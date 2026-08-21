"""Reference data for the 4xData synthetic support ticket dataset.

Everything here is fixed vocabulary: connectors, the frozen pattern taxonomy,
customers, and the team. Ticket generation draws from these.
"""

# --- Connectors -------------------------------------------------------------
# Five heavy connectors carry 65% of tickets, ten light ones carry 35%.

HEAVY_CONNECTORS = ["PostgreSQL", "Salesforce", "Snowflake", "MongoDB", "Amazon S3"]
LIGHT_CONNECTORS = [
    "MySQL", "SQL Server", "Oracle", "BigQuery", "Redshift",
    "DynamoDB", "NetSuite", "HubSpot", "Kafka", "Google Sheets",
]
CONNECTORS = HEAVY_CONNECTORS + LIGHT_CONNECTORS

# --- Patterns ---------------------------------------------------------------
# Causes only. `root_cause_fix` describes the durable fix for that class of
# problem, which is what a developer proposes in the thread.

PATTERNS = [
    {
        "pattern_name": "Missing right permissions",
        "pattern_description": (
            "The role granted to the connector lacks a privilege it needs for a specific "
            "operation. The source usually reports this as a missing object or an empty "
            "result rather than as an authorization error, which sends the customer looking "
            "for a data problem instead of a grant."
        ),
        "root_cause_fix": (
            "Ship a preflight permission check that enumerates every grant the selected sync "
            "mode requires and names the exact missing privilege before the first sync runs."
        ),
    },
    {
        "pattern_name": "Asking broader permissions",
        "pattern_description": (
            "The documented setup asks for a privilege wider than the work requires. The "
            "customer's security review either rejects it outright or grants a narrowed "
            "version that then fails somewhere else."
        ),
        "root_cause_fix": (
            "Split the documented grant set by sync mode so each mode asks for the minimum it "
            "needs, and remove every account-wide blanket privilege from the setup guide."
        ),
    },
    {
        "pattern_name": "Private Link setup failed",
        "pattern_description": (
            "The private network path between the connector and the source is misconfigured on "
            "one side. Most often DNS resolution, an unapproved endpoint, or a security group "
            "rule that never allowed the connector's subnet."
        ),
        "root_cause_fix": (
            "Add a connectivity diagnostic that resolves the endpoint, opens a socket, and "
            "reports which hop failed, so the customer's network team gets an actionable line "
            "instead of a timeout."
        ),
    },
    {
        "pattern_name": "Connector not scalable",
        "pattern_description": (
            "The extraction strategy works at the volume the first customer had and degrades "
            "as the source grows. Unbounded memory use, single-threaded reads, or a full scan "
            "where an index exists."
        ),
        "root_cause_fix": (
            "Replace the whole-object read with a bounded, resumable strategy: partitioned "
            "parallel reads with a checkpoint committed per partition."
        ),
    },
    {
        "pattern_name": "Not in sync with source",
        "pattern_description": (
            "The connector's committed cursor or watermark diverges from the source's true "
            "state, so rows are missed or replayed. The destination drifts from the source "
            "while every sync continues to report success."
        ),
        "root_cause_fix": (
            "Make the cursor commit atomic with the write to the destination, and add a "
            "periodic row count and checksum comparison that raises drift as an error instead "
            "of leaving it silent."
        ),
    },
    {
        "pattern_name": "Edge case not handled",
        "pattern_description": (
            "A data shape, type or state the source permits was never handled in the "
            "extraction logic. The sync either fails on that row or writes it wrong."
        ),
        "root_cause_fix": (
            "Add the shape to the connector's conformance suite so every source type is tested "
            "against the full range the source permits, rather than the range the first "
            "customer happened to have."
        ),
    },
    {
        "pattern_name": "Source limitations",
        "pattern_description": (
            "The source system cannot do what the customer is asking for. A hard API limit, a "
            "missing capability, or a guarantee the source does not offer."
        ),
        "root_cause_fix": (
            "Document the limit on the connector's page alongside the workaround, and surface "
            "it in the UI at configuration time rather than at first failure."
        ),
    },
    {
        "pattern_name": "Is a feature request",
        "pattern_description": (
            "The connector behaves as designed. The customer is asking for capability that "
            "does not exist yet."
        ),
        "root_cause_fix": (
            "None. Route to the roadmap with the customer and account attached so the demand "
            "gets counted instead of closed."
        ),
    },
    {
        "pattern_name": "Lack of documentation",
        "pattern_description": (
            "The behaviour is correct and documented nowhere, or documented somewhere the "
            "customer did not find. The ticket is a question the docs should have answered."
        ),
        "root_cause_fix": (
            "Write the page, and link it from the error message or the setup step where the "
            "question arises."
        ),
    },
    {
        "pattern_name": "Schema drift unhandled",
        "pattern_description": (
            "A column was added, dropped or retyped at the source. The connector either failed "
            "the sync or carried on writing the old shape."
        ),
        "root_cause_fix": (
            "Read the schema at the head of every sync, compare it to the committed shape, and "
            "apply the customer's configured drift policy instead of assuming the shape holds."
        ),
    },
    {
        "pattern_name": "API rate limit exceeded",
        "pattern_description": (
            "The connector issued requests faster than the source allows and got throttled or "
            "rejected. Most often when several syncs for one customer overlap on the same "
            "source account."
        ),
        "root_cause_fix": (
            "Move rate limiting from per-sync to per-source-account, honour the retry-after "
            "header, and back off across every sync sharing that account."
        ),
    },
    {
        "pattern_name": "Credential expiry or rotation",
        "pattern_description": (
            "The stored credential expired or the customer rotated it. The connector kept "
            "using the old one until a sync failed."
        ),
        "root_cause_fix": (
            "Refresh ahead of expiry where the source supports it, and alert the customer "
            "before the credential lapses rather than after the sync breaks."
        ),
    },
    {
        "pattern_name": "CDC log retention exceeded",
        "pattern_description": (
            "The connector fell far enough behind that the source discarded the change log it "
            "needed. Change capture cannot resume without a full re-read."
        ),
        "root_cause_fix": (
            "Track lag against the source's retention window and warn the customer while there "
            "is still time to act, then resume from a snapshot automatically instead of failing."
        ),
    },
]

PATTERN_NAMES = [p["pattern_name"] for p in PATTERNS]

# Four heavy patterns carry 65% of tickets.
HEAVY_PATTERNS = [
    "Missing right permissions",
    "Edge case not handled",
    "Schema drift unhandled",
    "Private Link setup failed",
]

# Patterns that ship no code, so fix_type stays null.
NO_FIX_PATTERNS = {"Is a feature request", "Lack of documentation", "Source limitations"}

# Patterns that lean towards a quick patch rather than a durable fix.
PATCH_LEANING = {"Edge case not handled", "API rate limit exceeded", "Credential expiry or rotation"}

# --- Severity ---------------------------------------------------------------

SEVERITIES = ["low", "medium", "high", "critical"]
SEVERITY_WEIGHTS = [0.30, 0.40, 0.22, 0.08]

# Median hours to resolution per severity. Actual draws are lognormal around these.
SEVERITY_MEDIAN_HOURS = {"critical": 6, "high": 24, "medium": 72, "low": 216}

# --- Customers --------------------------------------------------------------
# 8 enterprise, 14 growth, 18 startup. Enterprise files disproportionately more.

TIER_WEIGHTS = {"enterprise": 3.0, "growth": 1.5, "startup": 1.0}
REGIONS = ["us-east", "us-west", "eu-west", "ap-south"]

ENTERPRISE_NAMES = [
    "Northwind Financial", "Bellweather Health", "Talos Logistics", "Kestrel Energy",
    "Alderpoint Insurance", "Grantham Retail Group", "Vireo Telecom", "Marlow Manufacturing",
]
GROWTH_NAMES = [
    "Halcyon Labs", "Pinecrest Media", "Vantage Mobility", "Corely", "Brightfold",
    "Latchkey Software", "Ridgeline Sports", "Ambit Analytics", "Foldpoint",
    "Northaven Travel", "Quillon", "Sableside Foods", "Truenorth Fitness", "Wexler Robotics",
]
STARTUP_NAMES = [
    "Driftwood AI", "Pallas", "Sundial Health", "Copperline", "Marrow", "Tessellate",
    "Junebug", "Owlhouse", "Rill Commerce", "Sparrowtail", "Cobalt Route", "Fernwood",
    "Ashgrove Tech", "Petrichor", "Vellum Studio", "Quarry", "Lodestone", "Bramblewick",
]

# --- Employees --------------------------------------------------------------
# Five developers, each owning one heavy connector plus two light ones.
# Three support engineers and one manager.

DEVELOPERS = [
    {"name": "Priya Raghavan", "owns": ["PostgreSQL", "MySQL", "SQL Server"]},
    {"name": "Daniel Okafor", "owns": ["Salesforce", "HubSpot", "NetSuite"]},
    {"name": "Mei Lin Chow", "owns": ["Snowflake", "BigQuery", "Redshift"]},
    {"name": "Tomas Vrba", "owns": ["MongoDB", "DynamoDB", "Kafka"]},
    {"name": "Aisha Bello", "owns": ["Amazon S3", "Oracle", "Google Sheets"]},
]
SUPPORT_ENGINEERS = ["Marcus Hale", "Ines Duarte", "Rahul Menon"]
MANAGERS = ["Sofia Almeida"]

CHANNELS = ["ticket", "slack", "github"]
