"""ai_use_record.py -- which AI models and which versions of the command-line tool the session records show.

    python -B -I ai_use_record.py <session record (.jsonl)> <folder of the subagent records> <first day> <day made>

The session records of the Claude Code command-line tool are kept on the author's machine; they are private and are
not in the package, so this script cannot be re-run from the package. Its stored output (ai_use_record_<day>.txt) is
the record that the statement "Use of AI tools" of the article names. The script only reads the records: for each
line it takes the day, the model that wrote the message and the version of the tool; for each subagent record, the
day of its first line and the models that wrote in it.
"""
import collections
import json
import os
import sys

NAMES = {"claude-opus-5-5": "Claude Opus 5.5", "claude-fable-5-2": "Claude Fable 5.2", "claude-haiku-5-5": "Claude Haiku 5.5"}


def lines(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                yield json.loads(line)
            except Exception:
                continue


def main():
    session, subdir, first, made = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    models = collections.defaultdict(collections.Counter)
    versions = collections.defaultdict(collections.Counter)
    for d in lines(session):
        day = (d.get("timestamp") or "")[:10]
        if day < first:
            continue
        m = d.get("message")
        if isinstance(m, dict) and m.get("model") and m["model"] != "<synthetic>":
            models[day][m["model"]] += 1
        if d.get("version"):
            versions[day][d["version"]] += 1
    subs = collections.defaultdict(collections.Counter)
    for dp, _, fn in os.walk(subdir):
        for f in fn:
            if not f.endswith(".jsonl"):
                continue
            day, seen = None, set()
            for d in lines(os.path.join(dp, f)):
                if day is None and d.get("timestamp"):
                    day = d["timestamp"][:10]
                m = d.get("message")
                if isinstance(m, dict) and m.get("model") and m["model"] != "<synthetic>":
                    seen.add(m["model"])
            if day and day >= first:
                for s in seen:
                    subs[day][s] += 1
    all_models = set(k for c in models.values() for k in c) | set(k for c in subs.values() for k in c)
    all_versions = sorted(set(k for c in versions.values() for k in c), key=lambda v: [int(x) for x in v.split(".")])
    print("Record of the AI tools used for this work, %s to %s" % (first, made))
    print("Made on %s by ai_use_record.py from the session records of the Claude Code command-line tool on the" % made)
    print("author's machine (private; not in the package). Counts are messages written by a model (main session)")
    print("and subagent records in which a model wrote (subagents). The records of those days also hold other work")
    print("of the author with the same tools; the counts are for all of it, the lists of models and versions too.")
    print("")
    print("Models: " + "; ".join("%s (%s)" % (NAMES.get(m, m), m) for m in sorted(all_models)))
    print("Versions of the Claude Code command-line tool: " + ", ".join(all_versions)
          + " (that is, %s to %s)" % (all_versions[0], all_versions[-1]))
    print("")
    print("%-10s | %-44s | %-34s | %s" % ("day", "main session: model, messages", "tool version", "subagents: model, records"))
    for day in sorted(set(models) | set(versions) | set(subs)):
        a = ", ".join("%s %d" % (NAMES.get(k, k), v) for k, v in sorted(models[day].items()))
        b = ", ".join(sorted(versions[day], key=lambda v: [int(x) for x in v.split(".")]))
        c = ", ".join("%s %d" % (NAMES.get(k, k), v) for k, v in sorted(subs[day].items()))
        print("%-10s | %-44s | %-34s | %s" % (day, a or "-", b or "-", c or "-"))
    tot = collections.Counter()
    for c in subs.values():
        tot.update(c)
    print("")
    print("Subagent records in all: " + ", ".join("%s %d" % (NAMES.get(k, k), v) for k, v in sorted(tot.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
