<!-- Generated from sources.yaml by api/scripts/learn_index.py. Do not edit by hand. -->
# Learning index: protocol

<a id="protocol.base64-rfc4648"></a>
### Base64 encoding (RFC 4648)

Stories: 8.9.3 | Phase: P1
Keywords: base64, padding, base64url, file bodies

File bytes cannot sit raw in JSON, so encode them as base64 strings.
The standard alphabet uses plus and slash with equals padding.
The url-safe form swaps in dash and underscore.
Pick one form and test it with shared fixtures on both sides.

Sources:
- [RFC 4648: The Base16, Base32, and Base64 Data Encodings](https://www.rfc-editor.org/rfc/rfc4648) (primary): IETF / RFC Editor, RFC 4648, October 2006, checked 2026-11-24

<a id="protocol.datamodel-code-generator"></a>
### datamodel-code-generator

Stories: 8.9.3 | Phase: P1
Keywords: codegen, pydantic v2, jsonschema input, version pin

The tool turns a JSON Schema file into Pydantic v2 models.
Use input type jsonschema and output type pydantic_v2.BaseModel.
Pin the tool version so generated output does not churn.
Commit the generated file and check it in CI.

Sources:
- [datamodel-code-generator repository](https://github.com/koxudaxi/datamodel-code-generator) (primary): koxudaxi (project maintainer), default branch, checked 2026-11-24 (version not shown), checked 2026-11-24

<a id="protocol.json-number-precision"></a>
### JSON number interoperability (RFC 8259 section 6)

Stories: 8.9.3 | Phase: P1
Keywords: u64, IEEE 754, 2^53, integer precision

JSON numbers have no fixed size, but most parsers read them as IEEE 754 doubles.
Integers outside plus or minus 2^53 minus 1 may lose precision.
A Rust u64 can exceed that range, so send large ids or sizes as strings.
Add a fixture with a big value to catch this.

Sources:
- [RFC 8259: The JSON Data Interchange Format](https://www.rfc-editor.org/rfc/rfc8259) (primary): IETF / RFC Editor, RFC 8259, December 2017, checked 2026-11-24

<a id="protocol.json-schema-2020-12"></a>
### JSON Schema 2020-12 core

Stories: 8.9.3 | Phase: P1
Keywords: oneOf, const, additionalProperties, unevaluatedProperties

The schema file is the single contract between the Rust agent and the Python API.
Use oneOf with a const tag field to describe each message type.
additionalProperties false rejects unknown fields; this limits forward compatibility.
The Core spec defines applicators and unevaluatedProperties for composed schemas.

Sources:
- [JSON Schema: A Media Type for Describing JSON Documents](https://json-schema.org/draft/2020-12/json-schema-core) (primary): JSON Schema organization, draft-bhutton-json-schema-01 (2020-12), 2022-06-16, checked 2026-11-24

<a id="protocol.jsonschema-crate"></a>
### jsonschema crate (Rust validator)

Stories: 8.9.3 | Phase: P1
Keywords: jsonschema, validate, is_valid, draft 2020-12

Use the crate as a dev-dependency to validate Rust-made messages against the schema.
is_valid returns a bool; validate returns the first error.
It supports Draft 2020-12 and older drafts.
Pick the draft explicitly to match the schema file.

Sources:
- [jsonschema crate documentation](https://docs.rs/jsonschema/latest/jsonschema/) (primary): docs.rs, jsonschema 0.63.1, checked 2026-11-24

<a id="protocol.messagepack"></a>
### MessagePack format

Stories: 4.3.1 | Phase: P1
Keywords: messagepack, rmp-serde, binary format, bin type

MessagePack is a binary format with a native bin type, so no base64 is needed.
The Rust crate rmp-serde plugs into serde.
to_vec_named keeps field names, which suits tagged enums.
The study guide picks JSON first; MessagePack is the alternative.

Sources:
- [MessagePack specification](https://github.com/msgpack/msgpack/blob/master/spec.md) (primary): MessagePack project, spec.md, master branch, checked 2026-11-24
- [rmp-serde crate documentation](https://docs.rs/rmp-serde/latest/rmp_serde/): docs.rs, rmp-serde 1.3.1, checked 2026-11-24

<a id="protocol.ndjson-framing"></a>
### NDJSON and length-delimited framing

Stories: 4.3.1 | Phase: P1
Keywords: ndjson, LengthDelimitedCodec, frame size cap, framing

NDJSON puts one JSON text per line; texts must not contain raw newlines.
Length-delimited frames use a size prefix instead.
In tokio-util the codec exposes a max frame length setting.
Always cap the frame size to stop a huge length prefix.

Sources:
- [NDJSON specification](https://github.com/ndjson/ndjson-spec) (primary): ndjson project, 1.0.0, checked 2026-11-24
- [LengthDelimitedCodec](https://docs.rs/tokio-util/latest/tokio_util/codec/length_delimited/struct.LengthDelimitedCodec.html): docs.rs, tokio-util 0.7.20, checked 2026-11-24

<a id="protocol.protocol-semver"></a>
### Semantic Versioning for the protocol

Stories: 8.9.3 | Phase: P1
Keywords: semver, major version, minor version, feature flags

Apply semver to the protocol: a major change breaks compatibility, so refuse the peer.
A minor change adds features in a compatible way; negotiate with feature flags.
A patch fixes bugs without changing the wire format.
Send the version in the first message.

Sources:
- [Semantic Versioning 2.0.0](https://github.com/semver/semver/blob/master/semver.md) (primary): semver project, 2.0.0, checked 2026-11-24

<a id="protocol.pydantic-discriminated-unions"></a>
### Pydantic discriminated unions

Stories: 8.9.3 | Phase: P1
Keywords: discriminator, Literal tag, tagged union, Field

Field(discriminator="type") picks the union member from one tag field.
Each member declares the tag as a Literal type.
This gives faster validation and clearer errors than a plain union.
It maps to the oneOf plus const shape in the schema.

Sources:
- [Unions (Pydantic docs source)](https://github.com/pydantic/pydantic/blob/main/docs/concepts/unions.md) (primary): Pydantic project, main branch (docs.pydantic.dev now redirects to pydantic.dev), checked 2026-11-24

<a id="protocol.schemars"></a>
### schemars (JSON Schema from Rust types)

Stories: 8.9.3 | Phase: P1
Keywords: schemars, JsonSchema derive, schema_for

Derive JsonSchema on Rust types, then call schema_for! to get a schema.
It respects serde attributes.
Use it only to compare with the hand-written schema file, not as the source.
A diff shows drift between Rust types and the contract.

Sources:
- [schemars crate documentation](https://docs.rs/schemars/latest/schemars/) (primary): docs.rs, schemars 1.2.3, checked 2026-11-24

<a id="protocol.serde-tagged-enums"></a>
### Serde enum representations

Stories: 8.9.3 | Phase: P1
Keywords: serde tag, internally tagged, deny_unknown_fields, untagged

Serde has four enum forms: external (default), internal tag, adjacent tag and content, untagged.
Internal tagging with tag="type" matches a oneOf plus const schema.
Internal tags do not allow tuple variants.
deny_unknown_fields blocks new fields, so it costs forward compatibility.

Sources:
- [Enum representations (serde.rs source)](https://github.com/serde-rs/serde-rs.github.io/blob/master/_src/enum-representations.md) (primary): serde-rs project, master branch; serde 1.0.229 on docs.rs, checked 2026-11-24
- [serde crate documentation](https://docs.rs/serde/latest/serde/): docs.rs, serde 1.0.229, checked 2026-11-24

<a id="protocol.tokio-tungstenite"></a>
### tokio-tungstenite

Stories: 4.3.3 | Phase: P1
Keywords: tokio-tungstenite, accept_hdr_async, websocket server, handshake callback

The crate adds async WebSocket streams on top of tungstenite and tokio.
accept_async upgrades a stream; accept_hdr_async adds a header callback.
Use the callback to check token and Origin before the upgrade.
The stream is both a Stream and a Sink of messages.

Sources:
- [tokio-tungstenite crate documentation](https://docs.rs/tokio-tungstenite/latest/tokio_tungstenite/) (primary): docs.rs, tokio-tungstenite 0.30.0, checked 2026-11-24

<a id="protocol.websocket-rfc6455"></a>
### WebSocket protocol (RFC 6455)

Stories: 4.3.3 | Phase: P1
Keywords: websocket, frame opcodes, masking, close frame

Frames carry an opcode: text, binary, ping, pong or close.
Client-to-server frames are masked with a 32-bit key.
Use binary frames for terminal data and text frames for JSON control messages.
The handshake is an HTTP upgrade where origin and token checks happen.

Sources:
- [RFC 6455: The WebSocket Protocol](https://www.rfc-editor.org/rfc/rfc6455) (primary): IETF / RFC Editor, RFC 6455, December 2011, checked 2026-11-24
