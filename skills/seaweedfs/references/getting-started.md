# Getting Started

Source: https://github.com/seaweedfs/seaweedfs/wiki/Getting-Started

## What this page is about

- It contrasts the beginner-friendly `weed mini` path with the multi-component production path.
- It shows the minimal commands for master, volume, and combined single-host setups.
- It includes Docker-based bootstrap examples and persistence notes.

## Actionable takeaways

- Use `weed mini -dir=/data` only for learning, demos, local validation, and quick S3 experiments.
- Treat `weed server` and explicit `weed master` plus `weed volume` commands as the baseline for production-oriented reasoning.
- Put the `weed` binary on every relevant host and inspect subcommand flags with `./weed -h`, `./weed master -h`, and `./weed volume -h` before composing services.
- When starting a master, set `-ip` to a reachable address instead of relying on `localhost` if other nodes must join.
- When starting a volume server, define the master address, storage directory, and capacity limit deliberately instead of relying on defaults.
- If the master uses a non-default gRPC port, pass the master address as `<host>:<port>.<grpcPort>` to dependent services.
- For a simple one-master, one-volume topology, `weed server` is the shortest path for a combined process layout on one host.
- Validate installation by uploading a directory with `weed upload` and comparing logical file size to actual disk usage; text-heavy workloads may compress significantly.
- In containers, persist `/data` with Docker volumes or host mounts; the page explicitly points to volumes as the preferred persistence mechanism.
- Expose the standard service ports intentionally and document which interfaces are meant for admin, filer, S3, or volume access.
- Set `-publicIp` correctly in containerized or NATed deployments so clients and peers resolve the node address properly.

## Gotchas / prohibitions

- Do not use `weed mini` for production; the page states it may change without backward compatibility guarantees.
- Do not assume `localhost` values work once nodes are distributed across machines or containers.
- Do not skip persistent storage planning for Docker deployments.
- Do not forget the gRPC port behavior when overriding master ports.

## How to apply in a real repo

- Document two bootstrap modes separately: local learning (`weed mini`) and production (`weed master` plus `weed volume` or `weed server`).
- Keep example commands parameterized with explicit IPs, ports, and storage paths so operators do not cargo-cult local defaults.
- Add a smoke-test checklist around `weed upload`, cluster status, UI availability, and disk consumption after initial deploy.
- Make persistence and advertised address settings part of every Docker or Kubernetes deployment review.
