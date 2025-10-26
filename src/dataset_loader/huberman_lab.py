import os
import re
import random

from typing import Any, Dict, Iterator, List, Tuple


# Example expected header formats:
#  "0 (12m 3s):"
#  "1 (1h 25m 6s):"
# Non-integer speaker labels (e.g., "Joovv (1h 26m 28s):") are treated as ads and skipped
_HEADER_LINE_REGEX = re.compile(r"^\s*(?P<speaker>.+?)\s*\((?P<timestamp>[^)]*?)\):\s*$")


def parse_transcript_text(text: str) -> List[Dict[str, Any]]:
    """
    Parse a transcript string into a list of segments with integer speakers.

    Each segment is introduced by a header line formatted like:
      "<speaker> (<timestamp>):"
    - <speaker> must be an integer (e.g., 0, 1). Non-integers (ads) are ignored.
    - Text lines following the header (until the next header) are grouped as the segment text.

    Returns: List[{"speaker": int, "text": str}]
    """
    segments: List[Dict[str, Any]] = []
    current_speaker: int | None = None
    current_text_lines: List[str] = []
    current_is_valid: bool = False

    def flush_current_segment() -> None:
        nonlocal current_speaker, current_text_lines, current_is_valid
        if current_is_valid and current_speaker is not None:
            segment_text = " ".join(line.strip() for line in current_text_lines if line.strip() != "").strip()
            if segment_text:
                segments.append({"speaker": int(current_speaker), "text": segment_text})
        current_speaker = None
        current_text_lines = []
        current_is_valid = False

    for line in text.splitlines():
        header_match = _HEADER_LINE_REGEX.match(line)
        if header_match:
            flush_current_segment()
            speaker_label = header_match.group("speaker").strip()
            try:
                current_speaker = int(speaker_label)
                current_is_valid = True
            except ValueError:
                # Non-integer speaker (likely ad/sponsor); skip until next header
                current_speaker = None
                current_is_valid = False
            continue

        if current_is_valid:
            current_text_lines.append(line)

    flush_current_segment()
    return segments


def normalize_speakers(segments: List[Dict[str, Any]], host_phrase: str = "Welcome to the Huberman Lab podcast") -> List[Dict[str, Any]]:
    """Remap speaker ids so that the host (who says the host_phrase) is speaker 0.

    - If the host phrase is not found, the segments are returned unchanged.
    - Other speakers are assigned increasing ids starting from 1, preserving first-seen order.
    """
    if not segments:
        return segments

    host_phrase_cf = host_phrase.casefold()
    host_speaker: int | None = None
    for seg in segments:
        text_cf = str(seg.get("text", "")).casefold()
        if host_phrase_cf in text_cf:
            host_speaker = int(seg.get("speaker"))
            break

    if host_speaker is None:
        raise ValueError("Host phrase not found in any segment")

    if host_speaker == 0:
        return segments # already normalized

    # Build stable order of speakers as they appear
    seen: set[int] = set()
    order: List[int] = []
    for seg in segments:
        spk = int(seg.get("speaker"))
        if spk not in seen:
            seen.add(spk)
            order.append(spk)

    # Create remapping: host -> 0, others -> 1..N in first-seen order
    mapping: Dict[int, int] = {host_speaker: 0}
    next_id = 1
    for spk in order:
        if spk == host_speaker:
            continue
        mapping[spk] = next_id
        next_id += 1

    return [{"speaker": mapping[int(seg["speaker"])], "text": seg["text"]} for seg in segments]


def load_transcript_file(file_path: str) -> List[Dict[str, Any]]:
    """Load a single .txt transcript file and parse it into segments."""
    with open(file_path, "r") as f:
        content = f.read()
    parsed = parse_transcript_text(content)
    return normalize_speakers(parsed)


def iter_transcripts(data_dir: str = "data") -> Iterator[Tuple[str, List[Dict[str, Any]]]]:
    """Yield (absolute_path, segments) for each .txt file in the data directory."""
    if not os.path.isdir(data_dir):
        return
    for name in sorted(os.listdir(data_dir)):
        if not name.lower().endswith(".txt"):
            continue
        abs_path = os.path.join(data_dir, name)
        try:
            yield abs_path, load_transcript_file(abs_path)
        except Exception:
            # Skip unreadable/problematic files
            continue


