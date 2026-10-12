# Noisy-neighbour mitigation after rate limiting: research notes

Working notes for what comes after "### Rate Limiting" in the "Noisy Neighbour Problem" section of
`src/content/articles/designing-a-multi-tenant-system.md`. The article so far: scale the server, scale the
database connections, shard tenants across database instances, name the noisy neighbour problem, then cap
requests per tenant and per user (`429` + `Retry-After`).

The question, in the author's words: should the next step be **concurrency limits** (a per-tenant cap on
in-flight requests, or a fair share of the connection pool), or go straight to **dedicated instances for
heavy tenants**, then **tiers**? The author's objection to concurrency limits: high-profile customers will
still expect more usage, so a cap does not solve the real problem, and a section on it would be "for the
sake of it".

Sources are primary only: AWS (Builders' Library, Well-Architected SaaS Lens, SaaS Factory, cell-based
architecture guidance), the Azure Architecture Center, Stripe, Shopify and Netflix engineering. All quotes
below were read on the source page on 2026-10-12, unless marked otherwise.

---

## Short answer

1. **No primary source lays out one neat ladder** of rate limit -> concurrency limit -> load shedding ->
   isolation -> tiers. The pieces exist, but in two camps:
   - **The SaaS guidance (AWS SaaS Lens, AWS SaaS Factory, Azure multitenant guidance) skips concurrency
     limits.** It goes from throttling (by tier) straight to silos / dedicated stamps for heavy or premium
     tenants, with tiers as the business wrapper. This matches the author's plan.
   - **The service-operator writing (Stripe, AWS Builders' Library, Netflix) treats concurrency limits as
     a separate, second limiter** next to the rate limiter, because a rate limit counts requests, not
     their cost.
2. **What a concurrency limit solves that a rate limit does not:** expensive or slow requests. A tenant
   inside its requests-per-second limit can still hold many connections at once if each request is slow
   (in-flight = rate × latency, Little's law, as the Netflix library states it). Stripe built its
   concurrent requests limiter for exactly this: CPU-heavy endpoints, and clients retrying on top of them.
   In this article's design, where the scarce resource is database connections, that is the exact gap.
3. **On the author's objection:** the sources do not frame concurrency limits as a way to deny big
   customers capacity. The limit is sized per tenant and raised as the tenant grows (AWS: "increase each
   caller's limit as they grow"), and the SaaS Lens even uses concurrency as the tier lever (Basic 100,
   Advanced 300). So the objection holds against concurrency limits **as the answer to legitimate heavy
   usage**, and every source agrees: that answer is isolation plus tiers. It does not hold against them
   **as a guard on the shared pool** against slow requests, which a rate limit misses.
4. **Recommendation:** one short paragraph (or a few lines) under Rate Limiting, not a full section. Then
   dedicated instances for heavy tenants, then tiers. Details at the end.

---

## 1. Stripe — "Scaling your API with rate limiters" (2017)

<https://stripe.com/blog/rate-limiters> — Paul Tarjan, 30 March 2017.

**What it says.** Stripe runs four limiters in production, in this order of importance:

1. Request rate limiter (requests per second per user)
2. **Concurrent requests limiter** (requests in flight per user)
3. Fleet usage load shedder (reserve capacity for critical traffic)
4. Worker utilization load shedder (shed low-priority traffic when workers are busy)

**Quotes.**

- Concurrent limiter: "this rate limiter says "You can only have 20 API requests in progress at the same
  time"."
- Why: some endpoints are much more resource-heavy than others, and clients retried on them. "These
  retries add more demand to the already overloaded resource, slowing things down even more." The limiter
  "totally solved this".
- How often each fires: the request rate limiter "has rejected millions of requests this month alone",
  while the concurrent limiter "is triggered much less often (12,000 requests this month)".
- Load shedders vs limiters: "A load shedder makes its decisions based on the whole state of the system
  rather than the user who is making the request."
- Where to start: "Start by building a Request Rate Limiter. It is the most important one to prevent
  abuse, and it's by far the one that we use the most frequently."
- Fleet usage load shedder: "If our reservation number is 20%, then any non-critical request over their
  80% allocation would be rejected" (with a `503`).

**Fit.** The clearest first-party, step-by-step source for "rate limit first, concurrency limit second". It
also answers the "what problem" question in one line: requests vary in cost. It says nothing about tenant
isolation or tiers, since Stripe is describing one shared API.

---

## 2. AWS Builders' Library — "Fairness in multi-tenant systems"

<https://builder.aws.com/content/3Eupj3d2bo4fEvlzYbICMZNhQ3B/fairness-in-multi-tenant-systems> (the old
URL <https://aws.amazon.com/builders-library/fairness-in-multi-tenant-systems/> redirects here). Author
handle `dyanacek` (David Yanacek), Sr. Principal Engineer, AWS. The page shows "Published Jun 12, 2026",
which is the date of the move to builder.aws.com; the Builders' Library first ran it around 2021 (my
recollection, not shown on the page).

**What it says.** The most complete first-party walk-through of fairness: placement and rebalancing,
fast load shedding, per-tenant rate limits and quotas, layered admission control, prioritising in-quota
traffic over bursts, letting tenants borrow unused capacity, and raising limits as customers grow.

**Quotes.**

- Why counting requests is not enough: "Some APIs are far more expensive for a service than others." and
  "the cost of an operation is not always known up front." Some services "simply count larger responses
  as multiple requests."
- Concurrency as a quota type: one kind of quota governs "the number of things the client can have
  running at the same time."
- Concurrency as isolation: "AWS Lambda exposes per-function concurrency isolation to isolate workloads
  from each other."
- Big customers get more, not less: "We implement Auto Scaling and increase each caller's limit as they
  grow in the normal course of business." Customers "often ask the service to raise its quota", and "The
  service should know that it might need to scale its fleet and increase the client's quota
  automatically."
- Bursting: "If the fleet is provisioned with some "slack" capacity that is underutilized, we let the
  caller burst into it." But in-quota traffic wins: "their traffic should take priority over Blue's burst
  traffic."

**Fit.** Directly addresses the author's objection. Limits are per caller and grow with the caller; the
point is that the excess part of one tenant's traffic is rejected instead of everyone's. It does not use
the words "dedicated", "cell" or "shuffle sharding", so it stops before the isolation step.

---

## 3. AWS Builders' Library — "Avoiding insurmountable queue backlogs"

<https://builder.aws.com/content/3EuRcgkTP1MI0c7zM8W6HL3WIqA/avoiding-insurmountable-queue-backlogs> (old
URL <https://aws.amazon.com/builders-library/avoiding-insurmountable-queue-backlogs/> redirects). David
Yanacek; originally ~2020 (Builders' Library), same republish caveat as above.

**Quotes.**

- Per-customer rate limits first: "setting per-customer rate-based limits, with some flexibility for
  bursting."
- Then a concurrency cap: a semaphore "limits the amount of concurrency that can be used for any single
  workload."
- Then per-customer separation: "Instead of sharing one queue across all customers, in some systems we
  give each customer its own queue." Lambda uses shuffle sharding: it "provisions a fixed number of
  queues, and hashes each customer to a small number of queues."
- Then sidelining excess: "they enqueue those excess messages into separate spillover queues".
- The goal: "no customer's workload impacts another customer."

**Fit.** The nearest thing to a primary-source ladder for async work: rate limit -> concurrency cap ->
separate queues / shuffle sharding -> spillover. Useful if the article ever covers background jobs.

---

## 4. Netflix — `concurrency-limits` library (2018)

<https://github.com/Netflix/concurrency-limits> (README). The companion blog post "Performance Under Load"
(Netflix Tech Blog, 2018, <https://netflixtechblog.com/performance-under-load-3e6fa9a60581>) returned 403
to my fetches, so only the README is verified here.

**Quotes.**

- "Instead of thinking in terms of RPS, we should be thinking in terms of concurrent requests."
- Little's law: "`Limit = Average RPS * Average Latency`."
- Partitioned limits: "we guarantee specific types of requests get a certain percentage of the
  concurrency limit" (the gRPC example splits one limit 90/10 between live and batch traffic).

**Fit.** Gives the one-line reason a rate limit does not bound in-flight work: in-flight = rate ×
latency. If latency doubles (a slow query, a tenant's large export), the same allowed rate holds twice the
connections. The library's limits are adaptive and per service, not per tenant, so it is the reasoning,
not the tenant pattern.

---

## 5. AWS Builders' Library — "Using load shedding to avoid overload"

<https://builder.aws.com/content/3Eun1EEyX6p2e3VYNyRLSJzLuMV/using-load-shedding-to-avoid-overload> (old
URL <https://aws.amazon.com/builders-library/using-load-shedding-to-avoid-overload/> redirects). David
Yanacek; originally ~2019.

**Quotes.**

- On a fixed max-connections cap: the team found it "too imprecise to provide the complete answer to the
  puzzle" (too low rejects work the server could do; too high lets servers go slow).
- "They use throttling to ensure fairness among clients."
- "Prioritization and throttling can be used together to avoid strict throttling ceilings"; "the excess
  requests from these clients might be prioritized lower than within-quota requests from other clients."

**Fit.** A counterweight: a fixed concurrency cap is a blunt tool. Load shedding and priority sit after
per-tenant limits and are system-wide, not per tenant. Probably out of scope for this article.

---

## 6. AWS Well-Architected SaaS Lens — PERF 1 and PERF 3

- PERF 1, "How do you prevent one tenant from adversely impacting the experience of another tenant?":
  <https://wa.aws.amazon.com/saas.question.PERF_1.en.html>
- PERF 3 (tiers), on the Monitoring page:
  <https://docs.aws.amazon.com/wellarchitected/latest/saas-lens/monitoring.html>

**Quotes (PERF 1).**

- "Use throttling policies to prevent individual tenants from placing excess load on the system."
- "Prevent lower tier tenants from impacting the performance of higher tier tenants."
- Silo only the bottleneck: "Siloes should only be introduced at the layer that represents the bottleneck
  of the experience."
- "Identify the workflows where the load of individual tenants could consume excess resources", then
  "create separate siloes where each tenant is given dedicated resources."
- "Support a model where higher end tiers might have siloed deployments for key services to minimize
  noisy neighbor impacts."

**Quotes (PERF 3).**

- "The least complex way to approach this problem is to introduce throttling policies that are associated
  with individual tenant tiers."
- Concurrency as the tier lever: "in AWS Lambda, you can use reserve concurrency to limit the consumption
  of a given tenant tier" — Basic 100, Advanced 300, Premium gets the rest.
- "deploying siloed microservices for higher tier tenants, eliminating any noisy neighbor considerations
  for these specific services."
- "Even if your system could accommodate the load of these tenants, you might choose to limit this load
  purely based on cost or business considerations."

**Fit.** The canonical SaaS ladder, and it matches the author's plan: throttle (by tier) -> silo the
bottleneck for heavy / premium tenants -> tiers. Concurrency shows up only as a way to size tiers, not as
its own step. Note the "silo only the bottleneck" line: for this article the bottleneck is the database,
so a dedicated *database instance* for a heavy tenant is the natural first silo, which the sharding work
already makes possible.

---

## 7. AWS SaaS Factory — "Performance Efficiency in AWS Multi-Tenant SaaS Environments" (2021)

<https://aws.amazon.com/blogs/apn/performance-efficiency-in-aws-multi-tenant-saas-environments/> —
Humberto Somensi, AWS SaaS Factory, 26 October 2021.

**Quotes.**

- "impose limits, potentially by tier, and apply throttling"
- "Basic tier tenants will operate under lower limits than premium tenants"
- "For services that have critical SLAs, and noisy neighbor mitigation strategies or scaling policies do
  not ensure the appropriate levels of service, isolating tenant resources in silos is a valid approach."

**Fit.** Throttling -> tier-based limits -> scaling -> silo as the fallback. Does not mention concurrency
limits at all. This is the clearest example of a source that goes from throttling straight to isolation.

---

## 8. Azure Architecture Center — Noisy Neighbor antipattern

<https://learn.microsoft.com/en-us/azure/architecture/antipatterns/noisy-neighbor/noisy-neighbor> —
John Downs et al., Microsoft; dated 11 June 2025.

**Provider actions, in the page's order:** monitor per-tenant usage; "Apply resource governance" (quota
enforcement through the Throttling or Rate Limiting pattern); provision more infrastructure (shards,
stamps); let tenants buy reserved capacity; rebalance tenants across stamps; check downstream controls;
"Restrict the operations that tenants can perform"; "Provide a quality of service (QoS) system".

**Quotes.**

- "Sharing a single resource inherently carries the risk of noisy neighbor problems that you can't
  completely avoid."
- "restrict tenants from running resource-intensive database queries by setting a maximum returnable
  record count or query time limit."
- "If you host multiple instances of your solution, consider rebalancing tenants across the instances or
  stamps."
- "Enable tenants to purchase pre-provisioned or reserved capacity."
- "treat these problems as resource governance problems and to apply usage quotas, throttling, and
  governance controls".

**Fit.** A list, not a ladder, and no concurrency limit by name. Its answer to expensive requests is to
cap the operation itself (query time limit, row limit) rather than cap in-flight requests. "Reserved
capacity" and "rebalance across stamps" support the dedicated-instance and tier steps.

---

## 9. Azure Architecture Center — compute approaches and Deployment Stamps

- Compute: <https://learn.microsoft.com/en-us/azure/architecture/guide/multitenant/approaches/compute>
  (dated 23 June 2026)
- Overview / stamps:
  <https://learn.microsoft.com/en-us/azure/architecture/guide/multitenant/approaches/overview> (dated
  11 June 2025)

**Quotes.**

- Shared compute: "You can often mitigate this risk by ensuring that you scale your solution
  appropriately and by applying controls like quotas and API limits to avoid tenants that consume more
  than their fair share of the capacity."
- Dedicated compute: "Dedicated resources mitigate the risk of the noisy neighbor problem by ensuring that
  the compute resources for each tenant are isolated from the others. ... However, dedicated resources
  typically incur a higher cost".
- Single-tenant stamps: "This pattern provides the highest level of isolation and helps to avoid the noisy
  neighbor problem." Cost: "You must also provision resources to handle the tenant's peak workload. Make
  sure that your pricing model offsets the cost of deployment for the tenant's infrastructure."
- Scale of the approach: "Single-tenant stamps often work well with a few tenants."
- Tiers via queues: "tenants who pay for a higher service level might have a higher set of dedicated
  resources to process the work from their queue messages."

**Fit.** The best primary support for "move heavy tenants to dedicated instances, then charge for it":
dedicated is the strongest isolation, it costs more, and pricing has to cover it. That is the bridge to
tiers.

---

## 10. AWS Builders' Library — "Workload isolation using shuffle-sharding"

<https://builder.aws.com/content/3F06NpJ8YeoIGP8VHTw4n81pFn8/workload-isolation-using-shuffle-sharding>
(old URL <https://aws.amazon.com/builders-library/workload-isolation-using-shuffle-sharding/> redirects).
Colm MacCárthaigh; originally ~2019.

**Quotes.**

- Builds on plain sharding: "first consider how a system can be made more scalable and resilient through
  ordinary sharding."
- "With eight workers, there are 28 unique combinations of two workers, which means that there are 28
  possible shuffle shards." ... "then the scope of impact due to a problem is just 1/28th."

**Fit.** A step past dedicated instances, for reducing blast radius across many tenants without a box per
tenant. Mention at most in passing; out of scope for this article's level.

---

## 11. AWS — "Reducing the Scope of Impact with Cell-Based Architecture" (2023)

<https://docs.aws.amazon.com/wellarchitected/latest/reducing-scope-of-impact-with-cell-based-architecture/cell-partition.html>
— AWS whitepaper, published 20 September 2023.

**Quote.** "`CustomerID` might seem like a reasonable candidate partition key ... but thought needs to go
into how to handle really large customers. It is unlikely you want to limit the degree to which a customer
can adopt your service."

**Fit.** The same point as the author's objection, from AWS: you do not cap a big customer's adoption; you
design placement so a big customer can grow (even across cells). Supports isolation over capping as the
answer to legitimate heavy usage.

---

## 12. Shopify — "A Pods Architecture To Allow Shopify To Scale" (2018)

<https://shopify.engineering/a-pods-architecture-to-allow-shopify-to-scale> — Xavier Denis, 2 March 2018.

**Quotes.**

- "Simply sharding the databases wasn't enough."
- "A pod consists of a set of shops that live on a fully isolated set of datastores."
- Pods prevent "a single shop from sucking up database time across the platform".

**Fit.** A real-world version of the article's path: shard the databases -> group tenants into isolated
units (pods) so one tenant's load stays in its pod. Secondary coverage (InfoQ, 2017 GOTO talk by Simon
Eskildsen) says large merchants can get dedicated pods; the Shopify post itself does not say this, so do
not cite it for that.

---

## Not verified

- **Tod Golding, _Building Multi-Tenant SaaS Architectures_ (O'Reilly, 2024).** Retail listings confirm it
  covers noisy neighbour, tenant isolation and tiering. The O'Reilly page returned 403 and I could not
  read the chapters, so no quotes or chapter numbers here. Golding also leads AWS SaaS Factory, whose SaaS
  Lens (§6) follows the same throttle -> silo -> tier line.
- **Marc Brooker's blog.** Searches found no post on per-tenant concurrency limits or noisy-neighbour
  mitigation. Not cited.
- **Slack.** Only its public API rate-limit docs (per method, per workspace, per app) turned up; no
  engineering post on tenant isolation for large workspaces.

---

## Recommendation for the article

After "### Rate Limiting", in this order:

1. **One short paragraph: rate limits count requests, not their cost.** A tenant inside its limit can
   still send slow requests (a large export, a heavy report) that each hold a database connection for a
   long time. In-flight work = rate × latency, so a rate limit does not bound how many connections a
   tenant holds. A per-tenant cap on in-flight requests (or on its share of the connection pool) closes
   that gap; Stripe runs one next to its rate limiter for this reason. Then the turn: like the rate
   limit, it only stops a tenant from taking more than its share. It does not help a high-profile tenant
   that legitimately needs more, which is the real problem. Sources: Stripe (§1), AWS Fairness (§2),
   Netflix README (§4).
2. **Dedicated instances for heavy tenants (section).** Move the few heavy tenants to their own database
   instance (and, if needed, their own servers), and silo only the layer that is the bottleneck. The
   sharding work already makes this a move, not a rewrite. Sources: SaaS Lens PERF 1 (§6), AWS SaaS
   Factory (§7), Azure stamps (§9), Shopify pods (§12).
3. **Tiers (section).** Dedicated capacity costs more, so it has to be priced: shared tier with lower
   limits, dedicated tier for tenants who pay for it. Limits, including any concurrency cap, are sized
   per tier. Sources: SaaS Lens PERF 3 (§6), Azure stamps pricing note (§9).
4. **Optional, one line each, or skip:** load shedding / priority for system-wide overload (Stripe §1,
   AWS §5); shuffle sharding and cells for blast radius at larger scale (§10, §11).

**Concurrency limits: a paragraph, not a section.** The author's objection is right about what they do
not solve (legitimate heavy usage), and the SaaS-specific guidance skips them for that reason. But the
gap they close (slow requests holding connections) is real and specific to this article's connection-bound
design, so leaving it out entirely would leave a hole a careful reader will spot. One paragraph that names
the gap and then says why it is not the answer makes a natural bridge into dedicated instances.
