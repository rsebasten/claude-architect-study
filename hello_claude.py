#!/usr/bin/env python3

import subprocess


prompt = """You are a concise assistant for an airline's support team.

Can I change my flight for free within 24 hours?"""

result = subprocess.run(
    ["claude", "--print", prompt],
    check=True,
    text=True,
    capture_output=True,
)

print(result.stdout)
