# Custom Domains

Configure custom domains for Pages projects.

## Adding a Custom Domain

### Dashboard Method

1. Workers & Pages > Project > Custom domains
2. Set up a domain
3. Enter domain name
4. Follow activation steps

### Domain Types

| Type                          | Requirements                                       |
| ----------------------------- | -------------------------------------------------- |
| Apex domain (`example.com`)   | Must add zone to Cloudflare, configure nameservers |
| Subdomain (`app.example.com`) | CNAME record only (zone optional)                  |

---

## DNS Configuration

### Subdomain (Recommended)

Add CNAME record in your DNS provider:

| Type  | Name  | Content               |
| ----- | ----- | --------------------- |
| CNAME | `app` | `<project>.pages.dev` |

Example:

```
shop.example.com → my-store.pages.dev
```

### Apex Domain

1. Add domain to Cloudflare as a zone
2. Update nameservers at registrar to Cloudflare
3. CNAME record added automatically

---

## SSL/TLS

- Automatic SSL certificate issuance
- Edge Certificates enabled by default
- HTTPS enforced

### CAA Records

If you have CAA records, add:

```
example.com. CAA 0 issue "digicert.com"
example.com. CAA 0 issue "letsencrypt.org"
example.com. CAA 0 issue "pki.goog"
```

> Missing CAA records may block certificate issuance.

---

## Multiple Domains

Attach multiple custom domains to same project:

1. Primary domain: `www.example.com`
2. Redirect domain: `example.com` → redirect to `www.example.com`

---

## Removing Custom Domain

1. Delete CNAME record from DNS zone
2. Workers & Pages > Project > Custom domains
3. Remove domain from project

---

## Disable pages.dev Access

Prevent access to `*.pages.dev` subdomain:

### Method 1: Cloudflare Access

Apply Access policy to pages.dev subdomain.

### Method 2: Bulk Redirects

Create account-level Bulk Redirect:

```
<project>.pages.dev/* → https://example.com/:splat 301
```

---

## Preview Subdomain Access

Preview deployments use pattern:

```
<branch>.<project>.pages.dev
```

### Restrict Preview Access

1. Apply Cloudflare Access policy
2. Configure allowed users/groups

---

## Caching

### Default Behavior

- Pages handles caching automatically
- Assets served from Tiered Cache
- No additional configuration needed

### Custom Domain Caching

When using custom domain via Cloudflare zone:

- Zone caching rules may apply
- Avoid conflicting cache settings

### Purge Cache

After deployment, stale assets may persist:

1. Go to zone Caching settings
2. Purge Everything

> Deploy triggers automatic cache invalidation for most assets.

---

## Known Issues

### Domain Inactive After DNS Change

If domain was temporarily pointed elsewhere:

1. Domain may become inactive
2. Re-validate in project settings
3. Or use Origin Rules for temporary redirects

### Conflicting Zone Settings

Page Rules or other zone settings may override Pages behavior:

- Disable conflicting Page Rules
- Review zone caching configuration
- Check redirect rules

---

## Domain Verification

For new domains:

1. Add TXT record if required for verification
2. Wait for DNS propagation (up to 48 hours)
3. Check domain status in dashboard

---

## Troubleshooting

| Issue                   | Solution                                     |
| ----------------------- | -------------------------------------------- |
| SSL certificate pending | Check CAA records, wait for issuance         |
| Domain not resolving    | Verify CNAME points to `<project>.pages.dev` |
| Redirect loop           | Check conflicting redirects in zone          |
| 522/523 errors          | Verify project is deployed and healthy       |
