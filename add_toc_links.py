#!/usr/bin/env python3
"""Add 'Return to Table of Contents' links after major sections."""

import re

filepath = "docs/design/solax-modbus-software-design-specification.md"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Patterns to add return links
patterns = [
    (r'(- Data types follow IEC 61131-3 conventions\n\n)(---)', 
     r'\1[Return to Table of Contents](<#table of contents>)\n\n\2'),
    (r'(6\. \*\*Protocol Fidelity\*\*: Maintain strict adherence to vendor protocol specifications\n\n)(---)',
     r'\1[Return to Table of Contents](<#table of contents>)\n\n\2'),
    (r'(- Net grid interaction\n\n)(---)',
     r'\1[Return to Table of Contents](<#table of contents>)\n\n\2'),
    (r'(\*\*REQ-NF-USE-004\*\*: The system SHALL provide health check endpoint for monitoring tools\.\n\n)(---)',
     r'\1[Return to Table of Contents](<#table of contents>)\n\n\2'),
    (r'(    def get_next_poll_time\(inverter_id: str\) -> datetime\n```\n\n)(---)',
     r'\1[Return to Table of Contents](<#table of contents>)\n\n\2'),
    (r'(  audit_log: /var/log/solax-monitor/audit\.log\n```\n\n)(---)',
     r'\1[Return to Table of Contents](<#table of contents>)\n\n\2'),
    (r'(│  Endpoint   │\n└─────────────┘\n```\n\n)(### 7\.2)',
     r'\1[Return to Table of Contents](<#table of contents>)\n\n\2'),
    (r'(│  Response   │\n└─────────────┘\n```\n\n)(---)',
     r'\1[Return to Table of Contents](<#table of contents>)\n\n\2'),
    (r'(- Anomalous network traffic detection\n\n)(---)',
     r'\1[Return to Table of Contents](<#table of contents>)\n\n\2'),
    (r'(- Database replication: InfluxDB clustering\n\n)(---)',
     r'\1[Return to Table of Contents](<#table of contents>)\n\n\2'),
    (r'(\| AC-006 \| Memory footprint <512MB \| Resource monitoring \|\n\n)(---)',
     r'\1[Return to Table of Contents](<#table of contents>)\n\n\2'),
    (r'(7\. Resume normal operation\n\n)(---)',
     r'\1[Return to Table of Contents](<#table of contents>)\n\n\2'),
    (r'(            raise e\n```\n\n)(---)',
     r'\1[Return to Table of Contents](<#table of contents>)\n\n\2'),
    (r'(\| Startup time \| <10s \| Systemd service metrics \|\n\n)(---)',
     r'\1[Return to Table of Contents](<#table of contents>)\n\n\2'),
    (r'(- Virtual power plant capabilities\n\n)(---)',
     r'\1[Return to Table of Contents](<#table of contents>)\n\n\2'),
    (r'(5\. \*\*Resource Availability\*\*: Sufficient storage for retention policies\n\n)(---)',
     r'\1[Return to Table of Contents](<#table of contents>)\n\n\2'),
    (r'(- Change management procedures\n\n)(---)',
     r'\1[Return to Table of Contents](<#table of contents>)\n\n\2'),
    (r'(\| Unit ID \| Modbus device identifier \(slave address\) \|\n\n)(---)',
     r'\1[Return to Table of Contents](<#table of contents>)\n\n\2'),
    (r'(3\. IEC 62109 - Safety of power converters for use in photovoltaic power systems\n\n)(---)',
     r'\1[Return to Table of Contents](<#table of contents>)\n\n\2'),
    (r'(Consult Solax protocol specification for complete register documentation\.\n\n)(### A\.2)',
     r'\1[Return to Table of Contents](<#table of contents>)\n\n\2'),
    (r'(\[Detailed holding register map would be included here with all configuration parameters\]\n\n)(---)',
     r'\1[Return to Table of Contents](<#table of contents>)\n\n\2'),
    (r'(    location: "Parking"\n```\n\n)(---)',
     r'\1[Return to Table of Contents](<#table of contents>)\n\n\2'),
    (r'(}\n```\n\n)(---\n\n## Appendix D)',
     r'\1[Return to Table of Contents](<#table of contents>)\n\n\2'),
    (r'(        └─ Check number of concurrent inverters\n```\n\n)(---)',
     r'\1[Return to Table of Contents](<#table of contents>)\n\n\2'),
]

for pattern, replacement in patterns:
    content = re.sub(pattern, replacement, content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Added 'Return to Table of Contents' links to all major sections")
