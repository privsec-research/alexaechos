import argparse
import csv


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("report_csv", type=str)
    parser.add_argument("policy_url_csv", type=str)
    parser.add_argument("out_csv", type=str)

    args = parser.parse_args()
    policy_urls = dict()
    publishers = dict()

    with open(args.policy_url_csv, newline="") as fin:
        for row in csv.DictReader(fin):
            policy_urls[row["asin"]] = row["privacy_policy_url"]
            publishers[row["asin"]] = row["publisher"]

    dedup = set()

    with open(args.report_csv, newline="") as fin, \
         open(args.out_csv, "w", newline="") as fout:

        writer = csv.DictWriter(fout, fieldnames=["app_id", "pii_types", "hostname", "creator",
                                                  "developer_privacy_policy", "extra_policies"])
        writer.writeheader()

        for row in csv.DictReader(fin):
            asin = row["skill_name"]
            fqdn = row["FQDN"]
            party = row["Party"]

            # Put party labels in the FQDN so the modified PoliCheck code can use them
            if party == 'First-Party':
                fqdn = fqdn + ":FIRST_PARTY"
            else:
                fqdn = fqdn + ":THIRD_PARTY"

            if (asin, fqdn) in dedup:
                continue
            else:
                dedup.add((asin, fqdn))

            flow = {
                "app_id": asin,
                "pii_types": "encrypted_data",
                "hostname": fqdn,
                "creator": publishers.get(asin, ""),
                "developer_privacy_policy": policy_urls.get(asin, ""),
                "extra_policies": "",
            }

            writer.writerow(flow)


if __name__ == '__main__':
    main()
