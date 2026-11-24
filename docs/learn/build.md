<!-- Generated from sources.yaml by api/scripts/learn_index.py. Do not edit by hand. -->
# Learning index: build

<a id="build.cargo-release-profile"></a>
### Cargo release profile

Stories: 8.10.4 | Phase: P1
Keywords: lto, panic abort, strip, codegen-units, opt-level

The release profile controls size and speed of the agent binary.
lto true or thin links across crates; codegen-units 1 helps optimization.
panic abort drops unwinding code.
strip symbols shrinks the file; the default is none.

Sources:
- [Profiles](https://doc.rust-lang.org/cargo/reference/profiles.html) (primary): The Rust Project, The Cargo Book (current), checked 2026-11-24

<a id="build.cargo-zigbuild"></a>
### cargo-zigbuild

Stories: 8.10.4 | Phase: P1
Keywords: zig, linker, cross compile, musl target

cargo-zigbuild uses Zig as the linker, so no container is needed.
For a fully static binary, choose a musl target.
A glibc version can be set as a target suffix.
It is the alternative to cross.

Sources:
- [cargo-zigbuild repository README](https://github.com/rust-cross/cargo-zigbuild) (primary): rust-cross project, README, default branch, checked 2026-11-24

<a id="build.cross-rs"></a>
### cross (cross-rs)

Stories: 8.10.4 | Phase: P1
Keywords: cross, docker, podman, cross compile

cross wraps cargo and builds inside a container with the target toolchain.
It needs Docker 20.10+ or Podman 3.4+.
Use the same flags as cargo, for example cross build --target.
Config lives in Cross.toml or Cargo.toml metadata.

Sources:
- [cross repository README](https://github.com/cross-rs/cross) (primary): cross-rs project, README, MSRV 1.85.0, checked 2026-11-24

<a id="build.mimalloc"></a>
### mimalloc allocator

Stories: 8.10.4 | Phase: P1
Keywords: mimalloc, global_allocator, musl malloc, allocator

The musl default allocator can be slow under heavy threads.
The mimalloc crate replaces it through #[global_allocator].
The optional secure feature adds hardening for a speed cost.
Measure before you adopt it.

Sources:
- [mimalloc crate documentation](https://docs.rs/mimalloc/latest/mimalloc/) (primary): docs.rs, mimalloc 0.1.52, checked 2026-11-24

<a id="build.reproducible-builds"></a>
### Reproducible Rust builds

Stories: 8.10.4 | Phase: P1
Keywords: remap-path-prefix, reproducible, Cargo.lock, checksum

Same inputs should give the same binary hash.
rustc --remap-path-prefix removes build paths from output.
Pin toolchain and dependencies; build with --locked.
Publish a checksum and verify it before injecting the binary.

Sources:
- [Command-line arguments (rustc)](https://doc.rust-lang.org/rustc/command-line-arguments.html) (primary): The Rust Project, rustc book (current), checked 2026-11-24
- [Profiles](https://doc.rust-lang.org/cargo/reference/profiles.html): The Rust Project, The Cargo Book (current), checked 2026-11-24

<a id="build.rust-musl-targets"></a>
### Rust musl targets

Stories: 8.10.4 | Phase: P1
Keywords: musl, static linking, x86_64-unknown-linux-musl, aarch64-unknown-linux-musl

The musl targets produce static Linux binaries that need no libc in the image.
Both x86_64 and aarch64 musl are Tier 2 with host tools.
The platform page lists musl 1.2.5.
Install them with rustup target add.

Sources:
- [Platform Support](https://doc.rust-lang.org/rustc/platform-support.html) (primary): The Rust Project, rustc book, musl 1.2.5 listed, checked 2026-11-24
