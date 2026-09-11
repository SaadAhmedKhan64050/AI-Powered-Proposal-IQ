"""
CLI entrypoint for Proposal IQ.

Usage:
    python -m proposal_iq.main \\
        --company-name "Acme Logistics" \\
        --company-url "https://acme-logistics.example.com" \\
        --contact-name "Jane Doe" \\
        --contact-email "jane@example.com"

Add --no-email to run the full research/opportunity/report pipeline and
print the report without actually sending an email (useful for iterating on
prompts without burning your daily Resend quota, or for the eval harness).
"""
import argparse
import json
import sys
from pathlib import Path

from app.graph import build_graph

OUTPUT_DIR = Path("outputs")


def parse_args():
    parser = argparse.ArgumentParser(description="Proposal IQ — company research to emailed report.")
    parser.add_argument("--company-name", required=True)
    parser.add_argument("--company-url", required=True)
    parser.add_argument("--contact-name", required=True)
    parser.add_argument("--contact-email", required=True)
    parser.add_argument(
        "--no-email",
        action="store_true",
        help="Run the pipeline and print/save the report, but skip sending the email.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    initial_state = {
        "company_name": args.company_name,
        "company_url": args.company_url,
        "contact_name": args.contact_name,
        "contact_email": args.contact_email,
        "errors": [],
    }

    graph = build_graph()

    if args.no_email:
        # Run everything except the final send_email node by invoking the
        # graph up to generate_report via direct node calls, so --no-email
        # truly never touches the email API.
        from app.graph import (
            node_research,
            node_identify_opportunities,
            node_map_solutions,
            node_generate_report,
        )

        state = dict(initial_state)
        state.update(node_research(state))
        state.update(node_identify_opportunities(state))
        state.update(node_map_solutions(state))
        state.update(node_generate_report(state))
    else:
        state = graph.invoke(initial_state)

    OUTPUT_DIR.mkdir(exist_ok=True)
    safe_name = "".join(c if c.isalnum() else "_" for c in args.company_name).strip("_")
    report_path = OUTPUT_DIR / f"{safe_name}_report.md"
    report_path.write_text(state.get("report_markdown", ""))

    state_path = OUTPUT_DIR / f"{safe_name}_state.json"
    state_path.write_text(json.dumps(state, indent=2, default=str))

    print("\n=== Report ===\n")
    print(state.get("report_markdown", "(no report generated)"))

    print(f"\nSaved report to {report_path}")
    print(f"Saved full run state to {state_path}")

    if state.get("errors"):
        print("\n=== Warnings/Errors during run ===")
        for e in state["errors"]:
            print(f"- {e}")

    if not args.no_email:
        if state.get("email_sent"):
            print(f"\nEmail sent to {args.contact_email}")
        else:
            print(f"\nEmail NOT sent: {state.get('email_error')}")
            sys.exit(1)


if __name__ == "__main__":
    main()
