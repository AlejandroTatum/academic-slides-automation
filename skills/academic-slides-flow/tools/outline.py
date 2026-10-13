#!/usr/bin/env python3
"""Read an approved outline and print the talk plan: time and speaker per slide.

Outline line (one per slide):
    component | message | visual | spoken note [| speaker [| m:ss]]
A line without "|" is a legacy one-message line. Header comments:
    # duration: 10 min        (or 10, or 10:00)
    # speakers: Ana, Luis
Other "#" lines are comments.

Without a duration every slide gets 1:00. Slides without an explicit time
share what the explicit times leave. Without per-line speakers the speakers
take contiguous, even blocks; a line without a speaker keeps the previous one.

Does not modify the outline. Exit 0 with the plan, 1 with "outline:" errors,
2 for usage. "note:" lines are advice, not failures.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

COMPONENTS = Path(__file__).resolve().parent.parent / "components"
USAGE = "usage: outline.py OUTLINE"
MAX_MESSAGE_WORDS = 8
WORD = re.compile(r"\w+", re.U)


@dataclass
class Slide:
    number: int
    line: int
    component: str
    message: str
    visual: str = ""
    note: str = ""
    speaker: str = ""
    seconds: int | None = None
    start: int = 0


@dataclass
class Plan:
    title: str = ""
    duration: int | None = None
    speakers: list[str] = field(default_factory=list)
    slides: list[Slide] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return sum(slide.seconds or 0 for slide in self.slides)


def clock(seconds: int) -> str:
    return f"{seconds // 60}:{seconds % 60:02d}"


def parse_time(text: str) -> int | None:
    text = text.strip().lower()
    match = re.fullmatch(r"(\d+):([0-5]\d)", text)
    if match:
        return int(match.group(1)) * 60 + int(match.group(2))
    match = re.fullmatch(r"(\d+)\s*(min|m)?", text)
    if match:
        return int(match.group(1)) * 60
    match = re.fullmatch(r"(\d+)\s*s", text)
    if match:
        return int(match.group(1))
    return None


def parse(path: Path) -> Plan:
    plan = Plan()
    known = {p.stem for p in COMPONENTS.glob("*.html")}
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        text = raw.strip()
        if not text:
            continue
        if text.startswith("#"):
            header = re.fullmatch(r"#\s*(duration|speakers)\s*:\s*(.*)", text, re.I)
            if not header:
                if not plan.title and not plan.slides:
                    plan.title = text.lstrip("#").strip()
                continue
            key, value = header.group(1).lower(), header.group(2).strip()
            if key == "duration":
                plan.duration = parse_time(value)
                if plan.duration is None:
                    plan.errors.append(f"outline: bad duration {value}")
            else:
                plan.speakers = [name.strip() for name in value.split(",") if name.strip()]
            continue
        fields = [part.strip() for part in text.split("|")] if "|" in text else [text]
        if len(fields) not in (1, 4, 5, 6):
            plan.errors.append(f"outline: line {number} needs 1 or 4-6 fields, found {len(fields)}")
            continue
        if len(fields) == 1:
            plan.slides.append(Slide(len(plan.slides) + 1, number, "-", fields[0]))
            continue
        slide = Slide(len(plan.slides) + 1, number, *fields[:4])
        if slide.component not in known:
            plan.errors.append(f"outline: line {number} unknown component {slide.component}")
        if len(fields) >= 5 and fields[4]:
            slide.speaker = fields[4]
            if plan.speakers and slide.speaker not in plan.speakers:
                plan.errors.append(f"outline: line {number} speaker {slide.speaker} is not in # speakers")
        if len(fields) == 6 and fields[5]:
            slide.seconds = parse_time(fields[5])
            if slide.seconds is None:
                plan.errors.append(f"outline: line {number} bad time {fields[5]}")
        words = len(WORD.findall(slide.message))
        if words > MAX_MESSAGE_WORDS:
            plan.notes.append(f"note: line {number} message has {words} words (default {MAX_MESSAGE_WORDS})")
        plan.slides.append(slide)
    if not plan.errors:
        budget(plan)
    return plan


def budget(plan: Plan) -> None:
    slides = plan.slides
    if not slides:
        return
    explicit = sum(s.seconds for s in slides if s.seconds is not None)
    open_slides = [s for s in slides if s.seconds is None]
    if plan.duration is None:
        for s in open_slides:
            s.seconds = 60
    else:
        if explicit > plan.duration:
            plan.errors.append(f"outline: explicit times {clock(explicit)} exceed duration {clock(plan.duration)}")
            return
        if open_slides:
            share, extra = divmod(plan.duration - explicit, len(open_slides))
            for index, s in enumerate(open_slides):
                s.seconds = share + (1 if index < extra else 0)
        minutes = plan.duration / 60
        if len(slides) < minutes / 3 or len(slides) > minutes * 2:
            plan.notes.append(
                f"note: {len(slides)} slides for {clock(plan.duration)} (about 1 per minute suggests {round(minutes)})"
            )
    start = 0
    for s in slides:
        s.start = start
        start += s.seconds or 0
    if plan.speakers:
        if not any(s.speaker for s in slides):
            per, extra = divmod(len(slides), len(plan.speakers))
            index = 0
            for position, name in enumerate(plan.speakers):
                count = per + (1 if position < extra else 0)
                for s in slides[index:index + count]:
                    s.speaker = name
                index += count
        else:
            current = plan.speakers[0]
            for s in slides:
                current = s.speaker or current
                s.speaker = current


def render(plan: Plan) -> list[str]:
    who = [s.speaker or "-" for s in plan.slides]
    what = [s.component for s in plan.slides]
    w_who = max(map(len, who), default=1)
    w_what = max(map(len, what), default=1)
    w_start = max((len(clock(s.start)) for s in plan.slides), default=4)
    w_len = max((len(clock(s.seconds or 0)) for s in plan.slides), default=4)
    total = plan.duration if plan.duration is not None else plan.total
    people = "speaker" if len(plan.speakers) == 1 else "speakers"
    lines = [f"plan: {len(plan.slides)} slides · {clock(total)} · {len(plan.speakers)} {people}"]
    for s, name, comp in zip(plan.slides, who, what):
        lines.append(
            f"{s.number:02d}  {clock(s.start).rjust(w_start)}  {clock(s.seconds or 0).rjust(w_len)}  "
            f"{name.ljust(w_who)}  {comp.ljust(w_what)}  {s.message}"
        )
    for name in plan.speakers:
        mine = [s for s in plan.slides if s.speaker == name]
        lines.append(f"speaker: {name} {len(mine)} slides {clock(sum(s.seconds or 0 for s in mine))}")
    return lines + plan.notes


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1 or args[0].startswith("-"):
        print(USAGE, file=sys.stderr)
        return 2
    path = Path(args[0])
    if not path.is_file():
        print(USAGE, file=sys.stderr)
        return 2
    plan = parse(path)
    if plan.errors:
        sys.stdout.write("\n".join(plan.errors) + "\n")
        return 1
    sys.stdout.write("\n".join(render(plan)) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
