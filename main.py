import argparse
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)


def cmd_scrape(args):
    from scraper.orchestrator import run_scrape
    run_scrape(
        company_type=args.type,
        company_filter=args.company,
        force=args.force,
    )


def cmd_export(args):
    from exporter.csv_export import export_all
    export_all()


def cmd_serve(args):
    import config
    from dashboard.app import create_app
    app = create_app()
    print(f"Dashboard running at http://{config.FLASK_HOST}:{config.FLASK_PORT}")
    app.run(host=config.FLASK_HOST, port=config.FLASK_PORT, debug=False)


def main():
    parser = argparse.ArgumentParser(
        prog="privacy-scraper",
        description="Scrape privacy policies for ASX 200, MNCs, and Australian Government entities.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # scrape
    p_scrape = sub.add_parser("scrape", help="Run the scraper")
    p_scrape.add_argument(
        "--type",
        choices=["ASX200", "MNC", "GOVERNMENT"],
        default=None,
        help="Limit scraping to one category",
    )
    p_scrape.add_argument(
        "--company",
        default=None,
        metavar="NAME_OR_CODE",
        help="Scrape a single company by name or ASX code (e.g. CBA)",
    )
    p_scrape.add_argument(
        "--force",
        action="store_true",
        help="Re-scrape companies that were already successfully scraped",
    )
    p_scrape.set_defaults(func=cmd_scrape)

    # export
    p_export = sub.add_parser("export", help="Export data to CSV")
    p_export.set_defaults(func=cmd_export)

    # serve
    p_serve = sub.add_parser("serve", help="Start Flask dashboard")
    p_serve.set_defaults(func=cmd_serve)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
