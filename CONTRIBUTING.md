# Contributing

Contributions should improve reproducible measurement of AI and agent capability. Start with an issue proposing a domain, task family or evaluator improvement.

A task contribution must provide:

- An original or appropriately licensed prompt with provenance.
- Precise conventions, units, constraints and machine-readable output format.
- A deterministic grader and an independently verified reference answer.
- A discussion of ambiguity, alternate valid solutions and numerical tolerance.
- A difficulty label supported by measured evidence, or explicitly `uncalibrated`.

Do not claim frontier difficulty based only on subject matter. Avoid copyrighted examination questions without permission. Do not add private data, model API credentials, or undisclosed external services. Keep reference answers and solution notes out of public prompt exports.

Run `python -m pytest -q` before submitting a pull request. Changes to existing prompts or reference answers require a suite-version change so historical scores remain interpretable. New grader types need explicit validation and negative tests.
