import os
import re

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

    if host_speaker is None or host_speaker == 0:
        return segments

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


def load_all_transcripts(data_dir: str = "data") -> Dict[str, List[Dict[str, Any]]]:
    """Return a mapping of absolute file paths to parsed segments for all .txt files."""
    return {file_path: segments for file_path, segments in iter_transcripts(data_dir)}

def collect_host_segments(data_dir: str = "data") -> List[Dict[str, Any]]:
    """Collect all segments spoken by the host (speaker 0) across all transcripts."""
    host_segments: List[Dict[str, Any]] = []
    for _, segments in iter_transcripts(data_dir):
        for seg in segments:
            if int(seg.get("speaker", -1)) == 0:
                text = str(seg.get("text", "")).strip()
                if text:
                    host_segments.append({"speaker": 0, "text": text})
    return host_segments

def batch_segments(segments: List[Dict[str, Any]], batch_size: int = 10) -> List[List[Dict[str, Any]]]:
    """Batch segments into fixed-size chunks, dropping the remainder that doesn't fill a batch."""
    if batch_size <= 0:
        raise ValueError("batch_size must be > 0")
    full_len = (len(segments) // batch_size) * batch_size
    segments = segments[:full_len]
    return [segments[i:i + batch_size] for i in range(0, len(segments), batch_size)]

def train_test_split_batches(batches: List[List[Dict[str, Any]]], train_ratio: float = 0.5) -> tuple[List[List[Dict[str, Any]]], List[List[Dict[str, Any]]]]:
    """Split batches into train and test sets by ratio (deterministic, no shuffle)."""
    if not 0.0 < train_ratio < 1.0:
        raise ValueError("train_ratio must be between 0 and 1")
    n_train = int(len(batches) * train_ratio)
    return batches[:n_train], batches[n_train:]

def build_host_batches(data_dir: str = "data", batch_size: int = 10, train_ratio: float = 0.5) -> tuple[List[List[Dict[str, Any]]], List[List[Dict[str, Any]]]]:
    """Convenience: collect host-only segments, batch them, then split into train/test."""
    segments = collect_host_segments(data_dir)
    batches = batch_segments(segments, batch_size=batch_size)
    return train_test_split_batches(batches, train_ratio=train_ratio)

if __name__ == "__main__":
    host_train, host_test = build_host_batches("data", batch_size=10, train_ratio=0.5)
    print(f"Host-only batches -> train: {len(host_train)}, test: {len(host_test)}")
    print("\n".join([segment["text"] for segment in host_train[0]]))
