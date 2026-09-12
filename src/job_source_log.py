import json


SOURCES = [
    ("Himalayas", "data/output/jobs.json"),
    ("Remote First Jobs", "data/output/jobs_remote_first.json"),
    ("Jobicy", "data/output/jobs_jobicy.json"),
    ("Arbeitnow", "data/output/jobs_arbeitnow.json"),
    ("RemNavi", "data/output/jobs_remnavi.json"),
]

FINAL_FILE = "data/output/jobs_final.json"
OUTPUT_FILE = "data/output/job_source_log.json"


def main():
    with open(FINAL_FILE, "r", encoding="utf-8") as file:
        final_jobs = json.load(file)

    final_urls = {
        job.get("source_url", "").split("?")[0]
        for job in final_jobs
    }

    source_log = []

    for source_name, filename in SOURCES:
        with open(filename, "r", encoding="utf-8") as file:
            jobs = json.load(file)

        unique_count = 0

        for job in jobs:
            url = job.get("source_url", "").split("?")[0]

            if url in final_urls:
                unique_count += 1

        source_log.append({
            "source": source_name,
            "fresh_jobs_collected": len(jobs),
            "jobs_in_final_dataset": unique_count,
            "source_monitored": True
        })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(
            source_log,
            file,
            indent=2,
            ensure_ascii=False
        )

    print("Job source monitoring log:")
    print()

    for source in source_log:
        print(
            source["source"],
            "->",
            source["fresh_jobs_collected"],
            "collected,",
            source["jobs_in_final_dataset"],
            "in final dataset"
        )

    print()
    print("Saved:", OUTPUT_FILE)


if __name__ == "__main__":
    main()