def collect_segments_per_file(data_dir: str = "data") -> Dict[str, List[str]]:
    """Collect all segments spoken by the host (speaker 0) per file."""

    output: Dict[str, List[str]] = {} # file_path -> list of text segments

    for file_path, segments in iter_transcripts(data_dir):
        output[file_path] = []

        for seg in segments:
            if int(seg.get("speaker", -1)) == 0 and seg.get("text") is not None:
                output[file_path].append(seg.get("text"))

    return output

def batch_segments_by_words(segments: List[str], max_words_per_batch: int = 2000) -> List[List[str]]:
    """Batch segments greedily by total word budget per batch."""
    if max_words_per_batch <= 0:
        raise ValueError("max_words_per_batch must be > 0")

    batches: List[List[str]] = []
    current_batch: List[str] = []
    current_words = 0

    for segment in segments:
        seg_words = len(segment.split())

        if current_batch and current_words + seg_words > max_words_per_batch:
            batches.append(current_batch)
            current_batch = []
            current_words = 0

        current_batch.append(segment)
        current_words += seg_words

        if current_words >= max_words_per_batch:
            batches.append(current_batch)
            current_batch = []
            current_words = 0

    if current_batch:
        batches.append(current_batch)

    return batches

def train_test_split_batches(batches: List[List[str]], train_ratio: float = 0.5) -> tuple[List[List[str]], List[List[str]]]:
    """Split batches into train and test sets by ratio (deterministic, no shuffle)."""
    if not 0.0 < train_ratio < 1.0:
        raise ValueError(f"train_ratio must be between 0 and 1: {train_ratio}")
    n_train = int(len(batches) * train_ratio)
    return batches[:n_train], batches[n_train:]

def load_dataset(
    data_dir: str,
    max_words_per_batch: int = 2000,
    train_ratio: float = 0.5,
    val_ratio: float = 0.2,
) -> tuple[List[List[str]], List[List[str]], List[List[str]]]:
    """Convenience: collect host-only segments, batch them, then split into train/test."""

    if not os.path.isdir(data_dir) or not os.listdir(data_dir):
        raise ValueError(f"data_dir does not exist or is empty: {data_dir}")

    segments_per_file = collect_segments_per_file(data_dir)

    nb_file_validation = int(len(segments_per_file) * val_ratio)

    flatten_segments = [segment for file_segments in list(segments_per_file.values())[:-nb_file_validation] for segment in file_segments]
    batches = batch_segments_by_words(flatten_segments, max_words_per_batch=max_words_per_batch)
    random.shuffle(batches) # NOTE: we're shuffling per batch instead of per-sample to keep a "logic" between samples within a same batch

    train_set, test_set = train_test_split_batches(batches, train_ratio=train_ratio)

    flatten_segments_validation_set = [segment for file_segments in list(segments_per_file.values())[-nb_file_validation:] for segment in file_segments]
    validation_set = batch_segments_by_words(flatten_segments_validation_set, max_words_per_batch=max_words_per_batch)

    if len(train_set) == 0:
        raise ValueError("train_set is empty")

    if len(test_set) == 0:
        raise ValueError("test_set is empty")

    if len(validation_set) == 0:
        raise ValueError("validation_set is empty")

    print("Number of words in train set: ", sum(len(segment.split()) for batch in train_set for segment in batch))
    print("Number of words in test set: ", sum(len(segment.split()) for batch in test_set for segment in batch))
    print("Number of words in validation set: ", sum(len(segment.split()) for batch in validation_set for segment in batch))

    return train_set, test_set, validation_set

if __name__ == "__main__":
    host_train, host_test = load_dataset("data", max_words_per_batch=2000, train_ratio=0.5)
    print(f"Host-only batches -> train: {len(host_train)}, test: {len(host_test)}")
    print("\n".join([segment["text"] for segment in host_train[0]]))
